import hashlib
import hmac
import json
import urllib.parse
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class TelegramAuthError(Exception):
    """Custom exception for Telegram authentication errors"""

    def __init__(self, message: str, error_code: str = "AUTH_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class TelegramAuth:
    def __init__(self, bot_token: str):
        if not bot_token:
            raise ValueError("Bot token is required")
        self.bot_token = bot_token
        self.secret_key = hashlib.sha256(bot_token.encode()).digest()

    def parse_init_data(self, init_data: str) -> Dict[str, Any]:
        """Parse Telegram initData string into dictionary"""
        try:
            if not init_data or not init_data.strip():
                raise TelegramAuthError("Empty init data", "EMPTY_DATA")

            parsed = urllib.parse.parse_qs(init_data)
            result = {}

            for key, value in parsed.items():
                if len(value) == 1:
                    if key == "user":
                        try:
                            result[key] = json.loads(value[0])
                        except json.JSONDecodeError:
                            raise TelegramAuthError(
                                "Invalid user data format", "INVALID_USER_DATA"
                            )
                    elif key in ["auth_date", "query_id"]:
                        result[key] = value[0]
                    else:
                        result[key] = value[0]
                else:
                    result[key] = value

            return result
        except TelegramAuthError:
            raise
        except Exception as e:
            logger.error(f"Failed to parse init data: {str(e)}")
            raise TelegramAuthError("Invalid data format", "PARSE_ERROR")

    def validate_hash(self, init_data: str) -> bool:
        """Validate Telegram initData hash according to official docs"""
        try:
            parsed_data = urllib.parse.parse_qs(init_data)

            if "hash" not in parsed_data:
                raise TelegramAuthError("Missing authentication hash", "NO_HASH")

            received_hash = parsed_data["hash"][0]
            if not received_hash:
                raise TelegramAuthError("Empty authentication hash", "EMPTY_HASH")

            # Remove hash from data for validation
            data_check_string_parts = []
            for key, value in parsed_data.items():
                if key != "hash" and value and value[0]:
                    data_check_string_parts.append(f"{key}={value[0]}")

            if not data_check_string_parts:
                raise TelegramAuthError("No data to validate", "NO_DATA")

            # Sort alphabetically
            data_check_string_parts.sort()
            data_check_string = "\n".join(data_check_string_parts)

            # Create HMAC
            secret_key = hmac.new(
                "WebAppData".encode(), self.bot_token.encode(), hashlib.sha256
            ).digest()

            calculated_hash = hmac.new(
                secret_key, data_check_string.encode(), hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(received_hash, calculated_hash)

        except TelegramAuthError:
            raise
        except Exception as e:
            logger.error(f"Hash validation error: {str(e)}")
            raise TelegramAuthError("Hash validation failed", "HASH_VALIDATION_ERROR")

    def validate_auth_date(self, auth_date: str, max_age_seconds: int = 86400) -> bool:
        """Validate that auth_date is not too old (default: 24 hours)"""
        try:
            if not auth_date:
                return False

            auth_timestamp = int(auth_date)
            current_timestamp = int(datetime.now(timezone.utc).timestamp())

            return current_timestamp - auth_timestamp <= max_age_seconds
        except (ValueError, TypeError):
            return False

    def authenticate(self, init_data: str) -> Dict[str, Any]:
        """
        Full authentication process with secure error handling
        """
        try:
            # Basic validation
            if not init_data or not init_data.strip():
                raise TelegramAuthError("Authentication data required", "MISSING_DATA")

            # Validate hash
            if not self.validate_hash(init_data):
                raise TelegramAuthError("Invalid authentication", "INVALID_HASH")

            # Parse data
            parsed_data = self.parse_init_data(init_data)

            # Validate auth_date
            if "auth_date" not in parsed_data:
                raise TelegramAuthError(
                    "Authentication timestamp missing", "NO_AUTH_DATE"
                )

            if not self.validate_auth_date(parsed_data["auth_date"]):
                raise TelegramAuthError("Authentication expired", "EXPIRED_AUTH")

            # Validate user data
            if "user" not in parsed_data or not parsed_data["user"]:
                raise TelegramAuthError("User information missing", "NO_USER_DATA")

            user_data = parsed_data["user"]

            # Validate required user fields
            required_fields = ["id", "first_name"]
            for field in required_fields:
                if field not in user_data:
                    raise TelegramAuthError(
                        "Incomplete user data", "INCOMPLETE_USER_DATA"
                    )

            return user_data

        except TelegramAuthError as e:
            # Log the specific error for debugging but don't expose details
            logger.warning(f"Telegram auth failed: {e.error_code} - {e.message}")
            # Always return generic error to client
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "tma"},
            )
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Unexpected auth error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "tma"},
            )
