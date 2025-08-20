from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.security import SecurityManager, pwd_context, security


class TestSecurityManager:
    """Test cases for the SecurityManager class"""

    @pytest.fixture
    def security_manager(self):
        """Create a SecurityManager instance for testing"""
        return SecurityManager()

    @pytest.fixture
    def mock_project_settings(self):
        """Mock project settings"""
        return MagicMock(
            secret_key="test_secret_key_that_is_long_enough_for_validation_purposes",
            algorithm="HS256",
            access_token_expire_minutes=30,
        )

    def test_init(self, security_manager):
        """Test SecurityManager initialization"""
        assert isinstance(security_manager, SecurityManager)

    def test_verify_password_success(self, security_manager):
        """Test successful password verification"""
        plain_password = "test_password"
        hashed_password = pwd_context.hash(plain_password)

        result = security_manager.verify_password(plain_password, hashed_password)

        assert result is True

    def test_verify_password_failure(self, security_manager):
        """Test password verification failure"""
        plain_password = "test_password"
        wrong_password = "wrong_password"
        hashed_password = pwd_context.hash(plain_password)

        result = security_manager.verify_password(wrong_password, hashed_password)

        assert result is False

    def test_verify_password_exception_handling(self, security_manager):
        """Test password verification exception handling"""
        with (
            patch("app.core.security.pwd_context.verify") as mock_verify,
            patch("app.core.security.logger") as mock_logger,
        ):
            mock_verify.side_effect = Exception("Verification error")

            result = security_manager.verify_password("password", "hash")

            assert result is False
            mock_logger.error.assert_called_once()
            error_call = mock_logger.error.call_args[0][0]
            assert "Password verification error" in error_call

    def test_get_password_hash(self, security_manager):
        """Test password hashing"""
        password = "test_password"

        hashed = security_manager.get_password_hash(password)

        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 0

        # Verify the hash can be used for verification
        assert pwd_context.verify(password, hashed)

    def test_create_access_token_default_expiry(self, security_manager):
        """Test JWT token creation with default expiry"""
        test_data = {"sub": "user123", "email": "test@example.com"}

        with (
            patch("app.core.security.PROJECT_SETTINGS") as mock_settings,
            patch("app.core.security.datetime") as mock_datetime,
        ):
            mock_settings.secret_key = (
                "test_secret_key_that_is_long_enough_for_validation"
            )
            mock_settings.algorithm = "HS256"
            mock_settings.access_token_expire_minutes = 30

            # Mock datetime to control token creation time
            mock_now = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.utcnow.return_value = mock_now

            token = security_manager.create_access_token(test_data)

            # Decode token to verify contents
            decoded = jwt.decode(
                token, mock_settings.secret_key, algorithms=[mock_settings.algorithm]
            )

            assert decoded["sub"] == "user123"
            assert decoded["email"] == "test@example.com"
            assert "exp" in decoded
            assert "iat" in decoded

    def test_create_access_token_custom_expiry(self, security_manager):
        """Test JWT token creation with custom expiry"""
        test_data = {"sub": "user123"}
        custom_delta = timedelta(hours=2)

        with (
            patch("app.core.security.PROJECT_SETTINGS") as mock_settings,
            patch("app.core.security.datetime") as mock_datetime,
        ):
            mock_settings.secret_key = (
                "test_secret_key_that_is_long_enough_for_validation"
            )
            mock_settings.algorithm = "HS256"

            mock_now = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.utcnow.return_value = mock_now

            token = security_manager.create_access_token(test_data, custom_delta)

            decoded = jwt.decode(
                token, mock_settings.secret_key, algorithms=[mock_settings.algorithm]
            )

            expected_exp = mock_now + custom_delta
            assert decoded["exp"] == expected_exp.timestamp()

    def test_create_access_token_exception(self, security_manager):
        """Test JWT token creation exception handling"""
        test_data = {"sub": "user123"}

        with (
            patch("app.core.security.jwt.encode") as mock_encode,
            patch("app.core.security.logger") as mock_logger,
        ):
            mock_encode.side_effect = Exception("Encoding error")

            with pytest.raises(HTTPException) as exc_info:
                security_manager.create_access_token(test_data)

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert exc_info.value.detail == "Could not create access token"
            mock_logger.error.assert_called_once()

    def test_verify_token_success(self, security_manager):
        """Test successful token verification"""
        test_payload = {
            "sub": "user123",
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
        }

        with (
            patch("app.core.security.PROJECT_SETTINGS") as mock_settings,
            patch("app.core.security.jwt.decode") as mock_decode,
        ):
            mock_settings.secret_key = "test_secret"
            mock_settings.algorithm = "HS256"
            mock_decode.return_value = test_payload

            result = security_manager.verify_token("test_token")

            assert result == test_payload
            mock_decode.assert_called_once_with(
                "test_token", "test_secret", algorithms=["HS256"]
            )

    def test_verify_token_expired(self, security_manager):
        """Test token verification with expired token"""
        expired_payload = {
            "sub": "user123",
            "exp": (datetime.utcnow() - timedelta(hours=1)).timestamp(),
        }

        with (
            patch("app.core.security.PROJECT_SETTINGS") as mock_settings,
            patch("app.core.security.jwt.decode") as mock_decode,
        ):
            mock_settings.secret_key = "test_secret"
            mock_settings.algorithm = "HS256"
            mock_decode.return_value = expired_payload

            with pytest.raises(HTTPException) as exc_info:
                security_manager.verify_token("expired_token")

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Token has expired"
            assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

    def test_verify_token_jwt_error(self, security_manager):
        """Test token verification with JWT error"""
        with (
            patch("app.core.security.PROJECT_SETTINGS") as mock_settings,
            patch("app.core.security.jwt.decode") as mock_decode,
            patch("app.core.security.logger") as mock_logger,
        ):
            mock_settings.secret_key = "test_secret"
            mock_settings.algorithm = "HS256"
            mock_decode.side_effect = JWTError("Invalid token")

            with pytest.raises(HTTPException) as exc_info:
                security_manager.verify_token("invalid_token")

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Could not validate credentials"
            assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
            mock_logger.warning.assert_called_once()

    def test_verify_token_general_exception(self, security_manager):
        """Test token verification with general exception"""
        with (
            patch("app.core.security.PROJECT_SETTINGS") as mock_settings,
            patch("app.core.security.jwt.decode") as mock_decode,
            patch("app.core.security.logger") as mock_logger,
        ):
            mock_settings.secret_key = "test_secret"
            mock_settings.algorithm = "HS256"
            mock_decode.side_effect = Exception("Unexpected error")

            with pytest.raises(HTTPException) as exc_info:
                security_manager.verify_token("token")

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert exc_info.value.detail == "Token verification failed"
            mock_logger.error.assert_called_once()

    def test_verify_token_no_expiry(self, security_manager):
        """Test token verification with no expiry field"""
        test_payload = {"sub": "user123"}  # No 'exp' field

        with (
            patch("app.core.security.PROJECT_SETTINGS") as mock_settings,
            patch("app.core.security.jwt.decode") as mock_decode,
        ):
            mock_settings.secret_key = "test_secret"
            mock_settings.algorithm = "HS256"
            mock_decode.return_value = test_payload

            result = security_manager.verify_token("test_token")

            assert result == test_payload

    def test_get_current_user_id_success(self, security_manager):
        """Test successful user ID extraction"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="test_token"
        )
        test_payload = {"sub": "user123", "email": "test@example.com"}

        with patch.object(security_manager, "verify_token", return_value=test_payload):
            user_id = security_manager.get_current_user_id(credentials)

            assert user_id == "user123"

    def test_get_current_user_id_missing_subject(self, security_manager):
        """Test user ID extraction with missing subject"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="test_token"
        )
        test_payload = {"email": "test@example.com"}  # No 'sub' field

        with patch.object(security_manager, "verify_token", return_value=test_payload):
            with pytest.raises(HTTPException) as exc_info:
                security_manager.get_current_user_id(credentials)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Invalid token payload"
            assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

    def test_get_current_user_id_none_subject(self, security_manager):
        """Test user ID extraction with None subject"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="test_token"
        )
        test_payload = {"sub": None, "email": "test@example.com"}

        with patch.object(security_manager, "verify_token", return_value=test_payload):
            with pytest.raises(HTTPException) as exc_info:
                security_manager.get_current_user_id(credentials)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Invalid token payload"

    def test_get_current_user_id_verify_token_exception(self, security_manager):
        """Test user ID extraction when token verification fails"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid_token"
        )

        with patch.object(
            security_manager,
            "verify_token",
            side_effect=HTTPException(status_code=401, detail="Invalid"),
        ):
            with pytest.raises(HTTPException):
                security_manager.get_current_user_id(credentials)

    def test_integration_password_flow(self, security_manager):
        """Test complete password hash and verify flow"""
        password = "secure_password123"

        # Hash password
        hashed = security_manager.get_password_hash(password)

        # Verify correct password
        assert security_manager.verify_password(password, hashed) is True

        # Verify wrong password
        assert security_manager.verify_password("wrong_password", hashed) is False

    def test_integration_jwt_flow(self, security_manager):
        """Test complete JWT creation and verification flow"""
        user_data = {"sub": "user123", "email": "test@example.com"}

        with patch("app.core.security.PROJECT_SETTINGS") as mock_settings:
            mock_settings.secret_key = (
                "test_secret_key_that_is_long_enough_for_testing_purposes"
            )
            mock_settings.algorithm = "HS256"
            mock_settings.access_token_expire_minutes = 30

            # Create token
            token = security_manager.create_access_token(user_data)
            assert isinstance(token, str)
            assert len(token) > 0

            # Verify token
            payload = security_manager.verify_token(token)
            assert payload["sub"] == "user123"
            assert payload["email"] == "test@example.com"

            # Extract user ID
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer", credentials=token
            )
            user_id = security_manager.get_current_user_id(credentials)
            assert user_id == "user123"


class TestSecurityModuleConstants:
    """Test module-level constants and instances"""

    def test_pwd_context_configuration(self):
        """Test password context configuration"""
        assert isinstance(pwd_context, CryptContext)
        assert "bcrypt" in pwd_context.schemes()

    def test_security_bearer_instance(self):
        """Test HTTPBearer security instance"""
        from fastapi.security import HTTPBearer

        assert isinstance(security, HTTPBearer)

    def test_global_security_manager_instance(self):
        """Test global security_manager instance"""
        from app.core.security import security_manager

        assert security_manager is not None
        assert isinstance(security_manager, SecurityManager)

    def test_password_hashing_consistency(self):
        """Test that password hashing is consistent with verification"""
        password = "test_password"

        # Hash the same password multiple times
        hash1 = pwd_context.hash(password)
        hash2 = pwd_context.hash(password)

        # Hashes should be different (due to salt)
        assert hash1 != hash2

        # But both should verify against the original password
        assert pwd_context.verify(password, hash1)
        assert pwd_context.verify(password, hash2)

    def test_password_verification_with_wrong_password(self):
        """Test password verification fails with wrong password"""
        password = "correct_password"
        wrong_password = "wrong_password"

        hashed = pwd_context.hash(password)

        assert pwd_context.verify(password, hashed) is True
        assert pwd_context.verify(wrong_password, hashed) is False


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    @pytest.fixture
    def security_manager(self):
        return SecurityManager()

    def test_empty_password_hash(self, security_manager):
        """Test hashing empty password"""
        hashed = security_manager.get_password_hash("")
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert security_manager.verify_password("", hashed) is True

    def test_very_long_password(self, security_manager):
        """Test hashing very long password"""
        long_password = "a" * 1000
        hashed = security_manager.get_password_hash(long_password)
        assert security_manager.verify_password(long_password, hashed) is True

    def test_unicode_password(self, security_manager):
        """Test hashing password with unicode characters"""
        unicode_password = "pässwörd123!@#$%^&*()_+{}[]|\\:\";'<>?,./"
        hashed = security_manager.get_password_hash(unicode_password)
        assert security_manager.verify_password(unicode_password, hashed) is True

    def test_token_with_empty_data(self, security_manager):
        """Test creating token with empty data"""
        with patch("app.core.security.PROJECT_SETTINGS") as mock_settings:
            mock_settings.secret_key = "test_secret_key_that_is_long_enough"
            mock_settings.algorithm = "HS256"
            mock_settings.access_token_expire_minutes = 30

            token = security_manager.create_access_token({})
            payload = security_manager.verify_token(token)

            assert "exp" in payload
            assert "iat" in payload

    def test_token_with_large_payload(self, security_manager):
        """Test creating token with large payload"""
        large_data = {"sub": "user123"}
        for i in range(100):
            large_data[f"field_{i}"] = f"value_{i}" * 10

        with patch("app.core.security.PROJECT_SETTINGS") as mock_settings:
            mock_settings.secret_key = "test_secret_key_that_is_long_enough"
            mock_settings.algorithm = "HS256"
            mock_settings.access_token_expire_minutes = 30

            token = security_manager.create_access_token(large_data)
            payload = security_manager.verify_token(token)

            assert payload["sub"] == "user123"
            assert len(payload) > 100
