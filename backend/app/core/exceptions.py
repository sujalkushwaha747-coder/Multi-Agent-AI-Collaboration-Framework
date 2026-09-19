from fastapi import HTTPException, status


class ShodhAIError(Exception):
    """Base application error with a user-safe message."""

    def __init__(self, message: str, *, error_type: str = "application_error"):
        super().__init__(message)
        self.message = message
        self.error_type = error_type


class LLMUnavailableError(ShodhAIError):
    def __init__(self, message: str):
        super().__init__(message, error_type="llm_unavailable")


class RetrievalError(ShodhAIError):
    def __init__(self, message: str):
        super().__init__(message, error_type="retrieval_error")


class EvaluationError(ShodhAIError):
    def __init__(self, message: str):
        super().__init__(message, error_type="evaluation_error")


class InvalidUploadError(ShodhAIError):
    def __init__(self, message: str):
        super().__init__(message, error_type="invalid_upload")


def http_bad_request(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def http_not_found(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

