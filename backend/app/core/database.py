import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import DATABASE_SETTINGS

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base model class with common attributes"""

    pass


class DatabaseManager:
    """Production-ready database manager with connection pooling"""

    def __init__(self):
        self._engine = None
        self._session_factory = None

    async def initialize(self):
        """Initialize database connection with proper pooling"""
        if self._engine is not None:
            return

        # Create engine with connection pooling
        self._engine = create_async_engine(
            DATABASE_SETTINGS.database_url,
            pool_size=DATABASE_SETTINGS.database_pool_size,
            max_overflow=DATABASE_SETTINGS.database_max_overflow,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,  # Recycle connections every hour
            echo=DATABASE_SETTINGS.debug,  # Log SQL in debug mode
        )

        # Add connection event listeners for monitoring
        @event.listens_for(self._engine.sync_engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            logger.info("Database connection established")

        @event.listens_for(self._engine.sync_engine, "disconnect")
        def receive_disconnect(dbapi_connection, connection_record):
            logger.info("Database connection closed")

        # Create session factory
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

        logger.info("Database initialized successfully")

    async def close(self):
        """Clean shutdown of database connections"""
        if self._engine:
            await self._engine.dispose()
            logger.info("Database connections closed")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session with automatic cleanup"""
        if not self._session_factory:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def health_check(self) -> bool:
        """Health check for database connectivity"""
        try:
            async with self.get_session() as session:
                result = await session.execute("SELECT 1")
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


async def get_db(db_manager: DatabaseManager) -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions"""
    async with db_manager.get_session() as session:
        yield session
