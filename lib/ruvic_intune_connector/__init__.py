"""Conector Ruvic para Microsoft Intune (Microsoft Graph): dispositivos y cumplimiento."""

from .client import IntuneClient
from .config import ENV_PREFIX, IntuneConfig
from .exceptions import IntuneAuthError, IntuneConnectorError, IntuneDataError, IntuneNetworkError
from .logging_utils import setup_logging

__all__ = [
    "ENV_PREFIX",
    "IntuneAuthError",
    "IntuneClient",
    "IntuneConfig",
    "IntuneConnectorError",
    "IntuneDataError",
    "IntuneNetworkError",
    "setup_logging",
]

__version__ = "1.0.0"
