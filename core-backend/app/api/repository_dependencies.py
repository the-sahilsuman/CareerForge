from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.clients.s3 import S3Client

from app.repositories.user import UserRepository
from app.repositories.profile import ProfileRepository
from app.repositories.skill import SkillRepository
from app.repositories.education import EducationRepository
from app.repositories.experience import ExperienceRepository
from app.repositories.project import ProjectRepository
from app.repositories.certification import CertificationRepository
from app.repositories.resume import ResumeRepository   

from app.repositories.application import ApplicationRepository
from app.repositories.application_event import (
    ApplicationEventRepository
)

from app.services.user import UserService
from app.services.profile import ProfileService
from app.services.skill import SkillService
from app.services.education import EducationService
from app.services.experience import ExperienceService
from app.services.project import ProjectService
from app.services.certification import CertificationService
from app.services.resume import ResumeService
from app.services.application import ApplicationService
from app.services.application_event import (
    ApplicationEventService,
)

from app.repositories.email_connection import (
    EmailConnectionRepository,
)
from app.services.email_connection import (
    EmailConnectionService,
)

from app.repositories.email import EmailRepository
from app.services.email import EmailService

from app.clients.cognito import CognitoClient

from app.repositories.agentic_email import (
    AgenticEmailRepository,
)

from app.services.agentic_email import (
    AgenticEmailService,
)

# ============================================================
# AGENTIC EMAIL RECORDS
# ============================================================

def get_agentic_email_repository(
    db: AsyncSession = Depends(get_db),
) -> AgenticEmailRepository:

    return AgenticEmailRepository(db)


def get_agentic_email_service(
    repository: AgenticEmailRepository = Depends(
        get_agentic_email_repository
    ),
) -> AgenticEmailService:

    return AgenticEmailService(
        repository=repository,
    )

# ============================================================
# USER
# ============================================================

def get_user_repository(
    db: AsyncSession = Depends(get_db),
) -> UserRepository:

    return UserRepository(db)


def get_user_service(
    repository: UserRepository = Depends(
        get_user_repository
    ),
) -> UserService:

    return UserService(repository)


# ============================================================
# PROFILE
# ============================================================

def get_profile_repository(
    db: AsyncSession = Depends(get_db),
) -> ProfileRepository:

    return ProfileRepository(db)

def get_email_connection_repository(
    db: AsyncSession = Depends(get_db),
) -> EmailConnectionRepository:

    return EmailConnectionRepository(db)


def get_email_connection_service(
    repository: EmailConnectionRepository = Depends(
        get_email_connection_repository
    ),
    profile_repository: ProfileRepository = Depends(
        get_profile_repository
    ),
) -> EmailConnectionService:

    return EmailConnectionService(
        repository=repository,
        profile_repository=profile_repository,
    )


def get_profile_service(
    repository: ProfileRepository = Depends(
        get_profile_repository
    ),
    email_connection_repository: EmailConnectionRepository = Depends(
        get_email_connection_repository
    ),
) -> ProfileService:

    return ProfileService(
        repository=repository,
        email_connection_repository=(
            email_connection_repository
        ),
    )


# ============================================================
# PROFESSIONAL EMAIL
# ============================================================



# ============================================================
# SKILL
# ============================================================

def get_skill_repository(
    db: AsyncSession = Depends(get_db),
) -> SkillRepository:

    return SkillRepository(db)


def get_skill_service(
    repository: SkillRepository = Depends(
        get_skill_repository
    ),
) -> SkillService:

    return SkillService(repository)


# ============================================================
# EDUCATION
# ============================================================

def get_education_repository(
    db: AsyncSession = Depends(get_db),
) -> EducationRepository:

    return EducationRepository(db)


def get_education_service(
    repository: EducationRepository = Depends(
        get_education_repository
    ),
) -> EducationService:

    return EducationService(repository)


# ============================================================
# EXPERIENCE
# ============================================================

def get_experience_repository(
    db: AsyncSession = Depends(get_db),
) -> ExperienceRepository:

    return ExperienceRepository(db)


def get_experience_service(
    repository: ExperienceRepository = Depends(
        get_experience_repository
    ),
) -> ExperienceService:

    return ExperienceService(repository)


# ============================================================
# PROJECT
# ============================================================

def get_project_repository(
    db: AsyncSession = Depends(get_db),
) -> ProjectRepository:

    return ProjectRepository(db)


def get_project_service(
    repository: ProjectRepository = Depends(
        get_project_repository
    ),
) -> ProjectService:

    return ProjectService(repository)


# ============================================================
# CERTIFICATION
# ============================================================

def get_certification_repository(
    db: AsyncSession = Depends(get_db),
) -> CertificationRepository:

    return CertificationRepository(db)


def get_certification_service(
    repository: CertificationRepository = Depends(
        get_certification_repository
    ),
) -> CertificationService:

    return CertificationService(repository)


# ============================================================
# RESUME
# ============================================================

def get_s3_client() -> S3Client:

    return S3Client()


def get_resume_repository(
    db: AsyncSession = Depends(get_db),
) -> ResumeRepository:

    return ResumeRepository(db)


def get_resume_service(
    repository: ResumeRepository = Depends(
        get_resume_repository
    ),
    s3_client: S3Client = Depends(
        get_s3_client
    ),
) -> ResumeService:

    return ResumeService(
        repository=repository,
        s3_client=s3_client,
    )


# ============================================================
# APPLICATION
# ============================================================

def get_application_repository(
    db: AsyncSession = Depends(get_db),
) -> ApplicationRepository:

    return ApplicationRepository(db)


def get_application_service(
    repository: ApplicationRepository = Depends(
        get_application_repository
    ),
) -> ApplicationService:

    return ApplicationService(repository)


# ============================================================
# APPLICATION EVENT
# ============================================================

def get_application_event_repository(
    db: AsyncSession = Depends(get_db),
) -> ApplicationEventRepository:

    return ApplicationEventRepository(db)


def get_application_event_service(
    repository: ApplicationEventRepository = Depends(
        get_application_event_repository
    ),
) -> ApplicationEventService:

    return ApplicationEventService(repository)


def get_email_repository(
    db: AsyncSession = Depends(get_db),
) -> EmailRepository:

    return EmailRepository(db)


def get_email_service(
    repository: EmailRepository = Depends(
        get_email_repository
    ),
) -> EmailService:

    return EmailService(repository)


def get_cognito_client() -> CognitoClient:
    return CognitoClient()
