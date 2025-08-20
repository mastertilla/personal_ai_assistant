import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import Base, DatabaseManager


class TestBase:
    """Test cases for the Base model class"""

    def test_base_class_exists(self):
        """Test that Base class is properly defined"""
        assert Base is not None
        assert hasattr(Base, "__tablename__")

    def test_base_inheritance(self):
        """Test that Base inherits from DeclarativeBase"""
        from sqlalchemy.orm import DeclarativeBase

        assert issubclass(Base, DeclarativeBase)


class TestDatabaseManager:
    """Test cases for the DatabaseManager class"""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing"""
        settings = MagicMock()
        settings.database_url = "postgresql+asyncpg://test:test@localhost/test"
        settings.database_pool_size = 10
        settings.database_max_overflow = 5
        settings.debug = False
        return settings

    @pytest.fixture
    def db_manager(self, mock_settings):
        """Create a DatabaseManager instance with mocked settings"""
        with patch("app.core.database.get_settings", return_value=mock_settings):
            return DatabaseManager()

    def test_init(self, mock_settings):
        """Test DatabaseManager initialization"""
        with patch(
            "app.core.database.get_settings", return_value=mock_settings
        ) as mock_get_settings:
            manager = DatabaseManager()

            mock_get_settings.assert_called_once()
            assert manager.settings == mock_settings
            assert manager._engine is None
            assert manager._session_factory is None

    @pytest.mark.asyncio
    async def test_initialize_first_time(self, db_manager, mock_settings):
        """Test database initialization when engine doesn't exist"""
        with (
            patch("app.core.database.create_async_engine") as mock_create_engine,
            patch("app.core.database.async_sessionmaker") as mock_sessionmaker,
            patch("app.core.database.event") as mock_event,
        ):
            mock_engine = AsyncMock()
            mock_engine.sync_engine = MagicMock()
            mock_create_engine.return_value = mock_engine
            mock_session_factory = MagicMock()
            mock_sessionmaker.return_value = mock_session_factory

            await db_manager.initialize()

            mock_create_engine.assert_called_once_with(
                mock_settings.database_url,
                pool_size=mock_settings.database_pool_size,
                max_overflow=mock_settings.database_max_overflow,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=mock_settings.debug,
            )

            mock_sessionmaker.assert_called_once_with(
                bind=mock_engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False,
            )

            assert db_manager._engine == mock_engine
            assert db_manager._session_factory == mock_session_factory

            # Verify event listeners were added
            assert mock_event.listens_for.call_count == 2

    @pytest.mark.asyncio
    async def test_initialize_already_initialized(self, db_manager):
        """Test that initialize doesn't reinitialize if engine already exists"""
        db_manager._engine = MagicMock()

        with patch("app.core.database.create_async_engine") as mock_create_engine:
            await db_manager.initialize()

            mock_create_engine.assert_not_called()

    @pytest.mark.asyncio
    async def test_close_with_engine(self, db_manager):
        """Test closing database connections when engine exists"""
        mock_engine = AsyncMock()
        db_manager._engine = mock_engine

        with patch("app.core.database.logger") as mock_logger:
            await db_manager.close()

            mock_engine.dispose.assert_called_once()
            mock_logger.info.assert_called_with("Database connections closed")

    @pytest.mark.asyncio
    async def test_close_without_engine(self, db_manager):
        """Test closing when no engine exists"""
        db_manager._engine = None

        with patch("app.core.database.logger") as mock_logger:
            await db_manager.close()

            mock_logger.info.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_session_success(self, db_manager):
        """Test successful session creation and commit"""
        mock_session = AsyncMock()
        mock_session_factory = MagicMock()
        mock_session_factory.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        mock_session_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        db_manager._session_factory = mock_session_factory

        async with db_manager.get_session() as session:
            assert session == mock_session

        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        mock_session.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_session_with_exception(self, db_manager):
        """Test session rollback when exception occurs"""
        mock_session = AsyncMock()
        mock_session.commit.side_effect = Exception("Test error")

        mock_session_factory = MagicMock()
        mock_session_factory.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        mock_session_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        db_manager._session_factory = mock_session_factory

        with pytest.raises(Exception, match="Test error"):
            async with db_manager.get_session() as session:
                await session.commit()  # This will raise the exception

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_session_not_initialized(self, db_manager):
        """Test get_session raises error when not initialized"""
        db_manager._session_factory = None

        with pytest.raises(RuntimeError, match="Database not initialized"):
            async with db_manager.get_session():
                pass

    @pytest.mark.asyncio
    async def test_health_check_success(self, db_manager):
        """Test successful health check"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1
        mock_session.execute.return_value = mock_result

        mock_session_factory = MagicMock()
        mock_session_factory.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        mock_session_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        db_manager._session_factory = mock_session_factory

        result = await db_manager.health_check()

        assert result is True
        mock_session.execute.assert_called_once_with("SELECT 1")

    @pytest.mark.asyncio
    async def test_health_check_failure(self, db_manager):
        """Test health check failure"""
        mock_session = AsyncMock()
        mock_session.execute.side_effect = SQLAlchemyError("Connection failed")

        mock_session_factory = MagicMock()
        mock_session_factory.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        mock_session_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        db_manager._session_factory = mock_session_factory

        with patch("app.core.database.logger") as mock_logger:
            result = await db_manager.health_check()

            assert result is False
            mock_logger.error.assert_called_once()
            error_call = mock_logger.error.call_args[0][0]
            assert "Database health check failed" in error_call

    @pytest.mark.asyncio
    async def test_health_check_wrong_result(self, db_manager):
        """Test health check when query returns wrong result"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0  # Wrong result
        mock_session.execute.return_value = mock_result

        mock_session_factory = MagicMock()
        mock_session_factory.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        mock_session_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        db_manager._session_factory = mock_session_factory

        result = await db_manager.health_check()

        assert result is False

    def test_connection_event_handlers(self, db_manager, mock_settings, caplog):
        """Test that connection event handlers work properly"""
        with (
            patch("app.core.database.create_async_engine") as mock_create_engine,
            patch("app.core.database.async_sessionmaker"),
        ):
            mock_engine = AsyncMock()
            mock_sync_engine = MagicMock()
            mock_engine.sync_engine = mock_sync_engine
            mock_create_engine.return_value = mock_engine

            # Capture the event handlers
            connect_handler = None
            disconnect_handler = None

            def mock_listens_for(target, event_name):
                def decorator(func):
                    nonlocal connect_handler, disconnect_handler
                    if event_name == "connect":
                        connect_handler = func
                    elif event_name == "disconnect":
                        disconnect_handler = func
                    return func

                return decorator

            with patch("app.core.database.event") as mock_event:
                mock_event.listens_for.side_effect = mock_listens_for

                # Run initialization to register handlers
                import asyncio

                asyncio.run(db_manager.initialize())

                # Test connect handler
                with caplog.at_level(logging.INFO):
                    connect_handler(None, None)
                    assert "Database connection established" in caplog.text

                # Test disconnect handler
                caplog.clear()
                with caplog.at_level(logging.INFO):
                    disconnect_handler(None, None)
                    assert "Database connection closed" in caplog.text

    @pytest.mark.asyncio
    async def test_integration_initialize_and_close(self, mock_settings):
        """Test full lifecycle of database manager"""
        with (
            patch("app.core.database.get_settings", return_value=mock_settings),
            patch("app.core.database.create_async_engine") as mock_create_engine,
            patch("app.core.database.async_sessionmaker") as mock_sessionmaker,
            patch("app.core.database.event"),
        ):
            mock_engine = AsyncMock()
            mock_create_engine.return_value = mock_engine
            mock_sessionmaker.return_value = MagicMock()

            manager = DatabaseManager()

            # Initialize
            await manager.initialize()
            assert manager._engine == mock_engine
            assert manager._session_factory is not None

            # Close
            await manager.close()
            mock_engine.dispose.assert_called_once()
