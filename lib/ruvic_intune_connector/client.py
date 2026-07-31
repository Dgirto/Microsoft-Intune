"""Cliente de Microsoft Intune (vía Microsoft Graph) para gestión de dispositivos.

Capacidades:
- list_devices():    lista los dispositivos administrados por Intune.
- get_compliance():  consulta el estado de cumplimiento de un dispositivo.
- sync_device():     dispara una sincronización remota de un dispositivo.

Las credenciales SIEMPRE provienen de variables de entorno
RUVIC_INTUNE_* (ver config.IntuneConfig.from_env). Prohibido
hardcodearlas.

Autenticación: azure-identity.ClientSecretCredential contra el scope
"https://graph.microsoft.com/.default" (client credentials flow).
"""

from __future__ import annotations

from typing import Any

import requests
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import ClientSecretCredential
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import HTTPError, Timeout

from .config import IntuneConfig
from .exceptions import IntuneAuthError, IntuneDataError, IntuneNetworkError
from .logging_utils import get_logger

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
GRAPH_SCOPE = "https://graph.microsoft.com/.default"


class IntuneClient:
    """Cliente de Microsoft Intune sobre Microsoft Graph.

    Args:
        config: configuración de conexión. Si se omite, se lee de las
            variables de entorno RUVIC_INTUNE_* (comportamiento
            estándar en el runtime de la plataforma).

    Ejemplo:
        >>> client = IntuneClient()  # lee RUVIC_INTUNE_* del entorno
        >>> client.list_devices()
    """

    def __init__(self, config: IntuneConfig | None = None) -> None:
        self.config = config or IntuneConfig.from_env()
        self._logger = get_logger()
        self._credential: ClientSecretCredential | None = None

    # ------------------------------------------------------------------ #
    # Conexión
    # ------------------------------------------------------------------ #

    def _get_credential(self) -> ClientSecretCredential:
        if self._credential is None:
            self._credential = ClientSecretCredential(
                tenant_id=self.config.tenant_id,
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
            )
        return self._credential

    def _get_token(self) -> str:
        try:
            token = self._get_credential().get_token(GRAPH_SCOPE)
        except ClientAuthenticationError as exc:
            raise IntuneAuthError(f"Credenciales inválidas: {exc}") from exc
        return token.token

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._get_token()}"
        try:
            response = requests.request(
                method,
                f"{GRAPH_BASE_URL}{path}",
                headers=headers,
                timeout=self.config.connect_timeout,
                **kwargs,
            )
        except Timeout as exc:
            raise IntuneNetworkError(f"Timeout conectando a Microsoft Graph: {exc}") from exc
        except RequestsConnectionError as exc:
            raise IntuneNetworkError(f"No se pudo conectar a Microsoft Graph: {exc}") from exc

        if response.status_code in (401, 403):
            raise IntuneAuthError(
                f"Credenciales inválidas o sin permiso suficiente ({response.status_code})."
            )
        if response.status_code == 404:
            raise IntuneDataError(f"Recurso no encontrado: {path}")
        try:
            response.raise_for_status()
        except HTTPError as exc:
            raise IntuneDataError(f"Error de Microsoft Graph: {exc}") from exc
        return response

    def ping(self) -> bool:
        """Verifica la conexión listando dispositivos administrados.

        Returns:
            True si la conexión funciona.

        Raises:
            IntuneAuthError / IntuneNetworkError / IntuneDataError.
        """
        self.list_devices()
        self._logger.info("Ping exitoso a Microsoft Intune")
        return True

    # ------------------------------------------------------------------ #
    # Capacidad 1: listar dispositivos
    # ------------------------------------------------------------------ #

    def list_devices(self) -> list[dict[str, Any]]:
        """Lista los dispositivos administrados por Intune.

        Returns:
            Lista de dicts con id, deviceName, operatingSystem,
            complianceState.

        Ejemplo:
            >>> client.list_devices()
            [{'id': '...', 'deviceName': 'LAPTOP-01', ...}]
        """
        response = self._request(
            "GET",
            "/deviceManagement/managedDevices"
            "?$select=id,deviceName,operatingSystem,complianceState",
        )
        devices = response.json().get("value", [])
        self._logger.info("Listados %d dispositivos", len(devices))
        return devices

    # ------------------------------------------------------------------ #
    # Capacidad 2: estado de cumplimiento
    # ------------------------------------------------------------------ #

    def get_compliance(self, device_id: str) -> dict[str, Any]:
        """Consulta el estado de cumplimiento de un dispositivo.

        Args:
            device_id: ID del dispositivo administrado en Intune.

        Returns:
            Dict con id, deviceName y complianceState.

        Ejemplo:
            >>> client.get_compliance("device-id")
            {'id': 'device-id', 'deviceName': 'LAPTOP-01', 'complianceState': 'compliant'}
        """
        response = self._request(
            "GET",
            f"/deviceManagement/managedDevices/{device_id}"
            "?$select=id,deviceName,complianceState",
        )
        data = response.json()
        self._logger.info(
            "Cumplimiento de %s: %s", device_id, data.get("complianceState")
        )
        return data

    # ------------------------------------------------------------------ #
    # Capacidad 3: sincronizar dispositivo (acción remota)
    # ------------------------------------------------------------------ #

    def sync_device(self, device_id: str) -> None:
        """Dispara una sincronización remota del dispositivo con Intune.

        Args:
            device_id: ID del dispositivo administrado en Intune.

        Ejemplo:
            >>> client.sync_device("device-id")
        """
        self._request(
            "POST", f"/deviceManagement/managedDevices/{device_id}/syncDevice"
        )
        self._logger.info("Sincronización disparada para el dispositivo %s", device_id)
