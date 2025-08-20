"""Custom exceptions for Hunter.io API client."""


class HunterAPIError(Exception):
    """Base exception for Hunter.io API errors."""

    def __init__(self, message: str = 'Hunter API error occurred') -> None:
        """Initialize the HunterAPIError.

        Args:
            message: The error message to display.

        """
        super().__init__(message)
        self.message = message


class MissingNameError(HunterAPIError):
    """Exception raised when a name is missing for email finding."""


class MissingCompanyError(HunterAPIError):
    """Exception raised when a company is missing for email finding."""
