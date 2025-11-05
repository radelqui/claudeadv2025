# 🖥️ SETUP LOCAL CON METATRADER 5

Guía completa para ejecutar el bot en tu computadora local conectado a MetaTrader 5.

---

## ⚠️ **REQUISITOS PREVIOS**

### 1. **Sistema Operativo**
- ✅ **Windows 10/11** (MetaTrader 5 solo funciona en Windows)
- ❌ MacOS/Linux no soportados directamente (necesitas Wine o VM)

### 2. **MetaTrader 5**
- ✅ MT5 instalado y funcionando
- ✅ Cuenta demo/real configurada
- ✅ MT5 debe estar **ABIERTO** mientras el bot corre

### 3. **Python**
- ✅ Python 3.8 o superior
- ✅ pip (gestor de paquetes)

### 4. **Tu Cuenta MT5** (ya la tienes)
```yaml
Cuenta:   206895
Password: Xpuerta08!
Servidor: FusionMarkets_demo
```

---

## 📦 **PASO 1: INSTALAR METATRADER 5**

### Si no tienes MT5 instalado:

1. **Descargar MT5:**
   - Ve a: https://www.metatrader5.com/en/download
   - O descarga desde tu broker (FusionMarkets)

2. **Instalar:**
   - Ejecuta el instalador
   - Sigue las instrucciones
   - Instala en la ruta predeterminada

3. **Configurar tu cuenta:**
   ```
   Cuenta:   206895
   Password: Xpuerta08!
   Servidor: FusionMarkets_demo
   ```

4. **Verificar:**
   - Abre MT5
   - Ve a Tools → Options → Trade
   - Verifica que "Allow automated trading" esté ✅ ACTIVADO
   - Verifica que "Allow DLL imports" esté ✅ ACTIVADO

---

## 🐍 **PASO 2: INSTALAR PYTHON**

### Si no tienes Python:

1. **Descargar Python:**
   - Ve a: https://www.python.org/downloads/
   - Descarga Python 3.11 o 3.10

2. **Instalar:**
   - ✅ **IMPORTANTE:** Marca "Add Python to PATH"
   - Instala con opciones predeterminadas

3. **Verificar instalación:**
   ```bash
   python --version
   # Debe mostrar: Python 3.x.x

   pip --version
   # Debe mostrar: pip 23.x.x
   ```

---

## 📥 **PASO 3: CLONAR EL REPOSITORIO**

```bash
# Abrir PowerShell o CMD

# Clonar
git clone https://github.com/radelqui/claudeadv2025.git
cd claudeadv2025

# Cambiar al branch correcto
git checkout claude/optimize-trading-bot-011CUoo5yY4Ufe7WcLwD6VPe
```

---

## 📚 **PASO 4: INSTALAR DEPENDENCIAS**

```bash
# En el directorio claudeadv2025/

pip install -r requirements_local.txt
```

### Dependencias que se instalarán:

```
MetaTrader5>=5.0.45    ⭐ CRÍTICO para MT5
yfinance>=0.2.28       Datos históricos
pandas>=2.0.0          Análisis de datos
numpy>=1.24.0          Cálculos numéricos
requests>=2.31.0       API Telegram
scipy>=1.10.0          Estadísticas
pyyaml>=6.0            Config files
```

### ⚠️ **Si da error instalando MetaTrader5:**

```bash
# Opción 1: Instalar directamente
pip install MetaTrader5

# Opción 2: Desde archivo wheel
pip install --upgrade pip
pip install MetaTrader5 --no-cache-dir

# Opción 3: Si persiste el error
pip install --upgrade --force-reinstall MetaTrader5
```

---

## ⚙️ **PASO 5: CONFIGURAR EL BOT**

### Editar `mt5_config.yaml`:

```yaml
mt5:
  account: 206895
  password: "Xpuerta08!"
  server: "FusionMarkets_demo"
  risk_per_trade_pct: 1.0  # 1% riesgo por trade

execution:
  mode: "mt5"  # Usar MT5 real

environment:
  is_demo: true  # true = demo, false = real
```

### Configurar Telegram (opcional pero recomendado):

Editar `config.py`:
```python
TELEGRAM_TOKEN = "tu_token_aqui"
CHAT_ID = "tu_chat_id_aqui"
```

Para obtener token:
1. Buscar `@BotFather` en Telegram
2. Enviar `/newbot`
3. Copiar token

Para obtener Chat ID:
1. Buscar `@userinfobot` en Telegram
2. Copiar tu ID

---

## 🧪 **PASO 6: PROBAR LA CONEXIÓN**

### Test 1: Verificar MT5

```bash
python mt5_connector.py
```

**Deberías ver:**
```
======================================================================
TEST DE CONEXIÓN MT5
======================================================================

🔌 Conectando a MT5...

✅ CONECTADO A MT5

Cuenta:   206895
Broker:   Fusion Markets
Servidor: FusionMarkets_demo
Balance:  $10,000.00
Equity:   $10,000.00
Modo:     DEMO

📊 Información de cuenta:
  login: 206895
  balance: 10000.0
  ...

✅ Test completado
```

**Si da error:**
- ❌ "MT5 initialize() falló" → MT5 no está abierto o instalado
- ❌ "Login falló" → Credenciales incorrectas
- ❌ "No module named 'MetaTrader5'" → Instalar: `pip install MetaTrader5`

---

## 🚀 **PASO 7: EJECUTAR EL BOT**

### Opción A: Modo DEMO (Recomendado para empezar)

```bash
python claude_advanced_bot_mt5.py --mode demo
```

### Opción B: Modo PAPER (Sin conectar MT5, solo simulación)

```bash
python claude_advanced_bot.py --paper
```

### Opción C: Modo REAL (Solo después de probar MUCHO en demo)

1. Editar `mt5_config.yaml`:
   ```yaml
   environment:
     is_demo: false  # CAMBIAR A FALSE
     confirm_real_trading: true
   ```

2. Ejecutar:
   ```bash
   python claude_advanced_bot_mt5.py --mode real
   ```

3. El bot pedirá confirmación:
   ```
   ⚠️  ADVERTENCIA: Modo REAL activado
   ¿Estás seguro? (yes/no):
   ```

---

## 📊 **MONITOREO EN TIEMPO REAL**

### El bot mostrará:

```
======================================================================
CLAUDE ADVANCED BOT MT5 - INICIANDO
======================================================================

✅ Conectado a MT5
   Cuenta: 206895
   Balance: $10,000.00
   Modo: DEMO

⚙️  Configuración:
   Riesgo por trade: 1.0%
   Max posiciones: 3
   Kelly Criterion: Activo
   ADX Detection: Activo
   ATR Stops: Activo

======================================================================
CICLO #1 - 2025-11-05 18:30:00
======================================================================

💰 Capital: $10,000.00 | Trades hoy: 0 | PnL: $0.00

🔍 Analizando EUR/USD...
  Mercado: trending - ADX: 32.5
  ✓ Multi-TF: BUY (75%)
  ✓ Trend Following: BUY (80%)

🎯 SEÑAL CONFIRMADA: EUR/USD BUY
  Confianza: 77.5%
  Entry: 1.08450
  SL: 1.08250 (20 pips)
  TP: 1.08950 (50 pips)
  Lot size: 0.02 lotes

📈 Ejecutando trade en MT5...
✅ Trade abierto: Ticket #12345

⏳ Esperando 5 minutos...
```

### Y en Telegram recibirás:

```
🎯 TRADE EJECUTADO

📊 Par: EUR/USD
📈 Dirección: BUY
🎫 Ticket: #12345
💰 Entrada: 1.08450
🛡️ SL: 1.08250
🎯 TP: 1.08950
💼 Lotes: 0.02

Capital: $10,000.00
⏰ 18:30:15
```

---

## 🛡️ **SEGURIDAD Y PROTECCIONES**

### El bot incluye:

✅ **Max Daily Loss:** Para si pérdida diaria > 5%
✅ **Max Drawdown:** Para si drawdown > 20%
✅ **Max Positions:** Máximo 3 posiciones abiertas
✅ **Spread Check:** No tradea si spread > 5 pips
✅ **Margin Check:** Verifica margin level > 200%
✅ **Trailing Stops:** Protege ganancias automáticamente

### Cómo detener el bot:

```bash
Ctrl + C  # En la terminal

# El bot cerrará ordenadamente:
🛑 Bot detenido por usuario
📊 Cerrando posiciones abiertas...
✅ Bot cerrado correctamente
```

---

## 📁 **ESTRUCTURA DE ARCHIVOS**

```
claudeadv2025/
├── claude_advanced_bot_mt5.py   ⭐ Bot principal con MT5
├── mt5_connector.py              ⭐ Conector MT5
├── mt5_config.yaml               ⭐ Configuración MT5
├── config.py                      Configuración general
├── indicators.py                  Indicadores técnicos
├── market_conditions.py           Detección de mercado
├── risk_management.py             Gestión de riesgo
├── backtest.py                    Sistema de backtesting
├── requirements_local.txt        ⭐ Dependencias locales
├── SETUP_LOCAL_MT5.md            ⭐ Esta guía
└── README.md                      Documentación general
```

---

## ❓ **SOLUCIÓN DE PROBLEMAS**

### Error: "No module named 'MetaTrader5'"
```bash
pip install MetaTrader5
```

### Error: "MT5 initialize() failed"
- ✅ Abrir MetaTrader 5
- ✅ Verificar que esté logueado
- ✅ Tools → Options → Expert Advisors → Allow automated trading

### Error: "Login failed"
- ✅ Verificar cuenta: 206895
- ✅ Verificar password: Xpuerta08!
- ✅ Verificar servidor: FusionMarkets_demo
- ✅ En MT5: File → Login to Trade Account

### Error: "Symbol EURUSD not found"
- ✅ En MT5: View → Market Watch
- ✅ Click derecho → Show All
- ✅ Buscar EURUSD y activar

### Bot no genera señales
- ✅ Normal en mercados sin oportunidades
- ✅ Verificar ADX > 20 (mercado debe ser tradeable)
- ✅ Requiere consenso de 2+ estrategias

### Slippage alto
- ✅ Normal en alta volatilidad
- ✅ Configurar en mt5_config.yaml:
  ```yaml
  slippage_points: 20  # Aumentar a 20 points
  ```

---

## 📊 **MONITOREAR PERFORMANCE**

### Archivos generados:

```
mt5_trades.csv          Historial de todos los trades
trading_bot.log         Log completo del bot
bot_state.json          Estado actual del bot
performance_metrics.json Métricas de performance
```

### Ver métricas en tiempo real:

```bash
# En otra terminal/PowerShell
python view_performance.py
```

---

## 🎯 **MEJORES PRÁCTICAS**

### 1. **Siempre empezar en DEMO**
```yaml
environment:
  is_demo: true  # SIEMPRE true al inicio
```

### 2. **Probar al menos 2-3 semanas en demo**
- Verificar que win rate ≈ 60%
- Verificar que drawdown < 15%
- Verificar que no hay errores

### 3. **Empezar con riesgo bajo en real**
```yaml
mt5:
  risk_per_trade_pct: 0.5  # 0.5% en vez de 1%
```

### 4. **Monitorear diariamente**
- Revisar alertas Telegram
- Verificar trades en MT5
- Controlar drawdown

### 5. **No modificar durante trading activo**
- Si quieres cambiar config, espera a cerrar todas las posiciones
- O detén el bot, modifica, y reinicia

---

## ✅ **CHECKLIST ANTES DE EMPEZAR**

```
[ ] Windows 10/11 instalado
[ ] MetaTrader 5 instalado y funcionando
[ ] Cuenta demo configurada (206895)
[ ] MT5 abierto y logueado
[ ] Automated trading activado en MT5
[ ] Python 3.8+ instalado
[ ] pip funcionando
[ ] Repositorio clonado
[ ] Branch correcto checked out
[ ] Dependencias instaladas (pip install -r requirements_local.txt)
[ ] MetaTrader5 library instalada
[ ] mt5_config.yaml configurado
[ ] Test de conexión OK (python mt5_connector.py)
[ ] Telegram configurado (opcional)
[ ] mt5_config.yaml: is_demo = true
```

**Cuando TODOS los checks estén ✅, ejecuta:**
```bash
python claude_advanced_bot_mt5.py --mode demo
```

---

## 🆘 **SOPORTE**

Si tienes problemas:

1. **Revisar logs:**
   ```bash
   type trading_bot.log  # Windows CMD
   cat trading_bot.log   # PowerShell
   ```

2. **Test individual:**
   ```bash
   python mt5_connector.py   # Test conexión
   python indicators.py      # Test indicadores
   python config.py          # Test config
   ```

3. **GitHub Issues:**
   https://github.com/radelqui/claudeadv2025/issues

---

## 🎉 **¡LISTO!**

Cuando todo funcione, verás:

```
✅ MT5 conectado
✅ Estrategias cargadas
✅ Bot monitoreando mercados
✅ Trades ejecutándose automáticamente
✅ Telegram notificando en tiempo real
```

**¡Tu bot está operando profesionalmente en MetaTrader 5!** 🚀

---

**Última actualización:** 2025-11-05
**Versión:** 2.0 MT5 Integration
