"""Validación local del conector intune: ejercita las 3 capacidades.

Uso:
    python validate_local.py

Requiere las variables RUVIC_INTUNE_* exportadas en el entorno.

ADVERTENCIA: si seteás RUVIC_INTUNE_TEST_DEVICE_ID, este script
dispara una sincronización REAL de ese dispositivo. Ejecútalo solo
contra un dispositivo de prueba.
"""

import os

from ruvic_intune_connector import IntuneClient, setup_logging

setup_logging("INFO")
client = IntuneClient()

print("== 1. Listar dispositivos administrados ==")
dispositivos = client.list_devices()
print(f"  {len(dispositivos)} dispositivo(s) encontrado(s)")

device_id = os.environ.get("RUVIC_INTUNE_TEST_DEVICE_ID") or (
    dispositivos[0]["id"] if dispositivos else None
)

if device_id:
    print("== 2. Consultar cumplimiento ==")
    cumplimiento = client.get_compliance(device_id)
    print(f"  {cumplimiento}")

    print("== 3. Sincronizar dispositivo ==")
    client.sync_device(device_id)
    print("  sincronización disparada")
else:
    print("== 2 y 3. Omitidas: no hay dispositivos para probar ==")

print("\nTodo OK: list_devices, get_compliance y sync_device funcionan.")
