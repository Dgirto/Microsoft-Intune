# Conector Microsoft Intune (CON-074)

Conector Ruvic de gestión de dispositivos en Microsoft Intune vía
Microsoft Graph. Permite listar dispositivos administrados, consultar
el estado de cumplimiento de un dispositivo, y disparar una
sincronización remota.

## Instalación

```bash
pip install git+https://github.com/Dgirto/Microsoft-Intune.git#subdirectory=lib
```

Python 3.10+. Dependencias: `azure-identity`, `requests`.

## Permisos requeridos en Azure AD / Microsoft Graph

Registrá un **Service Principal dedicado** (App registration) y
otorgale el permiso de **aplicación** de Microsoft Graph:

- **`DeviceManagementManagedDevices.ReadWrite.All`**: necesario para
  las 3 operaciones (listar, consultar cumplimiento y sincronizar).

Este permiso requiere **consentimiento de administrador** (admin
consent) en el tenant. No otorgues permisos de administración de
políticas de configuración ni de cumplimiento (`DeviceManagementConfiguration.*`,
`DeviceManagementServiceConfig.*`).

## Variables de entorno (`RUVIC_INTUNE_*`)

| Variable | Obligatoria | Descripción |
|----------|-------------|-------------|
| `RUVIC_INTUNE_TENANT_ID` | Sí | Tenant ID de Azure AD |
| `RUVIC_INTUNE_CLIENT_ID` | Sí | Client ID del Service Principal |
| `RUVIC_INTUNE_CLIENT_SECRET` | Sí | Client Secret del Service Principal |
| `RUVIC_INTUNE_CONNECT_TIMEOUT` | No (default `10`) | Timeout de conexión en segundos |

## Pruebas locales

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ./lib

export RUVIC_INTUNE_TENANT_ID=tu-tenant-id
export RUVIC_INTUNE_CLIENT_ID=tu-client-id
export RUVIC_INTUNE_CLIENT_SECRET=tu-client-secret

python test_connection.py
python validate_local.py
```

Para acotar la prueba a un dispositivo específico, exportá
`RUVIC_INTUNE_TEST_DEVICE_ID`; si no se define, `validate_local.py`
usa el primer dispositivo listado.

## Notas de integración

- `list_devices` y `get_compliance` son de **solo lectura**.
  `sync_device` **SÍ dispara una acción real** sobre el dispositivo
  (una sincronización con el servicio de Intune) — no hay modo
  dry-run.
- La autenticación usa `azure-identity.ClientSecretCredential` contra
  el scope `https://graph.microsoft.com/.default` (client credentials
  flow), no requiere delegación de usuario.
- `sync_device` no bloquea a la espera de que la sincronización
  termine; solo dispara la solicitud (comportamiento estándar de la
  API de Graph).
