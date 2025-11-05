"""
CLAUDE TRADING BOT - GESTIÓN DE RIESGO AVANZADA
================================================
Sistema profesional de gestión de riesgo con Kelly Criterion,
trailing stops dinámicos y protección de capital
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from config import RISK_CONFIG, TRADING_PAIRS
from indicators import TechnicalIndicators


class RiskManager:
    """Gestión avanzada de riesgo para trading algorítmico"""

    def __init__(self, initial_capital: float = None):
        """
        Inicializa el gestor de riesgo

        Args:
            initial_capital: Capital inicial (usa config si es None)
        """
        self.config = RISK_CONFIG
        self.indicators = TechnicalIndicators()

        self.capital = initial_capital if initial_capital else self.config['initial_capital']
        self.initial_capital = self.capital
        self.peak_capital = self.capital

        # Tracking
        self.daily_pnl = 0
        self.total_pnl = 0
        self.daily_trades = 0
        self.open_positions = []
        self.trade_history = []

    # ========================================================================
    # KELLY CRITERION - POSITION SIZING ÓPTIMO
    # ========================================================================

    def calculate_kelly_size(self, win_rate: float, avg_win: float,
                           avg_loss: float) -> float:
        """
        Calcula tamaño de posición óptimo usando Kelly Criterion

        Kelly% = (Win_Rate * Avg_Win - (1 - Win_Rate) * Avg_Loss) / Avg_Win

        Ejemplo:
        - Win Rate = 60%
        - Avg Win = $150
        - Avg Loss = $100
        - Kelly = (0.6 * 150 - 0.4 * 100) / 150 = 0.333 (33.3%)

        Args:
            win_rate: Tasa de éxito histórica (0-1)
            avg_win: Ganancia promedio por trade ganador
            avg_loss: Pérdida promedio por trade perdedor (positivo)

        Returns:
            Porcentaje del capital a arriesgar (0-1)
        """
        try:
            if win_rate <= 0 or win_rate >= 1:
                return self.config['min_position_size']

            if avg_win <= 0 or avg_loss <= 0:
                return self.config['min_position_size']

            # Kelly Criterion Formula
            kelly_pct = ((win_rate * avg_win) - ((1 - win_rate) * avg_loss)) / avg_win

            # Aplicar Kelly Fraction (1/4 Kelly para reducir volatilidad)
            adjusted_kelly = kelly_pct * self.config['kelly_fraction']

            # Limitar entre min y max
            position_size = np.clip(
                adjusted_kelly,
                self.config['min_position_size'],
                self.config['max_position_size']
            )

            return float(position_size)

        except Exception as e:
            print(f"Error calculando Kelly: {e}")
            return self.config['min_position_size']

    def calculate_position_size(self, symbol: str, direction: str,
                               win_rate: float = 0.65,
                               avg_win: float = 50,
                               avg_loss: float = 20,
                               volatility_multiplier: float = 1.0) -> Dict[str, float]:
        """
        Calcula tamaño de posición considerando múltiples factores

        Args:
            symbol: Par de trading
            direction: 'BUY' o 'SELL'
            win_rate: Tasa de éxito histórica
            avg_win: Ganancia promedio en pips
            avg_loss: Pérdida promedio en pips
            volatility_multiplier: Ajuste por volatilidad (de market_conditions)

        Returns:
            Dict con detalles del tamaño de posición
        """
        try:
            # Kelly position size
            if self.config['use_kelly']:
                kelly_size = self.calculate_kelly_size(win_rate, avg_win, avg_loss)
            else:
                kelly_size = self.config['max_position_size']

            # Ajustar por volatilidad
            adjusted_size = kelly_size * volatility_multiplier

            # Limitar
            final_size = np.clip(
                adjusted_size,
                self.config['min_position_size'],
                self.config['max_position_size']
            )

            # Calcular tamaño en unidades monetarias
            risk_amount = self.capital * final_size

            # Obtener info del par
            pair_info = TRADING_PAIRS.get(symbol, {})
            pip_value = pair_info.get('pip', 0.0001)

            return {
                'kelly_percent': kelly_size,
                'adjusted_percent': adjusted_size,
                'final_percent': final_size,
                'risk_amount': risk_amount,
                'capital': self.capital,
                'volatility_adj': volatility_multiplier
            }

        except Exception as e:
            print(f"Error calculando position size: {e}")
            return {
                'final_percent': self.config['min_position_size'],
                'risk_amount': self.capital * self.config['min_position_size']
            }

    # ========================================================================
    # STOP LOSS Y TAKE PROFIT
    # ========================================================================

    def calculate_stops(self, data: pd.DataFrame, symbol: str,
                       direction: str, entry_price: float,
                       use_atr: bool = True) -> Dict[str, float]:
        """
        Calcula stop-loss y take-profit óptimos

        Args:
            data: DataFrame con OHLC
            symbol: Par de trading
            direction: 'BUY' o 'SELL'
            entry_price: Precio de entrada
            use_atr: Usar ATR para stops dinámicos

        Returns:
            Dict con SL, TP y distancias
        """
        try:
            pair_info = TRADING_PAIRS.get(symbol, {})
            pip = pair_info.get('pip', 0.0001)

            if use_atr and self.config['use_atr_stops']:
                # Stops basados en ATR (volatilidad)
                atr_stops = self.indicators.get_atr_stops(data, direction)
                sl = atr_stops['stop_loss']
                tp = atr_stops['take_profit']
            else:
                # Stops fijos del config
                sl_pips = self.config['default_sl_pips']
                tp_pips = self.config['default_tp_pips']

                if direction == 'BUY':
                    sl = entry_price - (sl_pips * pip)
                    tp = entry_price + (tp_pips * pip)
                else:  # SELL
                    sl = entry_price + (sl_pips * pip)
                    tp = entry_price - (tp_pips * pip)

            # Calcular distancias
            sl_distance = abs(entry_price - sl)
            tp_distance = abs(tp - entry_price)

            # Risk/Reward Ratio
            rr_ratio = tp_distance / sl_distance if sl_distance > 0 else 0

            # Verificar que cumple RR mínimo
            min_rr = self.config['risk_reward_ratio']
            if rr_ratio < min_rr:
                print(f"⚠️ RR ratio {rr_ratio:.2f} < mínimo {min_rr}")
                # Ajustar TP para cumplir RR mínimo
                tp_distance = sl_distance * min_rr
                if direction == 'BUY':
                    tp = entry_price + tp_distance
                else:
                    tp = entry_price - tp_distance

            return {
                'stop_loss': sl,
                'take_profit': tp,
                'sl_distance': sl_distance,
                'tp_distance': tp_distance,
                'sl_pips': sl_distance / pip,
                'tp_pips': tp_distance / pip,
                'risk_reward': rr_ratio,
                'method': 'ATR' if use_atr else 'Fixed'
            }

        except Exception as e:
            print(f"Error calculando stops: {e}")
            return self._get_default_stops(symbol, direction, entry_price)

    def _get_default_stops(self, symbol: str, direction: str,
                          entry_price: float) -> Dict[str, float]:
        """Stops por defecto en caso de error"""
        pair_info = TRADING_PAIRS.get(symbol, {})
        pip = pair_info.get('pip', 0.0001)

        sl_pips = self.config['default_sl_pips']
        tp_pips = self.config['default_tp_pips']

        if direction == 'BUY':
            sl = entry_price - (sl_pips * pip)
            tp = entry_price + (tp_pips * pip)
        else:
            sl = entry_price + (sl_pips * pip)
            tp = entry_price - (tp_pips * pip)

        return {
            'stop_loss': sl,
            'take_profit': tp,
            'sl_pips': sl_pips,
            'tp_pips': tp_pips,
            'risk_reward': tp_pips / sl_pips,
            'method': 'Default'
        }

    # ========================================================================
    # TRAILING STOPS DINÁMICOS
    # ========================================================================

    def calculate_trailing_stop(self, entry_price: float, current_price: float,
                               direction: str, stop_loss: float,
                               take_profit: float) -> Optional[float]:
        """
        Calcula trailing stop dinámico

        El trailing stop se activa cuando el precio alcanza cierto % del TP,
        y luego sigue al precio manteniendo una distancia fija.

        Args:
            entry_price: Precio de entrada
            current_price: Precio actual
            direction: 'BUY' o 'SELL'
            stop_loss: Stop loss original
            take_profit: Take profit

        Returns:
            Nuevo nivel de trailing stop (None si no activado)
        """
        try:
            if not self.config['use_trailing_stops']:
                return None

            tp_distance = abs(take_profit - entry_price)
            current_profit = abs(current_price - entry_price)

            # Activar trailing cuando alcanza % del TP
            activation_threshold = tp_distance * self.config['trailing_activation']

            if current_profit < activation_threshold:
                return None  # No activado aún

            # Calcular distancia del trail
            trail_distance = current_profit * self.config['trailing_distance_pct']

            if direction == 'BUY':
                # Trail sube con el precio
                trailing_stop = current_price - trail_distance
                # No bajar nunca el stop
                return max(trailing_stop, stop_loss)
            else:  # SELL
                # Trail baja con el precio
                trailing_stop = current_price + trail_distance
                # No subir nunca el stop
                return min(trailing_stop, stop_loss)

        except Exception as e:
            print(f"Error calculando trailing stop: {e}")
            return None

    # ========================================================================
    # VALIDACIÓN DE TRADES
    # ========================================================================

    def can_open_trade(self, symbol: str) -> Tuple[bool, str]:
        """
        Verifica si se puede abrir un nuevo trade

        Args:
            symbol: Par de trading

        Returns:
            (puede_tradear, razón)
        """
        # Check 1: Límite diario de trades
        if self.daily_trades >= self.config['max_daily_trades']:
            return False, f"Límite diario alcanzado ({self.config['max_daily_trades']})"

        # Check 2: Pérdida diaria máxima
        daily_loss_pct = abs(self.daily_pnl) / self.initial_capital
        if self.daily_pnl < 0 and daily_loss_pct >= self.config['max_daily_loss_pct']:
            return False, f"Pérdida diaria máxima alcanzada ({daily_loss_pct*100:.1f}%)"

        # Check 3: Drawdown máximo
        drawdown = (self.peak_capital - self.capital) / self.peak_capital
        if drawdown >= self.config['max_drawdown_pct']:
            return False, f"Drawdown máximo alcanzado ({drawdown*100:.1f}%)"

        # Check 4: Posiciones abiertas máximas
        if len(self.open_positions) >= self.config['max_open_positions']:
            return False, f"Máximo de posiciones abiertas ({self.config['max_open_positions']})"

        # Check 5: Capital suficiente
        min_capital = self.initial_capital * 0.5  # No operar con menos del 50%
        if self.capital < min_capital:
            return False, f"Capital insuficiente (${self.capital:.2f})"

        return True, "OK"

    def validate_trade(self, symbol: str, direction: str, entry_price: float,
                      stop_loss: float, take_profit: float,
                      confidence: float) -> Tuple[bool, str]:
        """
        Validación completa de un trade antes de ejecutar

        Args:
            symbol: Par de trading
            direction: 'BUY' o 'SELL'
            entry_price: Precio de entrada
            stop_loss: Stop loss
            take_profit: Take profit
            confidence: Confianza de la señal (0-100)

        Returns:
            (es_válido, razón)
        """
        # Check básicos
        can_trade, reason = self.can_open_trade(symbol)
        if not can_trade:
            return False, reason

        # Validar precios
        if entry_price <= 0 or stop_loss <= 0 or take_profit <= 0:
            return False, "Precios inválidos"

        # Validar dirección del SL y TP
        if direction == 'BUY':
            if stop_loss >= entry_price:
                return False, "SL debe estar por debajo del precio en BUY"
            if take_profit <= entry_price:
                return False, "TP debe estar por encima del precio en BUY"
        else:  # SELL
            if stop_loss <= entry_price:
                return False, "SL debe estar por encima del precio en SELL"
            if take_profit >= entry_price:
                return False, "TP debe estar por debajo del precio en SELL"

        # Validar Risk/Reward
        sl_distance = abs(entry_price - stop_loss)
        tp_distance = abs(take_profit - entry_price)
        rr_ratio = tp_distance / sl_distance if sl_distance > 0 else 0

        if rr_ratio < self.config['risk_reward_ratio']:
            return False, f"RR ratio {rr_ratio:.2f} < mínimo {self.config['risk_reward_ratio']}"

        return True, "Trade válido"

    # ========================================================================
    # REGISTRO DE TRADES
    # ========================================================================

    def open_trade(self, symbol: str, direction: str, entry_price: float,
                  stop_loss: float, take_profit: float, size: float,
                  confidence: float, strategies: list) -> Dict:
        """
        Registra apertura de trade

        Args:
            symbol: Par de trading
            direction: 'BUY' o 'SELL'
            entry_price: Precio de entrada
            stop_loss: Stop loss
            take_profit: Take profit
            size: Tamaño de la posición (% del capital)
            confidence: Confianza de la señal
            strategies: Lista de estrategias que confirmaron

        Returns:
            Dict con información del trade
        """
        trade = {
            'id': len(self.trade_history) + 1,
            'symbol': symbol,
            'direction': direction,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'size_pct': size,
            'risk_amount': self.capital * size,
            'confidence': confidence,
            'strategies': strategies,
            'status': 'open',
            'entry_time': pd.Timestamp.now(),
            'exit_time': None,
            'exit_price': None,
            'pnl': 0,
            'pnl_pct': 0
        }

        self.open_positions.append(trade)
        self.trade_history.append(trade)
        self.daily_trades += 1

        return trade

    def close_trade(self, trade_id: int, exit_price: float,
                   reason: str = 'TP/SL') -> Optional[Dict]:
        """
        Registra cierre de trade y actualiza capital

        Args:
            trade_id: ID del trade
            exit_price: Precio de salida
            reason: Razón del cierre

        Returns:
            Dict con resultado del trade
        """
        # Buscar trade
        trade = None
        for t in self.open_positions:
            if t['id'] == trade_id:
                trade = t
                break

        if not trade:
            return None

        # Calcular PnL
        direction_multiplier = 1 if trade['direction'] == 'BUY' else -1
        price_diff = (exit_price - trade['entry_price']) * direction_multiplier
        pnl_pct = price_diff / trade['entry_price']
        pnl_amount = trade['risk_amount'] * pnl_pct

        # Actualizar trade
        trade['exit_price'] = exit_price
        trade['exit_time'] = pd.Timestamp.now()
        trade['pnl'] = pnl_amount
        trade['pnl_pct'] = pnl_pct
        trade['status'] = 'closed'
        trade['exit_reason'] = reason

        # Actualizar capital
        self.capital += pnl_amount
        self.daily_pnl += pnl_amount
        self.total_pnl += pnl_amount

        # Actualizar peak capital
        if self.capital > self.peak_capital:
            self.peak_capital = self.capital

        # Remover de posiciones abiertas
        self.open_positions = [t for t in self.open_positions if t['id'] != trade_id]

        return trade

    # ========================================================================
    # MÉTRICAS DE PERFORMANCE
    # ========================================================================

    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Calcula métricas de performance del trading

        Returns:
            Dict con métricas clave
        """
        closed_trades = [t for t in self.trade_history if t['status'] == 'closed']

        if not closed_trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'roi': 0
            }

        winning_trades = [t for t in closed_trades if t['pnl'] > 0]
        losing_trades = [t for t in closed_trades if t['pnl'] < 0]

        win_rate = len(winning_trades) / len(closed_trades) if closed_trades else 0
        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([abs(t['pnl']) for t in losing_trades]) if losing_trades else 0

        # ROI
        roi = (self.capital - self.initial_capital) / self.initial_capital

        # Profit Factor
        total_wins = sum([t['pnl'] for t in winning_trades])
        total_losses = sum([abs(t['pnl']) for t in losing_trades])
        profit_factor = total_wins / total_losses if total_losses > 0 else 0

        # Drawdown
        drawdown = (self.peak_capital - self.capital) / self.peak_capital

        return {
            'total_trades': len(closed_trades),
            'open_positions': len(self.open_positions),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'total_pnl': self.total_pnl,
            'daily_pnl': self.daily_pnl,
            'roi': roi,
            'profit_factor': profit_factor,
            'current_capital': self.capital,
            'peak_capital': self.peak_capital,
            'drawdown': drawdown
        }

    def reset_daily_stats(self):
        """Resetea estadísticas diarias"""
        self.daily_trades = 0
        self.daily_pnl = 0


# ============================================================================
# FUNCIÓN DE PRUEBA
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("PRUEBA DE GESTIÓN DE RIESGO")
    print("=" * 70)

    rm = RiskManager(initial_capital=10000)

    print(f"\n💰 Capital inicial: ${rm.capital:,.2f}")

    # Test 1: Kelly Criterion
    print("\n📊 Test Kelly Criterion:")
    kelly = rm.calculate_kelly_size(win_rate=0.65, avg_win=50, avg_loss=20)
    print(f"Kelly position size: {kelly*100:.2f}%")

    # Test 2: Position sizing
    print("\n📊 Test Position Sizing:")
    pos_size = rm.calculate_position_size('EURUSD=X', 'BUY')
    print(f"Tamaño recomendado: {pos_size['final_percent']*100:.2f}%")
    print(f"Monto a arriesgar: ${pos_size['risk_amount']:.2f}")

    # Test 3: Validación
    print("\n✅ Test Validación:")
    can_trade, reason = rm.can_open_trade('EURUSD=X')
    print(f"¿Puede tradear? {can_trade} - {reason}")

    # Test 4: Métricas
    print("\n📈 Métricas de Performance:")
    metrics = rm.get_performance_metrics()
    print(f"Total trades: {metrics['total_trades']}")
    print(f"Win rate: {metrics['win_rate']*100:.1f}%")
    print(f"ROI: {metrics['roi']*100:.1f}%")

    print("\n✅ Risk Manager funcionando correctamente")
