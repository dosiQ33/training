import hashlib
import hmac
import json
import urllib.parse
from typing import Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException, status


class TelegramAuthError(Exception):
    """Custom exception for Telegram authentication errors"""

    pass


class TelegramAuth:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.secret_key = hashlib.sha256(bot_token.encode()).digest()

    def parse_init_data(self, init_data: str) -> Dict[str, Any]:
        """Parse Telegram initData string into dictionary"""
        try:
            parsed = urllib.parse.parse_qs(init_data)
            result = {}

            for key, value in parsed.items():
                if len(value) == 1:
                    if key == "user":
                        # Parse user JSON string
                        result[key] = json.loads(value[0])
                    elif key in ["auth_date", "query_id"]:
                        result[key] = value[0]
                    else:
                        result[key] = value[0]
                else:
                    result[key] = value

            return result
        except Exception as e:
            raise TelegramAuthError(f"Failed to parse init data: {str(e)}")

    def validate_hash(self, init_data: str) -> bool:
        """Validate Telegram initData hash according to official docs"""
        try:
            parsed_data = urllib.parse.parse_qs(init_data)

            # Extract hash from init_data
            if "hash" not in parsed_data:
                raise TelegramAuthError("Hash not found in init data")

            received_hash = parsed_data["hash"][0]

            # Remove hash from data for validation
            data_check_string_parts = []
            for key, value in parsed_data.items():
                if key != "hash":
                    data_check_string_parts.append(f"{key}={value[0]}")

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

        except Exception as e:
            raise TelegramAuthError(f"Hash validation failed: {str(e)}")

    def validate_auth_date(self, auth_date: str, max_age_seconds: int = 86400) -> bool:
        """Validate that auth_date is not too old (default: 24 hours)"""
        try:
            auth_timestamp = int(auth_date)
            current_timestamp = int(datetime.now(timezone.utc).timestamp())

            if current_timestamp - auth_timestamp > max_age_seconds:
                return False

            return True
        except (ValueError, TypeError):
            return False

    def authenticate(self, init_data: str) -> Dict[str, Any]:
        """
        Full authentication process:
        1. Validate hash
        2. Check auth_date
        3. Return user data if valid
        """
        # Validate hash
        if not self.validate_hash(init_data):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Telegram authentication hash",
            )

        # Parse data
        parsed_data = self.parse_init_data(init_data)

        # Validate auth_date
        if "auth_date" not in parsed_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Auth date not found"
            )

        if not self.validate_auth_date(parsed_data["auth_date"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication data expired",
            )

        # Return user data
        if "user" not in parsed_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User data not found"
            )

        return parsed_data["user"]
