class AppException(Exception):
    code: str = "APP_ERROR"
    status_code: int = 500
    message: str = "An unexpected error occurred"

    def __init__(self, message: str | None = None):
        if message:
            self.message = message
        super().__init__(self.message)


class NotFoundError(AppException):
    code = "NOT_FOUND"
    status_code = 404


class UnauthorizedError(AppException):
    code = "UNAUTHORIZED"
    status_code = 401


class ForbiddenError(AppException):
    code = "FORBIDDEN"
    status_code = 403


class BadRequestError(AppException):
    code = "BAD_REQUEST"
    status_code = 400