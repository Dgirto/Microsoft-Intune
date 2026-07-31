"""Jerarquía de excepciones del conector Microsoft Intune."""

from __future__ import annotations


class IntuneConnectorError(Exception):
    """Error base del conector Microsoft Intune."""


class IntuneAuthError(IntuneConnectorError):
    """Credenciales inválidas o Service Principal sin permiso suficiente."""


class IntuneNetworkError(IntuneConnectorError):
    """Error de red o timeout al conectar con Microsoft Graph."""


class IntuneDataError(IntuneConnectorError):
    """Dispositivo inexistente u otro error de datos devuelto por Graph."""
