# claude_love.py
"""
🚀 CLAUDE LOVE - Versión Railway
Sin dependencias problemáticas, listo para deploy
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# =======================
# CONFIGURACIÓN
# =======================
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', "7718630865:AAEMclwlqzuxb5uFPqX9dyJLo7ib19QnJt8")
CHAT_ID = os.environ.get('CHAT_ID', "5358902915")

# Pares a operar
PARES = {
    'EURUSD=X': {'nombre': 'EUR/USD', 'pip_value': 0.0001},
    'USDJPY=X': {'nombre': 'USD/JPY', 'pip_value': 0.01},
    'GC=F': {'nombre': 'GOLD', 'pip_value': 0.1}
}

# Fibonacci
FIBONACCI_MINUTES = [3, 5, 8, 13, 21, 34, 55]

# =======================
# RSI MANUAL (sin talib)
# =======================
def calcular_rsi(data, period=14):
    """Calcula RSI sin usar talib"""
    close = data['Close']
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not rsi.empty else 50

# =======================
# CLASE PRINCIPAL
# =======================
class ClaudeLove:
    def __init__(self):
        self.nombre = "🤖 CLAUDE LOVE"
        self.trades_hoy = 0
        self.max_trades = 3
        self.gaps_detectados = []
        self.señales_enviadas = []
        
        print(f"\n{'='*50}")
        print(f"{self.nombre} - INICIANDO EN RAILWAY")
        print(f"{'='*50}")
        self.enviar_telegram(f"""
🚀 <b>CLAUDE LOVE ACTIVADO</b>

📊 Sistema funcionando en Railway
⚡ Detección de gaps activa
🎯 Máximo 3 trades/día
⏰ Fibonacci timing activado

<i>La Trinidad Sagrada está lista...</i>
""")
    
    def enviar_telegram(self, mensaje):
        """Envía alertas a Telegram"""
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            response = requests.post(url, json={
                'chat_id': CHAT_ID,
                'text': mensaje,
                'parse_mode': 'HTML'
            }, timeout=10)
            return response.ok
        except Exception as e:
            print(f"Error Telegram: {e}")
            return False
    
    def obtener_datos(self, symbol, period='2d', interval='1m'):
        """Obtiene datos de Yahoo Finance"""
        try:
            data = yf.download(
                symbol, 
                period=period, 
                interval=interval, 
                progress=False,
                auto_adjust=True,
                repair=True
            )
            if not data.empty:
                return data
        except Exception as e:
            print(f"Error obteniendo datos de {symbol}: {e}")
        return None
    
    def detectar_gaps(self, data, symbol):
        """Detecta gaps de liquidez que no vuelven"""
        gaps = []
        pip_value = PARES[symbol]['pip_value']
        
        for i in range(1, min(len(data), 50)):
            open_price = data['Open'].iloc[i]
            prev_close = data['Close'].iloc[i-1]
            
            gap_size = abs(open_price - prev_close)
            gap_pips = gap_size / pip_value
            
            if gap_pips >= 0.5:  # Mínimo 0.5 pips
                # Verificar si no se rellenó
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
                        'tiempo': data.index[i]
                    })
        
        return gaps
    
    def calcular_zonas(self, data):
        """Calcula Premium/Discount y detecta zona media"""
        high = data['High'].rolling(50).max().iloc[-1]
        low = data['Low'].rolling(50).min().iloc[-1]
        
        premium = high
        discount = low
        equilibrium = (premium + discount) / 2
        
        # Zona Atrapa (NO OPERAR)
        zona_superior = equilibrium + (premium - equilibrium) * 0.2
        zona_inferior = equilibrium - (equilibrium - discount) * 0.2
        
        precio = data['Close'].iloc[-1]
        
        if precio > zona_superior:
            zona = "PREMIUM"
        elif precio < zona_inferior:
            zona = "DISCOUNT"
        else:
            zona = "ZONA_ATRAPA"
        
        return {
            'premium': premium,
            'discount': discount,
            'equilibrium': equilibrium,
            'zona': zona,
            'precio': precio,
            'es_extremo': zona in ['PREMIUM', 'DISCOUNT']
        }
    
    def calcular_alma(self, data, window=9):
        """ALMA simplificado"""
        if len(data) < window:
            return None
        
        close = data['Close'].values[-window:]
        m = 0.85 * (window - 1)
        s = window / 6.0
        
        w = np.exp(-((np.arange(window) - m) ** 2) / (2 * s ** 2))
        w = w / w.sum()
        
        return np.sum(close * w)
    
    def calcular_kernel(self, data, lookback=8):
        """Kernel estimation simplificado"""
        if len(data) < lookback:
            return None
        
        close = data['Close'].values[-lookback:]
        weights = np.exp(-np.arange(lookback) / 2)
        weights = weights / weights.sum()
        
        return np.sum(close * weights)
    
    def calcular_donchian(self, data, period=12):
        """Donchian Channel"""
        if len(data) < period:
            return None, None, None
        
        upper = data['High'].rolling(period).max().iloc[-1]
        lower = data['Low'].rolling(period).min().iloc[-1]
        middle = (upper + lower) / 2
        
        return upper, middle, lower
    
    def detectar_mecha_55(self, data):
        """Detecta velas con 55%+ fuera de Bollinger"""
        if len(data) < 20:
            return False
        
        # Bollinger Bands manual
        sma = data['Close'].rolling(20).mean()
        std = data['Close'].rolling(20).std()
        upper_band = (sma + (2 * std)).iloc[-1]
        lower_band = (sma - (2 * std)).iloc[-1]
        
        ultima = data.iloc[-1]
        high = ultima['High']
        low = ultima['Low']
        rango = high - low
        
        if rango <= 0:
            return False
        
        # Calcular % fuera
        if low < lower_band:
            mecha_fuera = (lower_band - low) / rango
            if mecha_fuera >= 0.55:
                return 'bullish'
        
        if high > upper_band:
            mecha_fuera = (high - upper_band) / rango
            if mecha_fuera >= 0.55:
                return 'bearish'
        
        return False
    
    def es_fibonacci_time(self):
        """Verifica minuto Fibonacci"""
        minuto = datetime.now().minute
        return minuto in FIBONACCI_MINUTES
    
    def calcular_confluencias(self, symbol, data):
        """Analiza todas las confluencias"""
        confluencias = []
        puntos = 0
        
        # 1. Gaps
        gaps = self.detectar_gaps(data, symbol)
        if gaps:
            ultimo_gap = gaps[-1]
            confluencias.append(f"🔥 Gap {ultimo_gap['tipo']} ({ultimo_gap['pips']:.1f} pips)")
            puntos += 25
        
        # 2. Zonas
        zonas = self.calcular_zonas(data)
        if zonas['es_extremo']:
            confluencias.append(f"📍 Zona {zonas['zona']}")
            puntos += 20
        elif zonas['zona'] == 'ZONA_ATRAPA':
            return None  # NO OPERAR
        
        # 3. ALMA vs Kernel vs Donchian
        alma = self.calcular_alma(data)
        kernel = self.calcular_kernel(data)
        upper, middle, lower = self.calcular_donchian(data)
        
        if alma and kernel and middle:
            if alma > kernel > middle and zonas['zona'] == 'DISCOUNT':
                confluencias.append("✅ ALMA>Kernel>Donchian (BUY)")
                puntos += 25
            elif alma < kernel < middle and zonas['zona'] == 'PREMIUM':
                confluencias.append("✅ ALMA<Kernel<Donchian (SELL)")
                puntos += 25
        
        # 4. Mecha 55%
        mecha = self.detectar_mecha_55(data)
        if mecha:
            confluencias.append(f"🎯 Mecha 55% {mecha}")
            puntos += 20
        
        # 5. Timing Fibonacci
        if self.es_fibonacci_time():
            confluencias.append(f"⏰ Minuto Fibonacci {datetime.now().minute}")
            puntos += 10
        
        # 6. RSI
        rsi = calcular_rsi(data)
        if rsi < 30 and zonas['zona'] == 'DISCOUNT':
            confluencias.append(f"📊 RSI oversold ({rsi:.1f})")
            puntos += 15
        elif rsi > 70 and zonas['zona'] == 'PREMIUM':
            confluencias.append(f"📊 RSI overbought ({rsi:.1f})")
            puntos += 15
        
        # Determinar señal
        if puntos >= 60:
            if zonas['zona'] == 'DISCOUNT':
                return 'BUY', confluencias, puntos, zonas
            elif zonas['zona'] == 'PREMIUM':
                return 'SELL', confluencias, puntos, zonas
        
        return None
    
    def ejecutar(self):
        """Loop principal"""
        print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Escaneando...")
        
        if self.trades_hoy >= self.max_trades:
            print("✋ Límite diario alcanzado")
            return
        
        for symbol, info in PARES.items():
            print(f"📊 {info['nombre']}...", end=' ')
            
            data = self.obtener_datos(symbol, '1d', '1m')
            if data is None or len(data) < 100:
                print("❌ Sin datos")
                continue
            
            resultado = self.calcular_confluencias(symbol, data)
            
            if resultado:
                direccion, confluencias, puntos, zonas = resultado
                precio = data['Close'].iloc[-1]
                
                # Calcular SL/TP
                pip = PARES[symbol]['pip_value']
                if direccion == 'BUY':
                    sl = precio - (20 * pip)
                    tp = zonas['premium']
                else:
                    sl = precio + (20 * pip)
                    tp = zonas['discount']
                
                # Enviar señal
                self.enviar_señal({
                    'par': info['nombre'],
                    'direccion': direccion,
                    'precio': precio,
                    'sl': sl,
                    'tp': tp,
                    'puntos': puntos,
                    'confluencias': confluencias
                })
                
                self.trades_hoy += 1
                print(f"✅ SEÑAL {direccion}")
            else:
                print("⏳ Sin señal")
    
    def enviar_señal(self, señal):
        """Envía señal a Telegram"""
        mensaje = f"""
🚀 <b>SEÑAL CLAUDE LOVE</b>

📊 <b>Par:</b> {señal['par']}
🎯 <b>Dirección:</b> {señal['direccion']}
💰 <b>Entrada:</b> {señal['precio']:.5f}
🛡 <b>SL:</b> {señal['sl']:.5f}
🎯 <b>TP:</b> {señal['tp']:.5f}

<b>Confluencias ({señal['puntos']}%):</b>
{chr(10).join(señal['confluencias'])}

⏰ {datetime.now().strftime('%H:%M:%S')}
📍 Trade {self.trades_hoy}/{self.max_trades}
"""
        self.enviar_telegram(mensaje)
    
    def run(self):
        """Ejecuta el bot"""
        print(f"🚀 {self.nombre} corriendo...")
        
        while True:
            try:
                # Reset a medianoche
                if datetime.now().hour == 0 and datetime.now().minute == 0:
                    self.trades_hoy = 0
                    self.señales_enviadas = []
                
                self.ejecutar()
                time.sleep(60)  # Esperar 1 minuto
                
            except KeyboardInterrupt:
                print("\n👋 Detenido")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(60)

# =======================
# INICIO
# =======================
if __name__ == "__main__":
    print("""
    ╔════════════════════════════╗
    ║   CLAUDE LOVE v1.0         ║
    ║   Railway Edition          ║
    ╚════════════════════════════╝
    """)
    
    bot = ClaudeLove()
    bot.run()
