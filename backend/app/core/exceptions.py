class TTXTraderException(Exception):
    """Base exception for TTX Trader backend failures."""


class AuthenticationException(TTXTraderException):
    """Raised when Shioaji authentication fails or credentials are incomplete."""


class CAActivationException(TTXTraderException):
    """Raised when Shioaji CA certificate activation fails."""


class ConnectionLostException(TTXTraderException):
    """Raised when the Shioaji connection cannot be restored after retries."""
