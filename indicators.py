"""
CLAUDE TRADING BOT - INDICADORES TÉCNICOS AVANZADOS
====================================================
Implementación profesional de indicadores para análisis técnico
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict, List
from config import INDICATORS_CONFIG


class TechnicalIndicators:
    """Clase para cálculo de indicadores técnicos avanzados"""

    def __init__(self, config: Dict = None):
        """
        Inicializa los indicadores técnicos

        Args:
            config: Configuración personalizada de indicadores
        """
        self.config = config if config else INDICATORS_CONFIG

    # ========================================================================
    # RSI - RELATIVE STRENGTH INDEX
    # ========================================================================

    def calculate_rsi(self, data: pd.DataFrame, period: int = None) -> pd.Series:
        """
        Calcula el RSI (Relative Strength Index)

        El RSI es un oscilador de momentum que mide la velocidad y el cambio
        de los movimientos de precio. Valores > 70 indican sobrecompra,
        valores < 30 indican sobreventa.

        Args:
            data: DataFrame con columna 'Close'
            period: Período para el cálculo (default: config)

        Returns:
            Series con valores de RSI
        """
        if period is None:
            period = self.config['RSI']['period']

        try:
            close = data['Close']
            delta = close.diff()

            gain = delta.where(delta > 0, 0).rolling(window=period).mean()
            loss = -delta.where(delta < 0, 0).rolling(window=period).mean()

            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            return rsi
        except Exception as e:
            print(f"Error calculando RSI: {e}")
            return pd.Series([50] * len(data), index=data.index)

    # ========================================================================
    # MACD - MOVING AVERAGE CONVERGENCE DIVERGENCE
    # ========================================================================

    def calculate_macd(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calcula MACD con parámetros Linda Raschke (más rápido que estándar)

        MACD muestra la relación entre dos EMAs. El cruce de la línea MACD
        con la línea de señal genera señales de compra/venta.

        Args:
            data: DataFrame con columna 'Close'

        Returns:
            Tupla (macd_line, signal_line, histogram)
        """
        try:
            close = data['Close']
            config = self.config['MACD']

            ema_fast = close.ewm(span=config['fast'], adjust=False).mean()
            ema_slow = close.ewm(span=config['slow'], adjust=False).mean()

            macd = ema_fast - ema_slow
            signal = macd.ewm(span=config['signal'], adjust=False).mean()
            histogram = macd - signal

            return macd, signal, histogram
        except Exception as e:
            print(f"Error calculando MACD: {e}")
            return None, None, None

    # ========================================================================
    # BOLLINGER BANDS
    # ========================================================================

    def calculate_bollinger_bands(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calcula las Bandas de Bollinger

        Las Bollinger Bands miden la volatilidad del mercado. Precio tocando
        la banda superior = posible sobrecompra, banda inferior = sobreventa.

        Args:
            data: DataFrame con columna 'Close'

        Returns:
            Tupla (upper_band, middle_band, lower_band)
        """
        try:
            close = data['Close']
            config = self.config['BOLLINGER']

            sma = close.rolling(window=config['period']).mean()
            std = close.rolling(window=config['period']).std()

            upper = sma + (config['std_dev'] * std)
            lower = sma - (config['std_dev'] * std)

            return upper, sma, lower
        except Exception as e:
            print(f"Error calculando Bollinger Bands: {e}")
            return None, None, None

    def detect_bollinger_squeeze(self, data: pd.DataFrame) -> bool:
        """
        Detecta Bollinger Squeeze (baja volatilidad antes de breakout)

        Args:
            data: DataFrame con columna 'Close'

        Returns:
            True si hay squeeze (posible breakout inminente)
        """
        try:
            upper, middle, lower = self.calculate_bollinger_bands(data)
            if upper is None:
                return False

            # Ancho de banda normalizado
            bandwidth = (upper - lower) / middle
            threshold = self.config['BOLLINGER']['squeeze_threshold']

            return float(bandwidth.iloc[-1]) < threshold
        except:
            return False

    # ========================================================================
    # EMA - EXPONENTIAL MOVING AVERAGE
    # ========================================================================

    def calculate_ema(self, data: pd.DataFrame, period: int) -> pd.Series:
        """
        Calcula EMA (Exponential Moving Average)

        EMA da más peso a precios recientes que SMA. Usado para detectar
        tendencias y generar señales de crossover.

        Args:
            data: DataFrame con columna 'Close'
            period: Período de la EMA

        Returns:
            Series con valores de EMA
        """
        try:
            return data['Close'].ewm(span=period, adjust=False).mean()
        except Exception as e:
            print(f"Error calculando EMA: {e}")
            return pd.Series([0] * len(data), index=data.index)

    def get_ema_crossover(self, data: pd.DataFrame) -> Dict[str, bool]:
        """
        Detecta cruces de EMAs (Golden Cross / Death Cross)

        Args:
            data: DataFrame con columna 'Close'

        Returns:
            Dict con señales de cruce
        """
        config = self.config['EMA']

        ema_fast = self.calculate_ema(data, config['fast'])
        ema_medium = self.calculate_ema(data, config['medium'])
        ema_slow = self.calculate_ema(data, config['slow'])

        return {
            'bullish_cross': (
                float(ema_fast.iloc[-1]) > float(ema_medium.iloc[-1]) and
                float(ema_fast.iloc[-2]) <= float(ema_medium.iloc[-2])
            ),
            'bearish_cross': (
                float(ema_fast.iloc[-1]) < float(ema_medium.iloc[-1]) and
                float(ema_fast.iloc[-2]) >= float(ema_medium.iloc[-2])
            ),
            'golden_cross': (
                float(ema_medium.iloc[-1]) > float(ema_slow.iloc[-1]) and
                float(ema_medium.iloc[-2]) <= float(ema_slow.iloc[-2])
            ),
            'death_cross': (
                float(ema_medium.iloc[-1]) < float(ema_slow.iloc[-1]) and
                float(ema_medium.iloc[-2]) >= float(ema_slow.iloc[-2])
            )
        }

    # ========================================================================
    # ADX - AVERAGE DIRECTIONAL INDEX
    # ========================================================================

    def calculate_adx(self, data: pd.DataFrame, period: int = None) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calcula ADX (Average Directional Index) y DI+/DI-

        ADX mide la FUERZA de la tendencia (no dirección):
        - ADX < 20: Mercado lateral (ranging)
        - ADX 20-40: Tendencia moderada
        - ADX > 40: Tendencia fuerte

        DI+ > DI- = tendencia alcista
        DI- > DI+ = tendencia bajista

        Args:
            data: DataFrame con High, Low, Close
            period: Período para el cálculo

        Returns:
            Tupla (adx, di_plus, di_minus)
        """
        if period is None:
            period = self.config['ADX']['period']

        try:
            high = data['High']
            low = data['Low']
            close = data['Close']

            # True Range
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

            # Directional Movement
            up_move = high - high.shift(1)
            down_move = low.shift(1) - low

            plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
            minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

            # Smooth
            atr = tr.rolling(window=period).mean()
            plus_di = 100 * pd.Series(plus_dm).rolling(window=period).mean() / atr
            minus_di = 100 * pd.Series(minus_dm).rolling(window=period).mean() / atr

            # ADX
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(window=period).mean()

            return adx, plus_di, minus_di

        except Exception as e:
            print(f"Error calculando ADX: {e}")
            return None, None, None

    def get_trend_strength(self, data: pd.DataFrame) -> Dict[str, any]:
        """
        Analiza la fuerza y dirección de la tendencia usando ADX

        Args:
            data: DataFrame con OHLC

        Returns:
            Dict con análisis de tendencia
        """
        adx, di_plus, di_minus = self.calculate_adx(data)

        if adx is None:
            return {'strength': 'unknown', 'direction': 'unknown', 'tradeable': False}

        adx_value = float(adx.iloc[-1])
        config = self.config['ADX']

        # Determinar fuerza
        if adx_value > config['strong_trend']:
            strength = 'strong'
        elif adx_value > config['trending_threshold']:
            strength = 'moderate'
        elif adx_value > config['weak_trend']:
            strength = 'weak'
        else:
            strength = 'ranging'

        # Determinar dirección
        di_plus_val = float(di_plus.iloc[-1])
        di_minus_val = float(di_minus.iloc[-1])

        if di_plus_val > di_minus_val:
            direction = 'bullish'
        elif di_minus_val > di_plus_val:
            direction = 'bearish'
        else:
            direction = 'neutral'

        return {
            'strength': strength,
            'direction': direction,
            'adx': adx_value,
            'di_plus': di_plus_val,
            'di_minus': di_minus_val,
            'tradeable': adx_value > config['trending_threshold']
        }

    # ========================================================================
    # ATR - AVERAGE TRUE RANGE
    # ========================================================================

    def calculate_atr(self, data: pd.DataFrame, period: int = None) -> pd.Series:
        """
        Calcula ATR (Average True Range) - medida de volatilidad

        ATR mide la volatilidad promedio del mercado. Se usa para:
        - Ajustar stop-loss dinámicamente
        - Determinar tamaño de posición
        - Identificar breakouts

        Args:
            data: DataFrame con High, Low, Close
            period: Período para el cálculo

        Returns:
            Series con valores de ATR
        """
        if period is None:
            period = self.config['ATR']['period']

        try:
            high = data['High']
            low = data['Low']
            close = data['Close']

            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))

            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean()

            return atr

        except Exception as e:
            print(f"Error calculando ATR: {e}")
            return pd.Series([0] * len(data), index=data.index)

    def get_atr_stops(self, data: pd.DataFrame, direction: str = 'BUY') -> Dict[str, float]:
        """
        Calcula stop-loss y take-profit basados en ATR

        Args:
            data: DataFrame con OHLC
            direction: 'BUY' o 'SELL'

        Returns:
            Dict con SL, TP y trailing stop
        """
        atr = self.calculate_atr(data)
        price = float(data['Close'].iloc[-1])
        atr_value = float(atr.iloc[-1])

        config = self.config['ATR']

        if direction == 'BUY':
            sl = price - (atr_value * config['multiplier_sl'])
            tp = price + (atr_value * config['multiplier_tp'])
            trailing = price - (atr_value * config['multiplier_trail'])
        else:  # SELL
            sl = price + (atr_value * config['multiplier_sl'])
            tp = price - (atr_value * config['multiplier_tp'])
            trailing = price + (atr_value * config['multiplier_trail'])

        return {
            'stop_loss': sl,
            'take_profit': tp,
            'trailing_stop': trailing,
            'atr_value': atr_value,
            'volatility': 'high' if atr_value > atr.mean() else 'low'
        }

    # ========================================================================
    # STOCHASTIC OSCILLATOR
    # ========================================================================

    def calculate_stochastic(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """
        Calcula Stochastic Oscillator (%K y %D)

        Stochastic compara el precio de cierre actual con su rango durante
        un período. Valores > 80 = sobrecompra, < 20 = sobreventa.

        Args:
            data: DataFrame con High, Low, Close

        Returns:
            Tupla (%K, %D)
        """
        try:
            config = self.config['STOCHASTIC']

            low_min = data['Low'].rolling(window=config['k_period']).min()
            high_max = data['High'].rolling(window=config['k_period']).max()

            k = 100 * ((data['Close'] - low_min) / (high_max - low_min))
            d = k.rolling(window=config['d_period']).mean()

            return k, d

        except Exception as e:
            print(f"Error calculando Stochastic: {e}")
            return None, None

    # ========================================================================
    # VOLUME ANALYSIS
    # ========================================================================

    def analyze_volume(self, data: pd.DataFrame) -> Dict[str, any]:
        """
        Analiza el volumen para detectar smart money

        Args:
            data: DataFrame con Volume

        Returns:
            Dict con análisis de volumen
        """
        try:
            config = self.config['VOLUME']

            avg_volume = data['Volume'].rolling(window=config['ma_period']).mean()
            current_volume = float(data['Volume'].iloc[-1])
            avg_vol_value = float(avg_volume.iloc[-1])

            volume_ratio = current_volume / avg_vol_value if avg_vol_value > 0 else 1

            # Clasificar volumen
            if volume_ratio > config['surge_multiplier']:
                status = 'surge'  # Volumen institucional
            elif volume_ratio < config['dry_threshold']:
                status = 'dry'    # Volumen bajo (desinterés)
            else:
                status = 'normal'

            return {
                'current': current_volume,
                'average': avg_vol_value,
                'ratio': volume_ratio,
                'status': status,
                'smart_money': volume_ratio > config['surge_multiplier']
            }

        except Exception as e:
            print(f"Error analizando volumen: {e}")
            return {'status': 'unknown', 'smart_money': False}

    # ========================================================================
    # FIBONACCI RETRACEMENTS
    # ========================================================================

    def calculate_fibonacci_levels(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calcula niveles de retroceso de Fibonacci

        Fibonacci identifica niveles de soporte/resistencia potenciales
        basados en la secuencia de Fibonacci (23.6%, 38.2%, 50%, 61.8%, 78.6%)

        Args:
            data: DataFrame con High, Low

        Returns:
            Dict con niveles de Fibonacci
        """
        try:
            config = self.config['FIBONACCI']
            lookback = min(config['lookback'], len(data))

            recent_data = data.tail(lookback)
            high = recent_data['High'].max()
            low = recent_data['Low'].min()
            diff = high - low

            levels = {}
            for level in config['levels']:
                levels[f'fib_{int(level*1000)}'] = high - (diff * level)

            levels['swing_high'] = high
            levels['swing_low'] = low

            return levels

        except Exception as e:
            print(f"Error calculando Fibonacci: {e}")
            return {}

    # ========================================================================
    # SUPPORT & RESISTANCE
    # ========================================================================

    def find_support_resistance(self, data: pd.DataFrame, window: int = 20) -> Dict[str, List[float]]:
        """
        Identifica niveles de soporte y resistencia

        Args:
            data: DataFrame con High, Low, Close
            window: Ventana para detectar pivots

        Returns:
            Dict con listas de niveles de soporte y resistencia
        """
        try:
            highs = data['High']
            lows = data['Low']

            resistance_levels = []
            support_levels = []

            # Buscar pivots altos (resistencia)
            for i in range(window, len(data) - window):
                if highs.iloc[i] == highs.iloc[i-window:i+window+1].max():
                    resistance_levels.append(float(highs.iloc[i]))

            # Buscar pivots bajos (soporte)
            for i in range(window, len(data) - window):
                if lows.iloc[i] == lows.iloc[i-window:i+window+1].min():
                    support_levels.append(float(lows.iloc[i]))

            return {
                'resistance': sorted(set(resistance_levels), reverse=True)[:5],
                'support': sorted(set(support_levels), reverse=True)[:5]
            }

        except Exception as e:
            print(f"Error encontrando S/R: {e}")
            return {'resistance': [], 'support': []}

    # ========================================================================
    # INDICADOR COMBINADO
    # ========================================================================

    def get_full_analysis(self, data: pd.DataFrame) -> Dict[str, any]:
        """
        Análisis técnico completo con todos los indicadores

        Args:
            data: DataFrame con OHLC y Volume

        Returns:
            Dict con análisis completo
        """
        try:
            return {
                'rsi': float(self.calculate_rsi(data).iloc[-1]),
                'macd': self.calculate_macd(data),
                'bollinger': self.calculate_bollinger_bands(data),
                'bollinger_squeeze': self.detect_bollinger_squeeze(data),
                'ema_crossover': self.get_ema_crossover(data),
                'trend': self.get_trend_strength(data),
                'atr_stops': self.get_atr_stops(data),
                'stochastic': self.calculate_stochastic(data),
                'volume': self.analyze_volume(data),
                'fibonacci': self.calculate_fibonacci_levels(data),
                'support_resistance': self.find_support_resistance(data)
            }
        except Exception as e:
            print(f"Error en análisis completo: {e}")
            return {}


# ============================================================================
# FUNCIÓN DE PRUEBA
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("PRUEBA DE INDICADORES TÉCNICOS")
    print("=" * 70)

    # Crear datos de prueba
    import yfinance as yf

    print("\n📊 Descargando datos de prueba (EUR/USD)...")
    data = yf.download('EURUSD=X', period='30d', interval='1h', progress=False)

    if not data.empty:
        indicators = TechnicalIndicators()

        print("\n✅ Calculando indicadores...")
        analysis = indicators.get_full_analysis(data)

        print(f"\n📈 RSI: {analysis['rsi']:.2f}")
        print(f"📊 Tendencia: {analysis['trend']['strength']} - {analysis['trend']['direction']}")
        print(f"💹 ADX: {analysis['trend']['adx']:.2f}")
        print(f"📉 Volumen: {analysis['volume']['status']}")
        print(f"🎯 Fibonacci niveles: {len(analysis['fibonacci'])} calculados")

        print("\n✅ Indicadores funcionando correctamente")
    else:
        print("❌ No se pudieron descargar datos")
