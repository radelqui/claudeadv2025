"""
VERIFICACIÓN COMPLETA DEL SETUP LOCAL
======================================
Verifica que TODO esté instalado y configurado correctamente
"""

import sys
import subprocess
from datetime import datetime

print("=" * 70)
print("VERIFICACIÓN DE SETUP LOCAL - CLAUDE ADVANCED BOT MT5")
print("=" * 70)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

errors = []
warnings = []
success = []

# ============================================================================
# 1. VERIFICAR PYTHON
# ============================================================================

print("[1/7] Verificando Python...")
try:
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.patch}"

    if version.major == 3 and version.minor >= 8:
        success.append(f"✅ Python {version_str} (OK)")
    else:
        errors.append(f"❌ Python {version_str} (Requiere 3.8+)")
except Exception as e:
    errors.append(f"❌ Error verificando Python: {e}")

# ============================================================================
# 2. VERIFICAR PIP
# ============================================================================

print("[2/7] Verificando pip...")
try:
    result = subprocess.run([sys.executable, "-m", "pip", "--version"],
                          capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        success.append("✅ pip instalado (OK)")
    else:
        errors.append("❌ pip no funciona correctamente")
except Exception as e:
    errors.append(f"❌ Error verificando pip: {e}")

# ============================================================================
# 3. VERIFICAR LIBRERÍAS CRÍTICAS
# ============================================================================

print("[3/7] Verificando librerías Python...")

required_libs = {
    'MetaTrader5': 'MetaTrader5',
    'pandas': 'pandas',
    'numpy': 'numpy',
    'yfinance': 'yfinance',
    'requests': 'requests',
    'yaml': 'pyyaml'
}

for import_name, pip_name in required_libs.items():
    try:
        __import__(import_name)
        success.append(f"✅ {pip_name} instalado (OK)")
    except ImportError:
        errors.append(f"❌ {pip_name} NO instalado - Ejecutar: pip install {pip_name}")

# ============================================================================
# 4. VERIFICAR METATRADER 5
# ============================================================================

print("[4/7] Verificando MetaTrader 5...")
try:
    import MetaTrader5 as mt5

    if mt5.initialize():
        version = mt5.version()
        success.append(f"✅ MT5 instalado y funcionando - Versión: {version}")

        # Verificar cuenta
        account_info = mt5.account_info()
        if account_info:
            success.append(f"✅ MT5 cuenta activa: {account_info.login}")
            success.append(f"✅ Balance: ${account_info.balance:.2f}")
            success.append(f"✅ Modo: {'DEMO' if account_info.trade_mode == 0 else 'REAL'}")
        else:
            warnings.append("⚠️  MT5 abierto pero sin cuenta logueada")

        mt5.shutdown()
    else:
        errors.append("❌ MT5 no está abierto o no funciona correctamente")
        errors.append("   → Abre MetaTrader 5 y loguea tu cuenta")

except ImportError:
    errors.append("❌ Librería MetaTrader5 NO instalada")
    errors.append("   → Ejecutar: pip install MetaTrader5")
except Exception as e:
    errors.append(f"❌ Error con MT5: {e}")

# ============================================================================
# 5. VERIFICAR ARCHIVOS DEL BOT
# ============================================================================

print("[5/7] Verificando archivos del bot...")

required_files = [
    'config.py',
    'indicators.py',
    'market_conditions.py',
    'risk_management.py',
    'mt5_connector.py',
    'mt5_config.yaml',
    'backtest.py'
]

import os
for filename in required_files:
    if os.path.exists(filename):
        success.append(f"✅ {filename} encontrado")
    else:
        errors.append(f"❌ {filename} NO encontrado")

# ============================================================================
# 6. VERIFICAR CONFIGURACIÓN
# ============================================================================

print("[6/7] Verificando configuración...")
try:
    from config import validate_config

    if validate_config():
        success.append("✅ config.py es válido")
    else:
        errors.append("❌ config.py tiene errores")
except Exception as e:
    errors.append(f"❌ Error cargando config.py: {e}")

# Verificar mt5_config.yaml
try:
    import yaml
    with open('mt5_config.yaml', 'r') as f:
        mt5_config = yaml.safe_load(f)

    if mt5_config and 'mt5' in mt5_config:
        success.append("✅ mt5_config.yaml es válido")

        # Verificar credenciales
        account = mt5_config['mt5'].get('account')
        server = mt5_config['mt5'].get('server')

        if account == 206895:
            success.append(f"✅ Cuenta MT5 configurada: {account}")
        if server == "FusionMarkets_demo":
            success.append(f"✅ Servidor configurado: {server}")
    else:
        errors.append("❌ mt5_config.yaml mal formateado")

except FileNotFoundError:
    errors.append("❌ mt5_config.yaml NO encontrado")
except Exception as e:
    errors.append(f"❌ Error leyendo mt5_config.yaml: {e}")

# ============================================================================
# 7. TEST DE CONEXIÓN MT5
# ============================================================================

print("[7/7] Test de conexión MT5...")
try:
    from mt5_connector import MT5Connector

    connector = MT5Connector(
        account=206895,
        password="Xpuerta08!",
        server="FusionMarkets_demo"
    )

    connected, message = connector.connect()

    if connected:
        success.append("✅ CONEXIÓN MT5 EXITOSA")

        account_info = connector.get_account_info()
        if account_info:
            success.append(f"   Balance: ${account_info['balance']:.2f}")
            success.append(f"   Equity: ${account_info['equity']:.2f}")
            success.append(f"   Leverage: 1:{account_info['leverage']}")

        connector.disconnect()
    else:
        errors.append(f"❌ Conexión MT5 falló: {message}")

except Exception as e:
    errors.append(f"❌ Error en test MT5: {e}")

# ============================================================================
# REPORTE FINAL
# ============================================================================

print()
print("=" * 70)
print("REPORTE DE VERIFICACIÓN")
print("=" * 70)

print(f"\n✅ ÉXITOS: {len(success)}")
for item in success:
    print(f"   {item}")

if warnings:
    print(f"\n⚠️  ADVERTENCIAS: {len(warnings)}")
    for item in warnings:
        print(f"   {item}")

if errors:
    print(f"\n❌ ERRORES: {len(errors)}")
    for item in errors:
        print(f"   {item}")

print()
print("=" * 70)

if not errors:
    print("✅ SETUP COMPLETO - TODO LISTO PARA EJECUTAR EL BOT")
    print()
    print("Para ejecutar el bot:")
    print("  python claude_advanced_bot_mt5.py --mode demo")
    print()
elif len(errors) < 3:
    print("⚠️  CASI LISTO - Corrige los errores y vuelve a ejecutar:")
    print("  python verify_setup.py")
    print()
else:
    print("❌ SETUP INCOMPLETO - Sigue la guía SETUP_LOCAL_MT5.md")
    print()

print("=" * 70)

# Exit code
sys.exit(0 if not errors else 1)
