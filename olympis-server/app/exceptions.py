class BaseError(Exception):
    status_code = 500
    code = "INTERNAL_ERROR"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ResourceNotFoundError(BaseError):
    status_code = 404
    code = "NOT_FOUND"


class ValidationError(BaseError):
    status_code = 400
    code = "VALIDATION_ERROR"


class UnauthorizedError(BaseError):
    status_code = 401
    code = "UNAUTHORIZED"
