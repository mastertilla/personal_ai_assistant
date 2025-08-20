import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import redis.exceptions

from app.core.redis import RedisManager


class TestRedisManager:
    """Test cases for the RedisManager class"""

    @pytest.fixture
    def redis_manager(self):
        """Create a RedisManager instance for testing"""
        return RedisManager()

    @pytest.fixture
    def mock_redis_settings(self):
        """Mock Redis settings"""
        return MagicMock(redis_url="redis://localhost:6379/0", redis_max_connections=20)

    @pytest.mark.asyncio
    async def test_init(self, redis_manager):
        """Test RedisManager initialization"""
        assert redis_manager._pool is None
        assert redis_manager._redis is None

    @pytest.mark.asyncio
    async def test_initialize_first_time(self, redis_manager):
        """Test Redis initialization when pool doesn't exist"""
        mock_pool = AsyncMock()
        mock_redis = AsyncMock()

        with (
            patch("app.core.redis.ConnectionPool") as mock_connection_pool,
            patch("app.core.redis.redis.Redis") as mock_redis_class,
            patch("app.core.redis.REDIS_SETTINGS") as mock_settings,
        ):
            mock_settings.redis_url = "redis://localhost:6379/0"
            mock_settings.redis_max_connections = 20
            mock_connection_pool.from_url.return_value = mock_pool
            mock_redis_class.return_value = mock_redis

            await redis_manager.initialize()

            mock_connection_pool.from_url.assert_called_once_with(
                "redis://localhost:6379/0",
                max_connections=20,
                retry_on_timeout=True,
                health_check_interval=30,
            )

            mock_redis_class.assert_called_once_with(connection_pool=mock_pool)
            mock_redis.ping.assert_called_once()

            assert redis_manager._pool == mock_pool
            assert redis_manager._redis == mock_redis

    @pytest.mark.asyncio
    async def test_initialize_already_initialized(self, redis_manager):
        """Test that initialize doesn't reinitialize if pool already exists"""
        redis_manager._pool = MagicMock()

        with patch("app.core.redis.ConnectionPool") as mock_connection_pool:
            await redis_manager.initialize()

            mock_connection_pool.from_url.assert_not_called()

    @pytest.mark.asyncio
    async def test_initialize_connection_failure(self, redis_manager):
        """Test initialization failure handling"""
        mock_pool = AsyncMock()
        mock_redis = AsyncMock()
        mock_redis.ping.side_effect = redis.exceptions.ConnectionError(
            "Connection failed"
        )

        with (
            patch("app.core.redis.ConnectionPool") as mock_connection_pool,
            patch("app.core.redis.redis.Redis") as mock_redis_class,
            patch("app.core.redis.REDIS_SETTINGS") as mock_settings,
            patch("app.core.redis.logger") as mock_logger,
        ):
            mock_settings.redis_url = "redis://localhost:6379/0"
            mock_settings.redis_max_connections = 20
            mock_connection_pool.from_url.return_value = mock_pool
            mock_redis_class.return_value = mock_redis

            with pytest.raises(redis.exceptions.ConnectionError):
                await redis_manager.initialize()

            mock_logger.error.assert_called_once()
            error_call = mock_logger.error.call_args[0][0]
            assert "Failed to initialize Redis" in error_call

    @pytest.mark.asyncio
    async def test_close_with_connections(self, redis_manager):
        """Test closing Redis connections when they exist"""
        mock_redis = AsyncMock()
        mock_pool = AsyncMock()
        redis_manager._redis = mock_redis
        redis_manager._pool = mock_pool

        with patch("app.core.redis.logger") as mock_logger:
            await redis_manager.close()

            mock_redis.close.assert_called_once()
            mock_pool.disconnect.assert_called_once()
            mock_logger.info.assert_called_with("Redis connections closed")

    @pytest.mark.asyncio
    async def test_close_without_connections(self, redis_manager):
        """Test closing when no connections exist"""
        redis_manager._redis = None
        redis_manager._pool = None

        with patch("app.core.redis.logger") as mock_logger:
            await redis_manager.close()

            mock_logger.info.assert_called_with("Redis connections closed")

    @pytest.mark.asyncio
    async def test_get_success(self, redis_manager):
        """Test successful GET operation"""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = b"test_value"
        redis_manager._redis = mock_redis

        result = await redis_manager.get("test_key")

        assert result == "test_value"
        mock_redis.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_none_value(self, redis_manager):
        """Test GET operation when value doesn't exist"""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None
        redis_manager._redis = mock_redis

        result = await redis_manager.get("test_key")

        assert result is None
        mock_redis.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_exception(self, redis_manager):
        """Test GET operation exception handling"""
        mock_redis = AsyncMock()
        mock_redis.get.side_effect = redis.exceptions.ConnectionError(
            "Connection failed"
        )
        redis_manager._redis = mock_redis

        with patch("app.core.redis.logger") as mock_logger:
            result = await redis_manager.get("test_key")

            assert result is None
            mock_logger.error.assert_called_once()
            error_call = mock_logger.error.call_args[0][0]
            assert "Redis GET error for key test_key" in error_call

    @pytest.mark.asyncio
    async def test_set_success(self, redis_manager):
        """Test successful SET operation"""
        mock_redis = AsyncMock()
        mock_redis.set.return_value = True
        redis_manager._redis = mock_redis

        result = await redis_manager.set("test_key", "test_value")

        assert result is True
        mock_redis.set.assert_called_once_with("test_key", "test_value", ex=None)

    @pytest.mark.asyncio
    async def test_set_with_ttl(self, redis_manager):
        """Test SET operation with TTL"""
        mock_redis = AsyncMock()
        mock_redis.set.return_value = True
        redis_manager._redis = mock_redis

        result = await redis_manager.set("test_key", "test_value", ttl=300)

        assert result is True
        mock_redis.set.assert_called_once_with("test_key", "test_value", ex=300)

    @pytest.mark.asyncio
    async def test_set_exception(self, redis_manager):
        """Test SET operation exception handling"""
        mock_redis = AsyncMock()
        mock_redis.set.side_effect = redis.exceptions.ConnectionError(
            "Connection failed"
        )
        redis_manager._redis = mock_redis

        with patch("app.core.redis.logger") as mock_logger:
            result = await redis_manager.set("test_key", "test_value")

            assert result is False
            mock_logger.error.assert_called_once()
            error_call = mock_logger.error.call_args[0][0]
            assert "Redis SET error for key test_key" in error_call

    @pytest.mark.asyncio
    async def test_delete_success(self, redis_manager):
        """Test successful DELETE operation"""
        mock_redis = AsyncMock()
        mock_redis.delete.return_value = 1
        redis_manager._redis = mock_redis

        result = await redis_manager.delete("test_key")

        assert result is True
        mock_redis.delete.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_delete_key_not_found(self, redis_manager):
        """Test DELETE operation when key doesn't exist"""
        mock_redis = AsyncMock()
        mock_redis.delete.return_value = 0
        redis_manager._redis = mock_redis

        result = await redis_manager.delete("test_key")

        assert result is False
        mock_redis.delete.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_delete_exception(self, redis_manager):
        """Test DELETE operation exception handling"""
        mock_redis = AsyncMock()
        mock_redis.delete.side_effect = redis.exceptions.ConnectionError(
            "Connection failed"
        )
        redis_manager._redis = mock_redis

        with patch("app.core.redis.logger") as mock_logger:
            result = await redis_manager.delete("test_key")

            assert result is False
            mock_logger.error.assert_called_once()
            error_call = mock_logger.error.call_args[0][0]
            assert "Redis DELETE error for key test_key" in error_call

    @pytest.mark.asyncio
    async def test_exists_true(self, redis_manager):
        """Test EXISTS operation when key exists"""
        mock_redis = AsyncMock()
        mock_redis.exists.return_value = 1
        redis_manager._redis = mock_redis

        result = await redis_manager.exists("test_key")

        assert result is True
        mock_redis.exists.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_exists_false(self, redis_manager):
        """Test EXISTS operation when key doesn't exist"""
        mock_redis = AsyncMock()
        mock_redis.exists.return_value = 0
        redis_manager._redis = mock_redis

        result = await redis_manager.exists("test_key")

        assert result is False
        mock_redis.exists.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_exists_exception(self, redis_manager):
        """Test EXISTS operation exception handling"""
        mock_redis = AsyncMock()
        mock_redis.exists.side_effect = redis.exceptions.ConnectionError(
            "Connection failed"
        )
        redis_manager._redis = mock_redis

        with patch("app.core.redis.logger") as mock_logger:
            result = await redis_manager.exists("test_key")

            assert result is False
            mock_logger.error.assert_called_once()
            error_call = mock_logger.error.call_args[0][0]
            assert "Redis EXISTS error for key test_key" in error_call

    @pytest.mark.asyncio
    async def test_set_json_success(self, redis_manager):
        """Test successful SET_JSON operation"""
        test_data = {"key": "value", "number": 42}

        with patch.object(redis_manager, "set", return_value=True) as mock_set:
            result = await redis_manager.set_json("test_key", test_data)

            assert result is True
            expected_json = json.dumps(test_data)
            mock_set.assert_called_once_with("test_key", expected_json, None)

    @pytest.mark.asyncio
    async def test_set_json_with_ttl(self, redis_manager):
        """Test SET_JSON operation with TTL"""
        test_data = {"key": "value"}

        with patch.object(redis_manager, "set", return_value=True) as mock_set:
            result = await redis_manager.set_json("test_key", test_data, ttl=300)

            assert result is True
            expected_json = json.dumps(test_data)
            mock_set.assert_called_once_with("test_key", expected_json, 300)

    @pytest.mark.asyncio
    async def test_set_json_serialization_error(self, redis_manager):
        """Test SET_JSON operation with non-serializable data"""

        class NonSerializable:
            pass

        test_data = NonSerializable()

        with patch("app.core.redis.logger") as mock_logger:
            result = await redis_manager.set_json("test_key", test_data)

            assert result is False
            mock_logger.error.assert_called_once()
            error_call = mock_logger.error.call_args[0][0]
            assert "Redis SET_JSON error for key test_key" in error_call

    @pytest.mark.asyncio
    async def test_get_json_success(self, redis_manager):
        """Test successful GET_JSON operation"""
        test_data = {"key": "value", "number": 42}
        json_string = json.dumps(test_data)

        with patch.object(redis_manager, "get", return_value=json_string):
            result = await redis_manager.get_json("test_key")

            assert result == test_data

    @pytest.mark.asyncio
    async def test_get_json_none_value(self, redis_manager):
        """Test GET_JSON operation when value doesn't exist"""
        with patch.object(redis_manager, "get", return_value=None):
            result = await redis_manager.get_json("test_key")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_json_invalid_json(self, redis_manager):
        """Test GET_JSON operation with invalid JSON"""
        with (
            patch.object(redis_manager, "get", return_value="invalid json"),
            patch("app.core.redis.logger") as mock_logger,
        ):
            result = await redis_manager.get_json("test_key")

            assert result is None
            mock_logger.error.assert_called_once()
            error_call = mock_logger.error.call_args[0][0]
            assert "Redis GET_JSON error for key test_key" in error_call

    @pytest.mark.asyncio
    async def test_health_check_success(self, redis_manager):
        """Test successful health check"""
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        redis_manager._redis = mock_redis

        result = await redis_manager.health_check()

        assert result is True
        mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_failure(self, redis_manager):
        """Test health check failure"""
        mock_redis = AsyncMock()
        mock_redis.ping.side_effect = redis.exceptions.ConnectionError(
            "Connection failed"
        )
        redis_manager._redis = mock_redis

        with patch("app.core.redis.logger") as mock_logger:
            result = await redis_manager.health_check()

            assert result is False
            mock_logger.error.assert_called_once()
            error_call = mock_logger.error.call_args[0][0]
            assert "Redis health check failed" in error_call

    @pytest.mark.asyncio
    async def test_health_check_wrong_response(self, redis_manager):
        """Test health check with unexpected response"""
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = "PONG"  # String instead of True
        redis_manager._redis = mock_redis

        result = await redis_manager.health_check()

        assert result is False

    @pytest.mark.asyncio
    async def test_integration_full_lifecycle(self):
        """Test full lifecycle of Redis manager"""
        mock_pool = AsyncMock()
        mock_redis = AsyncMock()

        with (
            patch("app.core.redis.ConnectionPool") as mock_connection_pool,
            patch("app.core.redis.redis.Redis") as mock_redis_class,
            patch("app.core.redis.REDIS_SETTINGS") as mock_settings,
        ):
            mock_settings.redis_url = "redis://localhost:6379/0"
            mock_settings.redis_max_connections = 20
            mock_connection_pool.from_url.return_value = mock_pool
            mock_redis_class.return_value = mock_redis

            manager = RedisManager()

            # Initialize
            await manager.initialize()
            assert manager._pool == mock_pool
            assert manager._redis == mock_redis
            mock_redis.ping.assert_called_once()

            # Use operations
            mock_redis.get.return_value = b"test_value"
            result = await manager.get("test_key")
            assert result == "test_value"

            mock_redis.set.return_value = True
            result = await manager.set("test_key", "new_value")
            assert result is True

            # Health check
            mock_redis.ping.return_value = True
            result = await manager.health_check()
            assert result is True

            # Close
            await manager.close()
            mock_redis.close.assert_called_once()
            mock_pool.disconnect.assert_called_once()


class TestRedisManagerGlobalInstance:
    """Test the global redis_manager instance"""

    def test_global_instance_exists(self):
        """Test that global redis_manager instance exists"""
        from app.core.redis import redis_manager

        assert redis_manager is not None
        assert isinstance(redis_manager, RedisManager)
        assert redis_manager._pool is None
        assert redis_manager._redis is None
