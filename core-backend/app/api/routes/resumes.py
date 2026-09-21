from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    status,
)

from app.api.dependencies import (
    CurrentUser,
    get_current_user,
)
from app.api.repository_dependencies import (
    get_resume_service,
)
from app.schemas.resume import ResumeResponse
from app.services.resume import ResumeService


router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"],
)


@router.post(
    "/upload",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: ResumeService = Depends(
        get_resume_service
    ),
):

    file_bytes = await file.read()

    return await service.upload_resume(
        current_user.id,
        file_bytes=file_bytes,
        file_name=file.filename or "resume.pdf",
        content_type=file.content_type
        or "application/octet-stream",
    )


@router.get(
    "",
    response_model=ResumeResponse | None,
)
async def get_my_resume(
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: ResumeService = Depends(
        get_resume_service
    ),
):

    return await service.get_resume(
        current_user.id
    )

@router.get(
    "/download-url",
)
async def get_resume_download_url(
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: ResumeService = Depends(
        get_resume_service
    ),
):
    return await service.get_download_url(
        current_user.id
    )


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_my_resume(
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: ResumeService = Depends(
        get_resume_service
    ),
):

    await service.delete_resume(
        current_user.id
    )