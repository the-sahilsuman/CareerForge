class AppError(Exception):
    def __init__(
        self,
        message: str,
        code: str = "APPLICATION_ERROR",
    ):
        self.message = message
        self.code = code

        super().__init__(message)


class ResourceNotFoundError(AppError):

    def __init__(
        self,
        message: str = "Resource not found.",
    ):
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
        )


class ConflictError(AppError):

    def __init__(
        self,
        message: str = "Resource already exists.",
    ):
        super().__init__(
            message=message,
            code="CONFLICT",
        )


class ForbiddenError(AppError):

    def __init__(
        self,
        message: str = "Access denied.",
    ):
        super().__init__(
            message=message,
            code="FORBIDDEN",
        )


class ValidationError(AppError):

    def __init__(
        self,
        message: str = "Invalid request.",
    ):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
        )

class AppError(Exception):

    status_code = 500

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ResourceNotFoundError(AppError):

    status_code = 404


class ConflictError(AppError):

    status_code = 409


class UnauthorizedError(AppError):

    status_code = 401


class ForbiddenError(AppError):

    status_code = 403


class BadRequestError(AppError):

    status_code = 400