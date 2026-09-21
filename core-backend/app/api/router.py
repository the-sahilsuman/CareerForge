from fastapi import APIRouter

from app.api.routes import (
    applications,
    certifications,
    education,
    experience,
    health,
    notifications,
    profile,
    projects,
    resumes,
    skills,
    email_connections,
    emails,
    users,
    agentic,
)

from app.api.routes.buckets import router as buckets_router

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(users.router)
api_router.include_router(profile.router)
api_router.include_router(skills.router)
api_router.include_router(education.router)
api_router.include_router(experience.router)
api_router.include_router(projects.router)
api_router.include_router(certifications.router)

api_router.include_router(resumes.router)
api_router.include_router(applications.router)

api_router.include_router(email_connections.router)
api_router.include_router(emails.router)
api_router.include_router(notifications.router)
api_router.include_router(agentic.router)
api_router.include_router(buckets_router)