---
name: intune
description: Listar dispositivos de Microsoft Intune, consultar su cumplimiento y disparar una sincronización remota
---

# Microsoft Intune

Conector de gestión de dispositivos en Microsoft Intune vía
Microsoft Graph.

## Credenciales

Usa un Service Principal de Azure AD (`tenant_id`, `client_id`,
`client_secret`) autenticado vía `azure-identity.ClientSecretCredential`
contra el scope `https://graph.microsoft.com/.default`. Nunca
hardcodees ni loguees el `client_secret`. El Service Principal debe
tener el permiso de aplicación
`DeviceManagementManagedDevices.ReadWrite.All` con consentimiento de
administrador.

## Capacidades

### `list_devices() -> list[dict]`

Lista los dispositivos administrados por Intune (id, deviceName,
operatingSystem, complianceState). Solo lectura.

```python
dispositivos = client.list_devices()
```

### `get_compliance(device_id: str) -> dict`

Consulta el estado de cumplimiento de un dispositivo específico.
Solo lectura.

```python
estado = client.get_compliance("device-id")
```

### `sync_device(device_id: str) -> None`

Dispara una sincronización remota real del dispositivo con Intune.

```python
client.sync_device("device-id")
```

## Manejo de errores

Todas las excepciones heredan de `IntuneConnectorError`:

- `IntuneAuthError`: credenciales inválidas o falta el permiso de
  Graph necesario.
- `IntuneNetworkError`: Microsoft Graph inalcanzable, timeout de red.
- `IntuneDataError`: dispositivo inexistente u otro error de datos.

Nunca dejes propagar excepciones crudas de `requests` o
`azure.core.exceptions.*` — siempre se traducen a estas.

## Buenas prácticas

- Tratá `sync_device` como una acción con efecto real sobre el
  dispositivo del usuario final; no la dispares en bucle ni contra
  todos los dispositivos sin confirmar con el usuario.
- `list_devices` y `get_compliance` son seguras de ejecutar
  libremente (solo lectura).
- Si el usuario pide "sincronizar todos los dispositivos", confirmá
  el alcance antes de iterar `sync_device` sobre la lista completa.
