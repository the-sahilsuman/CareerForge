import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings


class CognitoClientError(Exception):
    """Raised when a Cognito operation fails."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code


class CognitoClient:
    def __init__(self) -> None:
        self.client = boto3.client(
            "cognito-idp",
            region_name=settings.aws_region,
        )

    def get_user_by_username(
        self,
        username: str,
    ) -> dict:
        try:
            response = self.client.admin_get_user(
                UserPoolId=settings.cognito_user_pool_id,
                Username=username,
            )

            return response

        except ClientError as exc:
            error = exc.response.get("Error", {})

            error_code = error.get(
                "Code",
                "UnknownError",
            )

            error_message = error.get(
                "Message",
                str(exc),
            )

            raise CognitoClientError(
                message=(
                    f"Cognito AdminGetUser failed: "
                    f"{error_code}: {error_message}"
                ),
                error_code=error_code,
            ) from exc

        except BotoCoreError as exc:
            raise CognitoClientError(
                message=f"AWS Cognito client error: {exc}",
            ) from exc

    def get_confirmed_user(
        self,
        username: str,
    ) -> dict:
        response = self.get_user_by_username(
            username=username,
        )

        user_status = response.get("UserStatus")

        if user_status != "CONFIRMED":
            raise CognitoClientError(
                message=(
                    "Cognito user is not confirmed. "
                    f"Current status: {user_status}"
                ),
            )

        return response

    @staticmethod
    def get_attribute(
        user: dict,
        name: str,
    ) -> str | None:
        for attribute in user.get(
            "UserAttributes",
            [],
        ):
            if attribute.get("Name") == name:
                return attribute.get("Value")

        return None