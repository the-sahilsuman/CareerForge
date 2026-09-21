from app.core.identifiers import generate_user_id
from app.models.enums import UserRole, UserStatus
from app.models.user import User
from app.repositories.user import UserRepository


class UserService:

    def __init__(
        self,
        repository: UserRepository,
    ):
        self.repository = repository

    async def get_or_create_from_cognito(
        self,
        *,
        cognito_sub: str,
        login_email: str,
    ) -> User:

        existing = await self.repository.get_by_cognito_sub(
            cognito_sub
        )

        if existing:
            return existing

        user_id = generate_user_id()

        user = User(
            user_id=user_id,
            cognito_sub=cognito_sub,
            login_email=login_email,
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
        )

        await self.repository.create(user)

        return user