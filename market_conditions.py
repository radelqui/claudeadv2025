"""
CLAUDE TRADING BOT - DETECCIÓN DE CONDICIONES DE MERCADO
==========================================================
Identifica el tipo de mercado para adaptar estrategias dinámicamente
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from config import MARKET_CONDITIONS_CONFIG, INDICATORS_CONFIG
from indicators import TechnicalIndicators


class MarketConditionDetector:
    """Detecta y clasifica las condiciones del mercado"""

    def __init__(self):
        """Inicializa el detector de condiciones de mercado"""
        self.config = MARKET_CONDITIONS_CONFIG
        self.indicators = TechnicalIndicators()

    # ========================================================================
    # DETECCIÓN DE TIPO DE MERCADO
    # ========================================================================

    def detect_market_type(self, data: pd.DataFrame) -> Dict[str, any]:
        """
        Detecta si el mercado está en tendencia o lateral (ranging)

        Utiliza ADX como indicador principal:
        - ADX > 25: Mercado tendencial (trending)
        - ADX < 20: Mercado lateral (ranging)
        - Entre 20-25: Transición

        Args:
            data: DataFrame con OHLC

        Returns:
            Dict con tipo de mercado y detalles
        """
        try:
            trend_analysis = self.indicators.get_trend_strength(data)

            adx_value = trend_analysis['adx']
            direction = trend_analysis['direction']

            # Clasificar tipo de mercado
            if adx_value >= self.config['trending_adx']:
                market_type = 'trending'
                confidence = min(100, (adx_value / 40) * 100)  # Escala 0-100
            elif adx_value <= self.config['ranging_adx']:
                market_type = 'ranging'
                confidence = min(100, ((40 - adx_value) / 40) * 100)
            else:
                market_type = 'transitioning'
                confidence = 50

            return {
                'type': market_type,
                'direction': direction,
                'adx': adx_value,
                'confidence': confidence,
                'tradeable': trend_analysis['tradeable'],
                'preferred_strategies': self._get_preferred_strategies(market_type),
                'adjustments': self._get_market_adjustments(market_type)
            }

        except Exception as e:
            print(f"Error detectando tipo de mercado: {e}")
            return {
                'type': 'unknown',
                'direction': 'neutral',
                'confidence': 0,
                'tradeable': False,
                'preferred_strategies': [],
                'adjustments': {}
            }

    def _get_preferred_strategies(self, market_type: str) -> List[str]:
        """
        Obtiene estrategias recomendadas según tipo de mercado

        Args:
            market_type: 'trending', 'ranging', o 'transitioning'

        Returns:
            Lista de estrategias recomendadas
        """
        if market_type == 'trending':
            return self.config['trending_market']['preferred_strategies']
        elif market_type == 'ranging':
            return self.config['ranging_market']['preferred_strategies']
        else:
            # En transición, usar todas las estrategias
            return []

    def _get_market_adjustments(self, market_type: str) -> Dict[str, float]:
        """
        Obtiene ajustes de parámetros según tipo de mercado

        Args:
            market_type: Tipo de mercado

        Returns:
            Dict con ajustes recomendados
        """
        if market_type == 'trending':
            config = self.config['trending_market']
            return {
                'confidence_boost': config['confidence_boost'],
                'position_size_multiplier': config['position_size_multiplier']
            }
        elif market_type == 'ranging':
            config = self.config['ranging_market']
            return {
                'confidence_boost': config['confidence_boost'],
                'position_size_multiplier': config['position_size_multiplier']
            }
        else:
            return {
                'confidence_boost': 0,
                'position_size_multiplier': 1.0
            }

    # ========================================================================
    # DETECCIÓN DE VOLATILIDAD
    # ========================================================================

    def detect_volatility(self, data: pd.DataFrame) -> Dict[str, any]:
        """
        Analiza la volatilidad del mercado usando ATR

        Alta volatilidad = mayor riesgo, requiere stops más amplios
        Baja volatilidad = menor riesgo, oportunidad de aumentar posición

        Args:
            data: DataFrame con OHLC

        Returns:
            Dict con análisis de volatilidad
        """
        try:
            atr = self.indicators.calculate_atr(data)
            current_atr = float(atr.iloc[-1])
            avg_atr = float(atr.tail(50).mean())
            price = float(data['Close'].iloc[-1])

            # Volatilidad normalizada (ATR / precio)
            atr_pct = (current_atr / price) * 100

            # Clasificar volatilidad
            if current_atr > avg_atr * 1.5:
                level = 'high'
                adjustments = self.config['volatile_market']
            elif current_atr < avg_atr * 0.7:
                level = 'low'
                adjustments = {'reduce_position_size': 1.0, 'increase_stops': 1.0}
            else:
                level = 'normal'
                adjustments = {'reduce_position_size': 1.0, 'increase_stops': 1.0}

            return {
                'level': level,
                'atr': current_atr,
                'atr_pct': atr_pct,
                'avg_atr': avg_atr,
                'ratio': current_atr / avg_atr if avg_atr > 0 else 1,
                'adjustments': adjustments
            }

        except Exception as e:
            print(f"Error detectando volatilidad: {e}")
            return {
                'level': 'unknown',
                'atr': 0,
                'adjustments': {}
            }

    # ========================================================================
    # ANÁLISIS DE MOMENTUM
    # ========================================================================

    def analyze_momentum(self, data: pd.DataFrame) -> Dict[str, any]:
        """
        Analiza el momentum del mercado

        Momentum fuerte = continuación probable
        Momentum débil = posible reversión

        Args:
            data: DataFrame con OHLC

        Returns:
            Dict con análisis de momentum
        """
        try:
            # RSI para momentum
            rsi = self.indicators.calculate_rsi(data)
            rsi_value = float(rsi.iloc[-1])

            # MACD para momentum
            macd, signal, hist = self.indicators.calculate_macd(data)
            macd_value = float(macd.iloc[-1])
            signal_value = float(signal.iloc[-1])
            hist_value = float(hist.iloc[-1])

            # Clasificar momentum
            if rsi_value > 60 and macd_value > signal_value and hist_value > 0:
                strength = 'strong_bullish'
                score = min(100, ((rsi_value - 50) / 50) * 100)
            elif rsi_value < 40 and macd_value < signal_value and hist_value < 0:
                strength = 'strong_bearish'
                score = min(100, ((50 - rsi_value) / 50) * 100)
            elif 45 <= rsi_value <= 55:
                strength = 'neutral'
                score = 50
            else:
                strength = 'weak'
                score = 50

            return {
                'strength': strength,
                'score': score,
                'rsi': rsi_value,
                'macd_hist': hist_value,
                'bullish': rsi_value > 50 and macd_value > signal_value,
                'bearish': rsi_value < 50 and macd_value < signal_value
            }

        except Exception as e:
            print(f"Error analizando momentum: {e}")
            return {
                'strength': 'unknown',
                'score': 50,
                'bullish': False,
                'bearish': False
            }

    # ========================================================================
    # DETECCIÓN DE CORRELACIÓN ENTRE PARES
    # ========================================================================

    def analyze_correlation(self, data_dict: Dict[str, pd.DataFrame],
                           lookback: int = 50) -> Dict[str, float]:
        """
        Calcula correlación entre pares de trading

        Correlación alta = no abrir múltiples posiciones
        Correlación negativa = diversificación

        Args:
            data_dict: Dict con DataFrames de cada par
            lookback: Período para calcular correlación

        Returns:
            Dict con matriz de correlación
        """
        try:
            pairs = list(data_dict.keys())
            returns_dict = {}

            # Calcular retornos para cada par
            for pair, data in data_dict.items():
                if len(data) >= lookback:
                    returns = data['Close'].pct_change().tail(lookback)
                    returns_dict[pair] = returns

            if len(returns_dict) < 2:
                return {}

            # Crear DataFrame de retornos
            returns_df = pd.DataFrame(returns_dict)

            # Calcular matriz de correlación
            correlation_matrix = returns_df.corr()

            # Convertir a diccionario
            correlations = {}
            for i, pair1 in enumerate(pairs):
                for pair2 in pairs[i+1:]:
                    if pair1 in returns_dict and pair2 in returns_dict:
                        corr_key = f"{pair1}_{pair2}"
                        correlations[corr_key] = float(correlation_matrix.loc[pair1, pair2])

            return correlations

        except Exception as e:
            print(f"Error calculando correlación: {e}")
            return {}

    def check_position_correlation(self, new_pair: str, open_positions: List[str],
                                   correlations: Dict[str, float]) -> bool:
        """
        Verifica si se puede abrir posición según correlación

        Args:
            new_pair: Par que se quiere tradear
            open_positions: Lista de pares con posiciones abiertas
            correlations: Dict con correlaciones

        Returns:
            True si se puede abrir la posición
        """
        try:
            highly_correlated = 0

            for open_pair in open_positions:
                corr_key = f"{min(new_pair, open_pair)}_{max(new_pair, open_pair)}"
                correlation = correlations.get(corr_key, 0)

                # Correlación > 0.7 = altamente correlacionados
                if abs(correlation) > 0.7:
                    highly_correlated += 1

            # Límite de posiciones correlacionadas del config
            max_correlated = MARKET_CONDITIONS_CONFIG.get('max_correlation_positions', 2)

            return highly_correlated < max_correlated

        except Exception as e:
            print(f"Error verificando correlación: {e}")
            return True  # Permitir en caso de error

    # ========================================================================
    # ANÁLISIS COMPLETO DE CONDICIONES
    # ========================================================================

    def get_full_market_analysis(self, data: pd.DataFrame) -> Dict[str, any]:
        """
        Análisis completo de todas las condiciones del mercado

        Args:
            data: DataFrame con OHLC y Volume

        Returns:
            Dict con análisis completo
        """
        try:
            market_type = self.detect_market_type(data)
            volatility = self.detect_volatility(data)
            momentum = self.analyze_momentum(data)

            # Calcular score general de tradabilidad
            tradability_score = 0

            # Mercado tendencial = mejor para trading
            if market_type['type'] == 'trending':
                tradability_score += 30

            # Volatilidad normal = ideal
            if volatility['level'] == 'normal':
                tradability_score += 30
            elif volatility['level'] == 'low':
                tradability_score += 20

            # Momentum fuerte = mejor
            if 'strong' in momentum['strength']:
                tradability_score += 40

            return {
                'market_type': market_type,
                'volatility': volatility,
                'momentum': momentum,
                'tradability_score': tradability_score,
                'recommendation': self._get_trading_recommendation(tradability_score),
                'timestamp': pd.Timestamp.now()
            }

        except Exception as e:
            print(f"Error en análisis completo: {e}")
            return {
                'tradability_score': 0,
                'recommendation': 'avoid'
            }

    def _get_trading_recommendation(self, score: int) -> str:
        """
        Genera recomendación de trading según score

        Args:
            score: Score de tradabilidad (0-100)

        Returns:
            Recomendación: 'excellent', 'good', 'fair', 'poor', 'avoid'
        """
        if score >= 80:
            return 'excellent'
        elif score >= 60:
            return 'good'
        elif score >= 40:
            return 'fair'
        elif score >= 20:
            return 'poor'
        else:
            return 'avoid'

    # ========================================================================
    # AJUSTES DINÁMICOS
    # ========================================================================

    def get_dynamic_adjustments(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calcula todos los ajustes dinámicos a aplicar

        Args:
            data: DataFrame con OHLC

        Returns:
            Dict con todos los ajustes multiplicadores
        """
        analysis = self.get_full_market_analysis(data)

        market_adj = analysis['market_type']['adjustments']
        vol_adj = analysis['volatility']['adjustments']

        return {
            'confidence_boost': market_adj.get('confidence_boost', 0),
            'position_size_multiplier': (
                market_adj.get('position_size_multiplier', 1.0) *
                vol_adj.get('reduce_position_size', 1.0)
            ),
            'stop_loss_multiplier': vol_adj.get('increase_stops', 1.0),
            'take_profit_multiplier': 1.0  # Mantener TP constante por ahora
        }


# ============================================================================
# FUNCIÓN DE PRUEBA
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("PRUEBA DE DETECCIÓN DE CONDICIONES DE MERCADO")
    print("=" * 70)

    import yfinance as yf

    print("\n📊 Descargando datos de prueba...")
    data = yf.download('EURUSD=X', period='60d', interval='1h', progress=False)

    if not data.empty:
        detector = MarketConditionDetector()

        print("\n🔍 Analizando condiciones de mercado...")
        analysis = detector.get_full_market_analysis(data)

        print(f"\n📈 Tipo de mercado: {analysis['market_type']['type']}")
        print(f"📊 Dirección: {analysis['market_type']['direction']}")
        print(f"💹 ADX: {analysis['market_type']['adx']:.2f}")
        print(f"📉 Volatilidad: {analysis['volatility']['level']}")
        print(f"⚡ Momentum: {analysis['momentum']['strength']}")
        print(f"🎯 Score tradabilidad: {analysis['tradability_score']}/100")
        print(f"💡 Recomendación: {analysis['recommendation'].upper()}")

        print(f"\n🎲 Estrategias preferidas:")
        for strategy in analysis['market_type']['preferred_strategies']:
            print(f"  - {strategy}")

        print(f"\n⚙️ Ajustes dinámicos:")
        adjustments = detector.get_dynamic_adjustments(data)
        for key, value in adjustments.items():
            print(f"  - {key}: {value}")

        print("\n✅ Detector funcionando correctamente")
    else:
        print("❌ No se pudieron descargar datos")
