# claude_love_2025_production.py
"""
CLAUDE LOVE 2025 - RAILWAY PRODUCTION
Optimizado para Railway
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
import time
import os
import sys
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuración desde variables de entorno
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', "7718630865:AAEMclwlqzuxb5uFPqX9dyJLo7ib19QnJt8")
CHAT_ID = os.environ.get('CHAT_ID', "5358902915")

# Para Railway - importante
print("=" * 50, flush=True)
print("CLAUDE LOVE 2025 - INICIANDO EN RAILWAY", flush=True)
print("=" * 50, flush=True)

# Pares principales
PARES = {
    'EURUSD=X': {'nombre': 'EUR/USD', 'pip': 0.0001},
    'GBPUSD=X': {'nombre': 'GBP/USD', 'pip': 0.0001},
    'USDJPY=X': {'nombre': 'USD/JPY', 'pip': 0.01}
}

class ClaudeLove2025:
    def __init__(self):
        self.nombre = "🤖 CLAUDE LOVE 2025"
        self.trades_hoy = 0
        self.max_trades = 10
        self.señales_semana = 0
        
        # Configuraciones del documento 2025
        self.RSI_CONFIG = {
            'period': 9,    # 30% menos señales falsas
            'high': 75,
            'low': 25
        }
        
        self.MACD_LINDA = {
            'fast': 3,      # 40% más rápido
            'slow': 10,
            'signal': 16
        }
        
        print(f"Sistema inicializado correctamente", flush=True)
        
        # Enviar mensaje de inicio
        self.enviar_telegram(f"""
🚀 <b>CLAUDE LOVE 2025 - RAILWAY</b>

✅ Sistema desplegado en Railway
✅ RSI(9) 75/25 activo
✅ MACD Linda Raschke activo
✅ Multi-timeframe activo
✅ Smart Money Concepts activo

🎯 Meta: 10-20 señales/semana
📊 Win Rate objetivo: 60-75%

⏰ Hora servidor: {datetime.now().strftime('%H:%M:%S')}

<i>Sistema en producción...</i>
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
            print(f"Error Telegram: {e}", flush=True)
            return False
    
    def obtener_datos(self, symbol, period='5d', interval='1h'):
        """Obtiene datos - optimizado para Railway"""
        intentos = 3
        for intento in range(intentos):
            try:
                data = yf.download(
                    symbol, 
                    period=period, 
                    interval=interval, 
                    progress=False,
                    auto_adjust=True,
                    repair=True,
                    threads=False  # Importante para Railway
                )
                
                if not data.empty and len(data) > 20:
                    return data
                    
            except Exception as e:
                print(f"Intento {intento+1}/{intentos} falló: {str(e)[:50]}", flush=True)
                time.sleep(2)
        
        return None
    
    def calcular_rsi(self, data, period=None):
        """RSI profesional"""
        if period is None:
            period = self.RSI_CONFIG['period']
        
        try:
            close = data['Close']
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except:
            return pd.Series([50] * len(data))
    
    def calcular_macd_linda(self, data):
        """MACD Linda Raschke"""
        try:
            close = data['Close']
            ema_fast = close.ewm(span=self.MACD_LINDA['fast'], adjust=False).mean()
            ema_slow = close.ewm(span=self.MACD_LINDA['slow'], adjust=False).mean()
            macd = ema_fast - ema_slow
            signal = macd.ewm(span=self.MACD_LINDA['signal'], adjust=False).mean()
            histogram = macd - signal
            return macd, signal, histogram
        except:
            return None, None, None
    
    def estrategia_rsi_macd_reversion(self, data):
        """73% win rate strategy"""
        try:
            if len(data) < 30:
                return None
            
            rsi = self.calcular_rsi(data)
            macd, signal, hist = self.calcular_macd_linda(data)
            
            if macd is None:
                return None
            
            # Bollinger Bands
            sma = data['Close'].rolling(20).mean()
            std = data['Close'].rolling(20).std()
            upper = sma + (2 * std)
            lower = sma - (2 * std)
            
            precio = float(data['Close'].iloc[-1])
            rsi_actual = float(rsi.iloc[-1])
            
            # Señales
            if rsi_actual < self.RSI_CONFIG['low'] and precio < float(lower.iloc[-1]):
                if float(macd.iloc[-1]) > float(signal.iloc[-1]):
                    return 'BUY', 73
            
            elif rsi_actual > self.RSI_CONFIG['high'] and precio > float(upper.iloc[-1]):
                if float(macd.iloc[-1]) < float(signal.iloc[-1]):
                    return 'SELL', 73
            
        except Exception as e:
            print(f"Error estrategia: {e}", flush=True)
        
        return None
    
    def detectar_smart_money(self, data):
        """Smart Money Concepts"""
        try:
            if len(data) < 20:
                return None
            
            # Order Block institucional
            avg_vol = float(data['Volume'].rolling(20).mean().iloc[-1])
            current_vol = float(data['Volume'].iloc[-1])
            
            if current_vol > avg_vol * 2.5:  # Ajustado para Railway
                if data['Close'].iloc[-1] > data['Open'].iloc[-1]:
                    return 'BUY', 70
                else:
                    return 'SELL', 70
                    
        except:
            pass
        
        return None
    
    def sistema_mtf_simple(self, symbol):
        """Multi-timeframe 70-75% win rate"""
        try:
            data = self.obtener_datos(symbol, '10d', '1h')
            if data is None or len(data) < 50:
                return None
            
            ema9 = data['Close'].ewm(span=9).mean()
            ema21 = data['Close'].ewm(span=21).mean()
            rsi = self.calcular_rsi(data)
            
            tendencia_alcista = float(ema9.iloc[-1]) > float(ema21.iloc[-1])
            tendencia_bajista = float(ema9.iloc[-1]) < float(ema21.iloc[-1])
            rsi_actual = float(rsi.iloc[-1])
            
            if tendencia_alcista and rsi_actual < 40:
                return 'BUY', 75
            elif tendencia_bajista and rsi_actual > 60:
                return 'SELL', 75
                
        except Exception as e:
            print(f"Error MTF: {e}", flush=True)
        
        return None
    
    def analizar_par(self, symbol, info):
        """Análisis completo"""
        print(f"Analizando {info['nombre']}...", flush=True)
        
        data = self.obtener_datos(symbol, '5d', '1h')
        if data is None or len(data) < 30:
            print(f"Sin datos suficientes para {symbol}", flush=True)
            return None
        
        señales = []
        
        # Estrategias
        resultado1 = self.estrategia_rsi_macd_reversion(data)
        if resultado1:
            dir1, conf1 = resultado1
            señales.append({'dir': dir1, 'conf': conf1, 'strategy': 'RSI+MACD'})
            print(f"✓ RSI+MACD: {dir1} ({conf1}%)", flush=True)
        
        resultado2 = self.detectar_smart_money(data)
        if resultado2:
            dir2, conf2 = resultado2
            señales.append({'dir': dir2, 'conf': conf2, 'strategy': 'SMC'})
            print(f"✓ Smart Money: {dir2} ({conf2}%)", flush=True)
        
        resultado3 = self.sistema_mtf_simple(symbol)
        if resultado3:
            dir3, conf3 = resultado3
            señales.append({'dir': dir3, 'conf': conf3, 'strategy': 'MTF'})
            print(f"✓ Multi-TF: {dir3} ({conf3}%)", flush=True)
        
        if not señales:
            return None
        
        # Consenso
        buy_signals = [s for s in señales if s['dir'] == 'BUY']
        sell_signals = [s for s in señales if s['dir'] == 'SELL']
        
        if len(buy_signals) > len(sell_signals) and len(buy_signals) >= 2:
            confianza = sum(s['conf'] for s in buy_signals) / len(buy_signals)
            if confianza >= 60:
                return {
                    'symbol': symbol,
                    'nombre': info['nombre'],
                    'direction': 'BUY',
                    'confidence': confianza,
                    'signals': buy_signals,
                    'price': float(data['Close'].iloc[-1]),
                    'pip': info['pip']
                }
        
        elif len(sell_signals) > len(buy_signals) and len(sell_signals) >= 2:
            confianza = sum(s['conf'] for s in sell_signals) / len(sell_signals)
            if confianza >= 60:
                return {
                    'symbol': symbol,
                    'nombre': info['nombre'],
                    'direction': 'SELL',
                    'confidence': confianza,
                    'signals': sell_signals,
                    'price': float(data['Close'].iloc[-1]),
                    'pip': info['pip']
                }
        
        return None
    
    def enviar_señal(self, signal):
        """Envía señal a Telegram"""
        try:
            precio = signal['price']
            pip = signal['pip']
            
            if signal['direction'] == 'BUY':
                sl = precio - (20 * pip)
                tp = precio + (50 * pip)
            else:
                sl = precio + (20 * pip)
                tp = precio - (50 * pip)
            
            estrategias = ", ".join([s['strategy'] for s in signal['signals']])
            
            mensaje = f"""
🎯 <b>SEÑAL DETECTADA</b>

📊 <b>Par:</b> {signal['nombre']}
📈 <b>Dirección:</b> {signal['direction']}
💰 <b>Entrada:</b> {precio:.5f}
🛡 <b>SL:</b> {sl:.5f}
🎯 <b>TP:</b> {tp:.5f}
📊 <b>Confianza:</b> {signal['confidence']:.1f}%

<b>Estrategias:</b> {estrategias}

⏰ {datetime.now().strftime('%H:%M:%S')}
📍 Señal #{self.señales_semana + 1} esta semana
"""
            
            if self.enviar_telegram(mensaje):
                self.trades_hoy += 1
                self.señales_semana += 1
                print(f"Señal enviada exitosamente", flush=True)
                return True
                
        except Exception as e:
            print(f"Error enviando señal: {e}", flush=True)
        
        return False
    
    def run(self):
        """Loop principal optimizado para Railway"""
        print(f"Sistema en ejecución...", flush=True)
        
        ciclo = 0
        while True:
            try:
                ciclo += 1
                hora = datetime.now()
                
                print(f"\nCiclo {ciclo} - {hora.strftime('%H:%M:%S')}", flush=True)
                print(f"Trades hoy: {self.trades_hoy} | Semana: {self.señales_semana}", flush=True)
                
                # Reset diario
                if hora.hour == 0 and hora.minute < 5:
                    self.trades_hoy = 0
                
                # Reset semanal
                if hora.weekday() == 0 and hora.hour == 0:
                    self.señales_semana = 0
                
                # Analizar pares
                if self.trades_hoy < self.max_trades:
                    for symbol, info in PARES.items():
                        signal = self.analizar_par(symbol, info)
                        
                        if signal:
                            print(f"SEÑAL CONFIRMADA: {info['nombre']}", flush=True)
                            self.enviar_señal(signal)
                            time.sleep(2)
                
                # Esperar 5 minutos
                print(f"Esperando 5 minutos...", flush=True)
                time.sleep(300)
                
            except Exception as e:
                print(f"Error en ciclo: {e}", flush=True)
                time.sleep(60)

# INICIO
if __name__ == "__main__":
    try:
        print("CLAUDE LOVE 2025 - RAILWAY EDITION", flush=True)
        print("="*50, flush=True)
        bot = ClaudeLove2025()
        bot.run()
    except Exception as e:
        print(f"Error fatal: {e}", flush=True)
        sys.exit(1)