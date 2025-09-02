# claude_love_turbo.py
"""
🚀 CLAUDE LOVE TURBO - Versión Rápida Funcional
Listo para ejecutar INMEDIATAMENTE
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
import json
import time
from datetime import datetime, timedelta
import warnings
import talib
from typing import Dict, List, Tuple, Optional
warnings.filterwarnings('ignore')

# =======================
# CONFIGURACIÓN RÁPIDA
# =======================
TELEGRAM_TOKEN = "7718630865:AAEMclwlqzuxb5uFPqX9dyJLo7ib19QnJt8"
CHAT_ID = "5358902915"

# Pares a operar
PARES = {
    'EURUSD=X': {'nombre': 'EUR/USD', 'pip_value': 0.0001},
    'USDJPY=X': {'nombre': 'USD/JPY', 'pip_value': 0.01},
    'GC=F': {'nombre': 'GOLD', 'pip_value': 0.1}
}

# Números Fibonacci maestros
FIBONACCI = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]
FIBONACCI_MINUTES = [3, 5, 8, 13, 21, 34, 55]

# =======================
# CLASE PRINCIPAL
# =======================
class ClaudeLoveTurbo:
    def __init__(self):
        self.nombre = "🤖 CLAUDE LOVE TURBO"
        self.trades_hoy = 0
        self.max_trades = 3
        self.confianza_minima = 0.75
        self.gaps_detectados = []
        self.zonas_actuales = {}
        self.señales_enviadas = []
        
        print(f"\n{'='*50}")
        print(f"{self.nombre} - INICIANDO")
        print(f"{'='*50}")
        self.enviar_telegram(f"{self.nombre} ACTIVADO 🚀\n⚡ Sistema rápido iniciado")
    
    def enviar_telegram(self, mensaje):
        """Envía alertas a Telegram"""
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            response = requests.post(url, json={
                'chat_id': CHAT_ID,
                'text': mensaje,
                'parse_mode': 'HTML'
            })
            return response.ok
        except:
            return False
    
    def obtener_datos(self, symbol, period='2d', interval='1m'):
        """Obtiene datos de Yahoo Finance"""
        try:
            data = yf.download(symbol, period=period, interval=interval, progress=False)
            if not data.empty:
                return data
        except Exception as e:
            print(f"❌ Error obteniendo datos: {e}")
        return None
    
    def detectar_gaps(self, data, symbol):
        """Detecta gaps de liquidez que no vuelven"""
        gaps = []
        pip_value = PARES[symbol]['pip_value']
        
        for i in range(1, min(len(data), 100)):  # Últimas 100 velas
            open_price = data['Open'].iloc[i]
            prev_close = data['Close'].iloc[i-1]
            
            gap_size = abs(open_price - prev_close)
            gap_pips = gap_size / pip_value
            
            if gap_pips >= 0.5:  # Mínimo 0.5 pips
                # Verificar si el gap no se rellenó (mirar 20 velas adelante)
                no_relleno = True
                for j in range(i, min(i+20, len(data))):
                    if open_price > prev_close:  # Gap alcista
                        if data['Low'].iloc[j] <= prev_close:
                            no_relleno = False
                            break
                    else:  # Gap bajista
                        if data['High'].iloc[j] >= prev_close:
                            no_relleno = False
                            break
                
                if no_relleno:
                    gaps.append({
                        'tipo': 'bullish' if open_price > prev_close else 'bearish',
                        'precio': open_price,
                        'pips': gap_pips,
                        'tiempo': data.index[i],
                        'no_retorno': True
                    })
        
        return gaps
    
    def calcular_zonas_premium_discount(self, data):
        """Calcula zonas Premium/Discount y detecta zona media"""
        high_50 = data['High'].rolling(50).max().iloc[-1]
        low_50 = data['Low'].rolling(50).min().iloc[-1]
        
        premium = high_50
        discount = low_50
        equilibrium = (premium + discount) / 2
        
        # Zona Atrapa (20% alrededor del equilibrio) - NO OPERAR
        zona_atrapa_superior = equilibrium + (premium - equilibrium) * 0.2
        zona_atrapa_inferior = equilibrium - (equilibrium - discount) * 0.2
        
        precio_actual = data['Close'].iloc[-1]
        
        # Determinar posición
        if precio_actual > zona_atrapa_superior:
            zona = "PREMIUM"
        elif precio_actual < zona_atrapa_inferior:
            zona = "DISCOUNT"
        else:
            zona = "ZONA_ATRAPA"
        
        return {
            'premium': premium,
            'discount': discount,
            'equilibrium': equilibrium,
            'zona_actual': zona,
            'precio': precio_actual,
            'es_extremo': zona in ['PREMIUM', 'DISCOUNT']
        }
    
    def calcular_alma(self, data, window=9):
        """Calcula ALMA simplificado"""
        if len(data) < window:
            return None
        
        close = data['Close'].values[-window:]
        m = 0.85 * (window - 1)
        s = window / 6.0
        
        w = np.exp(-((np.arange(window) - m) ** 2) / (2 * s ** 2))
        w = w / w.sum()
        
        return np.sum(close * w)
    
    def calcular_donchian(self, data, period=12):
        """Calcula Donchian Channel"""
        if len(data) < period:
            return None, None, None
        
        upper = data['High'].rolling(period).max().iloc[-1]
        lower = data['Low'].rolling(period).min().iloc[-1]
        middle = (upper + lower) / 2
        
        return upper, middle, lower
    
    def detectar_mecha_55(self, data):
        """Detecta velas con 55% o más fuera de Bollinger Bands"""
        if len(data) < 20:
            return False
        
        # Bollinger Bands
        sma = data['Close'].rolling(20).mean()
        std = data['Close'].rolling(20).std()
        upper_band = sma + (2 * std)
        lower_band = sma - (2 * std)
        
        ultima_vela = data.iloc[-1]
        high = ultima_vela['High']
        low = ultima_vela['Low']
        
        # Calcular % de mecha fuera
        if low < lower_band.iloc[-1]:
            mecha_fuera = (lower_band.iloc[-1] - low) / (high - low)
            if mecha_fuera >= 0.55:
                return 'bullish'
        
        if high > upper_band.iloc[-1]:
            mecha_fuera = (high - upper_band.iloc[-1]) / (high - low)
            if mecha_fuera >= 0.55:
                return 'bearish'
        
        return False
    
    def es_tiempo_fibonacci(self):
        """Verifica si estamos en minuto Fibonacci"""
        minuto_actual = datetime.now().minute
        return minuto_actual in FIBONACCI_MINUTES
    
    def calcular_correlaciones(self):
        """Calcula correlaciones simples entre pares"""
        correlaciones = {}
        
        try:
            # Obtener datos de todos los pares
            datos = {}
            for symbol in PARES.keys():
                data = self.obtener_datos(symbol, period='5d', interval='1h')
                if data is not None:
                    datos[symbol] = data['Close']
            
            # Calcular correlación
            if len(datos) >= 2:
                df = pd.DataFrame(datos)
                corr_matrix = df.corr()
                
                # Verificar si hay alta correlación
                for i, sym1 in enumerate(df.columns):
                    for j, sym2 in enumerate(df.columns):
                        if i < j:
                            correlaciones[f"{sym1}-{sym2}"] = corr_matrix.iloc[i, j]
            
        except:
            pass
        
        return correlaciones
    
    def analizar_confluencias(self, symbol, data):
        """Analiza todas las confluencias para una señal"""
        confluencias = []
        puntuaje = 0
        
        # 1. Detectar Gaps
        gaps = self.detectar_gaps(data, symbol)
        if gaps:
            gap_reciente = gaps[-1] if gaps else None
            if gap_reciente and gap_reciente['no_retorno']:
                confluencias.append(f"🔥 Gap no retorno {gap_reciente['tipo']}")
                puntuaje += 25
        
        # 2. Zonas Premium/Discount
        zonas = self.calcular_zonas_premium_discount(data)
        self.zonas_actuales[symbol] = zonas
        
        if zonas['es_extremo']:
            confluencias.append(f"📍 Zona {zonas['zona_actual']}")
            puntuaje += 20
        elif zonas['zona_actual'] == 'ZONA_ATRAPA':
            return None, []  # NO OPERAR EN ZONA MEDIA
        
        # 3. ALMA vs Donchian
        alma = self.calcular_alma(data)
        upper, middle, lower = self.calcular_donchian(data)
        
        if alma and middle:
            if alma > middle and zonas['zona_actual'] == 'DISCOUNT':
                confluencias.append("✅ ALMA > Donchian (BUY)")
                puntuaje += 20
            elif alma < middle and zonas['zona_actual'] == 'PREMIUM':
                confluencias.append("✅ ALMA < Donchian (SELL)")
                puntuaje += 20
        
        # 4. Mecha 55%
        mecha = self.detectar_mecha_55(data)
        if mecha:
            confluencias.append(f"🎯 Mecha 55% {mecha}")
            puntuaje += 15
        
        # 5. Timing Fibonacci
        if self.es_tiempo_fibonacci():
            confluencias.append(f"⏰ Minuto Fibonacci {datetime.now().minute}")
            puntuaje += 10
        
        # 6. RSI extremo
        if len(data) >= 14:
            rsi = talib.RSI(data['Close'].values, timeperiod=14)[-1]
            if rsi < 30 and zonas['zona_actual'] == 'DISCOUNT':
                confluencias.append(f"📊 RSI oversold ({rsi:.1f})")
                puntuaje += 10
            elif rsi > 70 and zonas['zona_actual'] == 'PREMIUM':
                confluencias.append(f"📊 RSI overbought ({rsi:.1f})")
                puntuaje += 10
        
        # Determinar dirección
        direccion = None
        if puntuaje >= 60:  # Umbral de confianza
            if zonas['zona_actual'] == 'DISCOUNT' and (not mecha or mecha == 'bullish'):
                direccion = 'BUY'
            elif zonas['zona_actual'] == 'PREMIUM' and (not mecha or mecha == 'bearish'):
                direccion = 'SELL'
        
        return direccion, confluencias, puntuaje
    
    def calcular_sl_tp(self, direccion, precio, symbol, zonas):
        """Calcula Stop Loss y Take Profit inteligentes"""
        pip_value = PARES[symbol]['pip_value']
        
        if direccion == 'BUY':
            # SL debajo del discount o -20 pips
            sl = min(zonas['discount'], precio - (20 * pip_value))
            # TP en premium o +40 pips
            tp = max(zonas['premium'], precio + (40 * pip_value))
        else:
            # SL arriba del premium o +20 pips
            sl = max(zonas['premium'], precio + (20 * pip_value))
            # TP en discount o -40 pips
            tp = min(zonas['discount'], precio - (40 * pip_value))
        
        return sl, tp
    
    def ejecutar_analisis(self):
        """Ejecuta análisis completo para todos los pares"""
        print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Analizando mercados...")
        
        if self.trades_hoy >= self.max_trades:
            print("✋ Límite diario alcanzado")
            return
        
        # Calcular correlaciones
        correlaciones = self.calcular_correlaciones()
        
        mejores_señales = []
        
        for symbol, info in PARES.items():
            print(f"\n📊 Analizando {info['nombre']}...")
            
            # Obtener datos
            data = self.obtener_datos(symbol, period='1d', interval='1m')
            if data is None or len(data) < 100:
                print(f"  ❌ Datos insuficientes")
                continue
            
            # Analizar confluencias
            resultado = self.analizar_confluencias(symbol, data)
            if resultado is None:
                continue
                
            direccion, confluencias, puntuaje = resultado
            
            if direccion and puntuaje >= 60:
                precio = data['Close'].iloc[-1]
                sl, tp = self.calcular_sl_tp(direccion, precio, symbol, self.zonas_actuales[symbol])
                
                señal = {
                    'symbol': symbol,
                    'nombre': info['nombre'],
                    'direccion': direccion,
                    'precio': precio,
                    'sl': sl,
                    'tp': tp,
                    'confluencias': confluencias,
                    'puntuaje': puntuaje,
                    'tiempo': datetime.now()
                }
                
                mejores_señales.append(señal)
                print(f"  ✅ SEÑAL DETECTADA: {direccion} - Confianza: {puntuaje}%")
                for conf in confluencias:
                    print(f"    {conf}")
        
        # Seleccionar mejor señal
        if mejores_señales:
            mejor = max(mejores_señales, key=lambda x: x['puntuaje'])
            self.enviar_señal(mejor)
    
    def enviar_señal(self, señal):
        """Envía señal a Telegram"""
        # Evitar duplicados
        señal_id = f"{señal['symbol']}-{señal['direccion']}-{datetime.now().hour}"
        if señal_id in self.señales_enviadas:
            return
        
        self.señales_enviadas.append(señal_id)
        self.trades_hoy += 1
        
        # Calcular R:R ratio
        pips_sl = abs(señal['precio'] - señal['sl']) / PARES[señal['symbol']]['pip_value']
        pips_tp = abs(señal['tp'] - señal['precio']) / PARES[señal['symbol']]['pip_value']
        rr_ratio = pips_tp / pips_sl if pips_sl > 0 else 0
        
        mensaje = f"""
🚀 <b>SEÑAL CLAUDE LOVE</b>

📊 <b>Par:</b> {señal['nombre']}
🎯 <b>Dirección:</b> {señal['direccion']}
💰 <b>Precio:</b> {señal['precio']:.5f}
🛡 <b>Stop Loss:</b> {señal['sl']:.5f} ({pips_sl:.1f} pips)
🎯 <b>Take Profit:</b> {señal['tp']:.5f} ({pips_tp:.1f} pips)
📈 <b>R:R Ratio:</b> 1:{rr_ratio:.1f}

<b>📍 Confluencias ({señal['puntuaje']}%):</b>
{chr(10).join(señal['confluencias'])}

⏰ {datetime.now().strftime('%H:%M:%S')}
🔢 Trade {self.trades_hoy}/{self.max_trades} del día
"""
        
        self.enviar_telegram(mensaje)
        print(f"\n📤 SEÑAL ENVIADA: {señal['nombre']} - {señal['direccion']}")
    
    def run(self):
        """Ejecuta el bot continuamente"""
        print(f"\n🚀 {self.nombre} corriendo...")
        print("Presiona Ctrl+C para detener\n")
        
        while True:
            try:
                # Reset diario a medianoche
                if datetime.now().hour == 0 and datetime.now().minute == 0:
                    self.trades_hoy = 0
                    self.señales_enviadas = []
                    print("🔄 Reset diario completado")
                
                # Ejecutar análisis
                self.ejecutar_analisis()
                
                # Esperar 60 segundos
                time.sleep(60)
                
            except KeyboardInterrupt:
                print("\n👋 Claude Love detenido")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(60)

# =======================
# EJECUCIÓN
# =======================
if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════╗
    ║       CLAUDE LOVE TURBO v1.0         ║
    ║   Sistema de Trading Cuántico IA     ║
    ╚═══════════════════════════════════════╝
    """)
    
    bot = ClaudeLoveTurbo()
    bot.run()
