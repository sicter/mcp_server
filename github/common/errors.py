from datetime import datetime
from typing import Any, Optional


class GitHubError(Exception):
    def __init__(self, message: str, status: int, response: Any):
        super().__init__(message)
        self.status = status
        self.response = response
        self.name = "GitHubError"


class GitHubValidationError(GitHubError):
    def __init__(self, message: str, status: int, response: Any):
        super().__init__(message, status, response)
        self.name = "GitHubValidationError"


class GitHubResourceNotFoundError(GitHubError):
    def __init__(self, resource: str):
        super().__init__(
            f"Resource not found: {resource}", 
            404, 
            {"message": f"{resource} not found"}
        )
        self.name = "GitHubResourceNotFoundError"


class GitHubAuthenticationError(GitHubError):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401, {"message": message})
        self.name = "GitHubAuthenticationError"


class GitHubPermissionError(GitHubError):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, 403, {"message": message})
        self.name = "GitHubPermissionError"


class GitHubRateLimitError(GitHubError):
    def __init__(self, message: str = "Rate limit exceeded", reset_at: Optional[datetime] = None):
        reset_at = reset_at or datetime.now()
        super().__init__(
            message, 
            429, 
            {"message": message, "reset_at": reset_at.isoformat()}
        )
        self.reset_at = reset_at
        self.name = "GitHubRateLimitError"


class GitHubConflictError(GitHubError):
    def __init__(self, message: str):
        super().__init__(message, 409, {"message": message})
        self.name = "GitHubConflictError"


def is_github_error(error: Any) -> bool:
    return isinstance(error, GitHubError)


def create_github_error(status: int, response: Optional[Any] = None) -> GitHubError:
    response = response or {}
    message = response.get("message", "GitHub API error")
    
    if status == 401:
        return GitHubAuthenticationError(message)
    elif status == 403:
        return GitHubPermissionError(message)
    elif status == 404:
        return GitHubResourceNotFoundError(response.get("message", "Resource"))
    elif status == 409:
        return GitHubConflictError(response.get("message", "Conflict occurred"))
    elif status == 422:
        return GitHubValidationError(
            response.get("message", "Validation failed"), status, response
        )
    elif status == 429:
        reset_at = datetime.fromisoformat(response.get("reset_at", datetime.now().isoformat()))
        return GitHubRateLimitError(message, reset_at)
    else:
        return GitHubError(message, status, response)
