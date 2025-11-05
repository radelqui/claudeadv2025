"""
CLAUDE TRADING BOT - CONFIGURACIÓN CENTRALIZADA
================================================
Configuración optimizada para trading automatizado de alto rendimiento
"""

import os
from typing import Dict, Any

# ============================================================================
# CONFIGURACIÓN DE API Y COMUNICACIÓN
# ============================================================================

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', "7718630865:AAEMclwlqzuxb5uFPqX9dyJLo7ib19QnJt8")
CHAT_ID = os.environ.get('CHAT_ID', "5358902915")

# ============================================================================
# PARES DE TRADING
# ============================================================================

TRADING_PAIRS = {
    'EURUSD=X': {
        'nombre': 'EUR/USD',
        'pip': 0.0001,
        'spread': 0.00015,  # Spread típico en pips
        'min_move': 0.00001,
        'commission': 0.00002  # 0.2 pips comisión por lado
    },
    'GBPUSD=X': {
        'nombre': 'GBP/USD',
        'pip': 0.0001,
        'spread': 0.0002,
        'min_move': 0.00001,
        'commission': 0.00002
    },
    'USDJPY=X': {
        'nombre': 'USD/JPY',
        'pip': 0.01,
        'spread': 0.015,
        'min_move': 0.001,
        'commission': 0.002
    }
}

# ============================================================================
# CONFIGURACIÓN DE INDICADORES TÉCNICOS
# ============================================================================

INDICATORS_CONFIG = {
    # RSI - Optimizado según Linda Raschke (30% menos señales falsas)
    'RSI': {
        'period': 9,
        'overbought': 75,
        'oversold': 25,
        'extreme_overbought': 85,
        'extreme_oversold': 15
    },

    # MACD Linda Raschke (40% más rápido que estándar)
    'MACD': {
        'fast': 3,
        'slow': 10,
        'signal': 16
    },

    # Bollinger Bands
    'BOLLINGER': {
        'period': 20,
        'std_dev': 2.0,
        'squeeze_threshold': 0.05  # Para detectar consolidación
    },

    # EMAs para Multi-Timeframe
    'EMA': {
        'fast': 9,
        'medium': 21,
        'slow': 50,
        'very_slow': 200
    },

    # ADX - Average Directional Index (detecta fuerza de tendencia)
    'ADX': {
        'period': 14,
        'trending_threshold': 25,  # ADX > 25 = tendencia fuerte
        'strong_trend': 40,         # ADX > 40 = tendencia muy fuerte
        'weak_trend': 20            # ADX < 20 = mercado lateral
    },

    # ATR - Average True Range (volatilidad)
    'ATR': {
        'period': 14,
        'multiplier_sl': 2.0,   # Stop loss = 2x ATR
        'multiplier_tp': 4.0,   # Take profit = 4x ATR
        'multiplier_trail': 3.0  # Trailing stop = 3x ATR
    },

    # Volume Analysis
    'VOLUME': {
        'ma_period': 20,
        'surge_multiplier': 2.5,  # Volume surge = 2.5x promedio
        'dry_threshold': 0.5      # Volume seco = 0.5x promedio
    },

    # Stochastic Oscillator
    'STOCHASTIC': {
        'k_period': 14,
        'd_period': 3,
        'overbought': 80,
        'oversold': 20
    },

    # Fibonacci Retracements
    'FIBONACCI': {
        'lookback': 100,  # Velas para buscar swing high/low
        'levels': [0.236, 0.382, 0.5, 0.618, 0.786]
    }
}

# ============================================================================
# GESTIÓN DE RIESGO
# ============================================================================

RISK_CONFIG = {
    # Kelly Criterion
    'use_kelly': True,
    'kelly_fraction': 0.25,  # 1/4 Kelly para reducir volatilidad
    'max_position_size': 0.02,  # Máximo 2% del capital por trade
    'min_position_size': 0.005,  # Mínimo 0.5% del capital por trade

    # Stop Loss y Take Profit
    'default_sl_pips': 20,
    'default_tp_pips': 50,
    'use_atr_stops': True,  # Usar ATR para stops dinámicos
    'risk_reward_ratio': 2.5,  # Mínimo RR ratio aceptable

    # Trailing Stops
    'use_trailing_stops': True,
    'trailing_activation': 0.5,  # Activar al 50% del TP
    'trailing_distance_pct': 0.3,  # Trail a 30% del profit

    # Límites de Exposición
    'max_daily_trades': 10,
    'max_weekly_trades': 30,
    'max_open_positions': 3,
    'max_correlation_positions': 2,  # Max 2 trades en pares correlacionados

    # Drawdown Protection
    'max_daily_loss_pct': 0.05,  # Stop trading si pérdida > 5% diaria
    'max_drawdown_pct': 0.20,     # Stop trading si drawdown > 20%

    # Capital inicial (para backtesting y paper trading)
    'initial_capital': 10000,
    'currency': 'USD'
}

# ============================================================================
# ESTRATEGIAS DE TRADING
# ============================================================================

STRATEGIES_CONFIG = {
    # Requiere consenso de mínimo 2 estrategias
    'consensus_required': 2,
    'min_confidence': 60,  # Confianza mínima en %

    # Pesos de estrategias (para calcular confianza ponderada)
    'strategy_weights': {
        'RSI_MACD_REVERSION': 1.0,
        'SMART_MONEY_CONCEPTS': 0.9,
        'MULTI_TIMEFRAME': 1.0,
        'MEAN_REVERSION': 0.85,
        'MOMENTUM_BREAKOUT': 0.95,
        'TREND_FOLLOWING': 1.0
    },

    # Habilitar/deshabilitar estrategias
    'enabled_strategies': [
        'RSI_MACD_REVERSION',
        'SMART_MONEY_CONCEPTS',
        'MULTI_TIMEFRAME',
        'MEAN_REVERSION',
        'MOMENTUM_BREAKOUT',
        'TREND_FOLLOWING'
    ]
}

# ============================================================================
# CONDICIONES DE MERCADO
# ============================================================================

MARKET_CONDITIONS_CONFIG = {
    # Tipos de mercado
    'detect_market_type': True,

    # Umbral para clasificación
    'trending_adx': 25,
    'ranging_adx': 20,

    # Ajustes por condición
    'trending_market': {
        'preferred_strategies': ['MOMENTUM_BREAKOUT', 'TREND_FOLLOWING', 'MULTI_TIMEFRAME'],
        'confidence_boost': 5,  # +5% confianza en mercado tendencial
        'position_size_multiplier': 1.2
    },

    'ranging_market': {
        'preferred_strategies': ['RSI_MACD_REVERSION', 'MEAN_REVERSION'],
        'confidence_boost': 5,
        'position_size_multiplier': 0.8
    },

    'volatile_market': {
        'reduce_position_size': 0.5,  # 50% del tamaño normal
        'increase_stops': 1.5         # 150% del stop normal
    }
}

# ============================================================================
# BACKTESTING
# ============================================================================

BACKTEST_CONFIG = {
    'start_date': '2023-01-01',
    'end_date': '2025-01-01',
    'initial_capital': 10000,
    'data_interval': '1h',
    'commission': 0.0002,  # 0.2 pips por lado
    'slippage': 0.0001,    # 1 pip de slippage

    # Optimización de parámetros
    'optimize_parameters': True,
    'optimization_method': 'grid_search',  # 'grid_search' o 'random'
    'n_trials': 100,  # Para random search

    # Parámetros a optimizar
    'param_ranges': {
        'rsi_period': [7, 9, 11, 14],
        'rsi_overbought': [70, 75, 80],
        'rsi_oversold': [20, 25, 30],
        'macd_fast': [3, 5, 8],
        'macd_slow': [10, 12, 15],
        'bb_std': [1.5, 2.0, 2.5],
        'adx_threshold': [20, 25, 30]
    }
}

# ============================================================================
# PAPER TRADING
# ============================================================================

PAPER_TRADING_CONFIG = {
    'enabled': False,  # Cambiar a True para paper trading
    'initial_capital': 10000,
    'save_trades': True,
    'trades_file': 'paper_trades.json',
    'realistic_slippage': True,
    'realistic_spreads': True
}

# ============================================================================
# LOGGING Y PERSISTENCIA
# ============================================================================

LOGGING_CONFIG = {
    'log_level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'log_to_file': True,
    'log_file': 'trading_bot.log',
    'max_log_size': 10 * 1024 * 1024,  # 10 MB
    'backup_count': 5,

    # Persistencia
    'save_state': True,
    'state_file': 'bot_state.json',
    'save_trades': True,
    'trades_file': 'trades_history.json',
    'save_performance': True,
    'performance_file': 'performance_metrics.json'
}

# ============================================================================
# CONFIGURACIÓN DE DATOS
# ============================================================================

DATA_CONFIG = {
    'source': 'yfinance',
    'default_period': '5d',
    'default_interval': '1h',
    'min_data_points': 30,
    'max_retries': 3,
    'retry_delay': 2,
    'validate_data': True,
    'repair_data': True,
    'cache_data': True,
    'cache_duration': 300  # 5 minutos
}

# ============================================================================
# CONFIGURACIÓN DE EJECUCIÓN
# ============================================================================

EXECUTION_CONFIG = {
    'mode': 'production',  # 'production', 'paper', 'backtest'
    'scan_interval': 300,  # 5 minutos
    'startup_delay': 5,
    'shutdown_graceful': True,
    'max_consecutive_errors': 5,

    # Horario de trading (UTC)
    'trading_hours': {
        'enabled': False,  # 24/7 por defecto
        'start_hour': 0,
        'end_hour': 24,
        'skip_weekends': False
    }
}

# ============================================================================
# ALERTAS Y NOTIFICACIONES
# ============================================================================

ALERTS_CONFIG = {
    'telegram_enabled': True,
    'alert_on_signal': True,
    'alert_on_trade': True,
    'alert_on_error': True,
    'alert_on_milestone': True,  # 10 trades, 100 trades, etc.

    # Niveles de alerta
    'alert_levels': {
        'INFO': True,
        'WARNING': True,
        'CRITICAL': True
    },

    # Resumen periódico
    'daily_summary': True,
    'weekly_summary': True,
    'summary_hour': 20  # 8 PM UTC
}

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def get_config(section: str = None) -> Dict[str, Any]:
    """
    Obtiene configuración por sección o completa

    Args:
        section: Nombre de la sección (None para toda la config)

    Returns:
        Diccionario con la configuración
    """
    config_map = {
        'telegram': {'token': TELEGRAM_TOKEN, 'chat_id': CHAT_ID},
        'pairs': TRADING_PAIRS,
        'indicators': INDICATORS_CONFIG,
        'risk': RISK_CONFIG,
        'strategies': STRATEGIES_CONFIG,
        'market': MARKET_CONDITIONS_CONFIG,
        'backtest': BACKTEST_CONFIG,
        'paper': PAPER_TRADING_CONFIG,
        'logging': LOGGING_CONFIG,
        'data': DATA_CONFIG,
        'execution': EXECUTION_CONFIG,
        'alerts': ALERTS_CONFIG
    }

    if section is None:
        return config_map

    return config_map.get(section, {})


def validate_config() -> bool:
    """
    Valida que la configuración sea correcta

    Returns:
        True si la configuración es válida
    """
    errors = []

    # Validar tokens
    if not TELEGRAM_TOKEN or len(TELEGRAM_TOKEN) < 10:
        errors.append("TELEGRAM_TOKEN inválido")

    # Validar risk management
    if RISK_CONFIG['max_position_size'] <= RISK_CONFIG['min_position_size']:
        errors.append("max_position_size debe ser mayor que min_position_size")

    if RISK_CONFIG['kelly_fraction'] <= 0 or RISK_CONFIG['kelly_fraction'] > 1:
        errors.append("kelly_fraction debe estar entre 0 y 1")

    # Validar estrategias
    if STRATEGIES_CONFIG['consensus_required'] < 1:
        errors.append("consensus_required debe ser al menos 1")

    # Mostrar errores
    if errors:
        print("⚠️ Errores de configuración:")
        for error in errors:
            print(f"  - {error}")
        return False

    return True


if __name__ == "__main__":
    print("=" * 70)
    print("VALIDANDO CONFIGURACIÓN DEL BOT DE TRADING")
    print("=" * 70)

    if validate_config():
        print("✅ Configuración válida")
        print(f"\n📊 Pares configurados: {len(TRADING_PAIRS)}")
        print(f"🎯 Estrategias activas: {len(STRATEGIES_CONFIG['enabled_strategies'])}")
        print(f"💰 Capital inicial: ${RISK_CONFIG['initial_capital']:,}")
        print(f"🎲 Kelly fraction: {RISK_CONFIG['kelly_fraction']}")
        print(f"⚡ Modo: {EXECUTION_CONFIG['mode']}")
        print(f"📈 Paper trading: {'✅' if PAPER_TRADING_CONFIG['enabled'] else '❌'}")
    else:
        print("❌ Configuración inválida")
        exit(1)
