"""Configuración del conector leída desde variables de entorno.

Convención de la plataforma: cada campo del formulario de configuración
llega como variable de entorno {ENV_PREFIX}{CAMPO} en mayúsculas.
Para este conector el prefijo es RUVIC_INTUNE_.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

ENV_PREFIX = "RUVIC_INTUNE_"


@dataclass(frozen=True)
class IntuneConfig:
    """Parámetros de conexión a Microsoft Intune (Graph) vía Service Principal."""

    tenant_id: str
    client_id: str
    client_secret: str
    connect_timeout: int = 10

    @classmethod
    def from_env(cls) -> "IntuneConfig":
        """Construye la configuración desde las variables RUVIC_INTUNE_*.

        Raises:
            ValueError: si falta alguna variable obligatoria.

        Ejemplo:
            >>> config = IntuneConfig.from_env()
            >>> config.tenant_id
            '00000000-0000-0000-0000-000000000000'
        """
        missing = [
            f"{ENV_PREFIX}{name}"
            for name in ("TENANT_ID", "CLIENT_ID", "CLIENT_SECRET")
            if not os.environ.get(f"{ENV_PREFIX}{name}")
        ]
        if missing:
            raise ValueError(
                "Faltan variables de entorno del conector intune: "
                + ", ".join(missing)
                + ". Configura el conector en Settings → Conectores."
            )
        return cls(
            tenant_id=os.environ[f"{ENV_PREFIX}TENANT_ID"],
            client_id=os.environ[f"{ENV_PREFIX}CLIENT_ID"],
            client_secret=os.environ[f"{ENV_PREFIX}CLIENT_SECRET"],
            connect_timeout=int(os.environ.get(f"{ENV_PREFIX}CONNECT_TIMEOUT", "10")),
        )
