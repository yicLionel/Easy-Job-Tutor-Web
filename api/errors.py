from dataclasses import dataclass


@dataclass
class ApiError(Exception):
    status_code: int
    error_code: str
    message: str
    retryable: bool = False
    supported_action: str = ""

    def __str__(self) -> str:
        return self.message
