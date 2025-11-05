"""
CLAUDE ADVANCED BOT - SISTEMA DE BACKTESTING
=============================================
Backtesting completo con datos históricos para validar estrategias
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json
import warnings
warnings.filterwarnings('ignore')

from config import *
from indicators import TechnicalIndicators
from market_conditions import MarketConditionDetector
from risk_management import RiskManager


class Backtester:
    """Sistema completo de backtesting para validar estrategias"""

    def __init__(self, start_date: str = '2023-01-01', end_date: str = '2025-01-01',
                 initial_capital: float = 10000):
        """
        Inicializa el backtester

        Args:
            start_date: Fecha inicio formato 'YYYY-MM-DD'
            end_date: Fecha fin formato 'YYYY-MM-DD'
            initial_capital: Capital inicial
        """
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital

        # Componentes
        self.indicators = TechnicalIndicators()
        self.market_detector = MarketConditionDetector()
        self.risk_manager = RiskManager(initial_capital)

        # Resultados
        self.trades = []
        self.equity_curve = []
        self.metrics = {}

        print(f"Backtester inicializado: {start_date} a {end_date}")
        print(f"Capital inicial: ${initial_capital:,.2f}")

    # ========================================================================
    # DESCARGA DE DATOS HISTÓRICOS
    # ========================================================================

    def fetch_historical_data(self, symbol: str) -> pd.DataFrame:
        """
        Descarga datos históricos para backtesting

        Args:
            symbol: Par de trading

        Returns:
            DataFrame con OHLCV histórico
        """
        try:
            import yfinance as yf

            print(f"\n📊 Descargando datos históricos: {symbol}")
            print(f"   Período: {self.start_date} a {self.end_date}")

            data = yf.download(
                symbol,
                start=self.start_date,
                end=self.end_date,
                interval='1h',
                progress=False,
                auto_adjust=True
            )

            if data.empty:
                print(f"❌ No hay datos para {symbol}")
                return None

            print(f"✅ Descargados {len(data)} velas (1h)")
            return data

        except Exception as e:
            print(f"❌ Error descargando {symbol}: {e}")
            return None

    # ========================================================================
    # IMPLEMENTACIÓN DE ESTRATEGIAS (igual que el bot)
    # ========================================================================

    def strategy_rsi_macd_reversion(self, data: pd.DataFrame, i: int) -> Dict:
        """Estrategia 1: RSI + MACD + Bollinger"""
        try:
            # Necesitamos al menos 30 velas anteriores
            if i < 30:
                return None

            window_data = data.iloc[:i+1]

            rsi = self.indicators.calculate_rsi(window_data)
            macd, signal, _ = self.indicators.calculate_macd(window_data)
            upper, middle, lower = self.indicators.calculate_bollinger_bands(window_data)

            if macd is None or upper is None:
                return None

            price = float(window_data['Close'].iloc[-1])
            rsi_val = float(rsi.iloc[-1])

            config = INDICATORS_CONFIG['RSI']

            # BUY
            if (rsi_val < config['oversold'] and
                price < float(lower.iloc[-1]) and
                float(macd.iloc[-1]) > float(signal.iloc[-1])):
                return {'direction': 'BUY', 'confidence': 73, 'strategy': 'RSI_MACD_REVERSION'}

            # SELL
            elif (rsi_val > config['overbought'] and
                  price > float(upper.iloc[-1]) and
                  float(macd.iloc[-1]) < float(signal.iloc[-1])):
                return {'direction': 'SELL', 'confidence': 73, 'strategy': 'RSI_MACD_REVERSION'}

        except:
            pass

        return None

    def strategy_multi_timeframe(self, data: pd.DataFrame, i: int) -> Dict:
        """Estrategia 3: Multi-Timeframe"""
        try:
            if i < 50:
                return None

            window_data = data.iloc[:i+1]

            ema9 = self.indicators.calculate_ema(window_data, 9)
            ema21 = self.indicators.calculate_ema(window_data, 21)
            rsi = self.indicators.calculate_rsi(window_data)

            trend_bullish = float(ema9.iloc[-1]) > float(ema21.iloc[-1])
            trend_bearish = float(ema9.iloc[-1]) < float(ema21.iloc[-1])
            rsi_val = float(rsi.iloc[-1])

            if trend_bullish and rsi_val < 40:
                return {'direction': 'BUY', 'confidence': 75, 'strategy': 'MULTI_TIMEFRAME'}
            elif trend_bearish and rsi_val > 60:
                return {'direction': 'SELL', 'confidence': 75, 'strategy': 'MULTI_TIMEFRAME'}

        except:
            pass

        return None

    def strategy_mean_reversion(self, data: pd.DataFrame, i: int) -> Dict:
        """Estrategia 4: Mean Reversion"""
        try:
            if i < 50:
                return None

            window_data = data.iloc[:i+1]
            close = window_data['Close']

            sma50 = close.rolling(50).mean()
            std = close.rolling(50).std()

            price = float(close.iloc[-1])
            mean = float(sma50.iloc[-1])
            std_val = float(std.iloc[-1])

            z_score = (price - mean) / std_val if std_val > 0 else 0

            if z_score < -2:
                return {'direction': 'BUY', 'confidence': 65, 'strategy': 'MEAN_REVERSION'}
            elif z_score > 2:
                return {'direction': 'SELL', 'confidence': 65, 'strategy': 'MEAN_REVERSION'}

        except:
            pass

        return None

    def strategy_trend_following(self, data: pd.DataFrame, i: int) -> Dict:
        """Estrategia 6: Trend Following con ADX"""
        try:
            if i < 50:
                return None

            window_data = data.iloc[:i+1]

            # ADX
            adx, di_plus, di_minus = self.indicators.calculate_adx(window_data)
            if adx is None:
                return None

            adx_val = float(adx.iloc[-1])

            # Solo operar si ADX > 25 (tendencia)
            if adx_val < INDICATORS_CONFIG['ADX']['trending_threshold']:
                return None

            # EMAs
            ema21 = self.indicators.calculate_ema(window_data, 21)
            ema50 = self.indicators.calculate_ema(window_data, 50)

            ema21_val = float(ema21.iloc[-1])
            ema50_val = float(ema50.iloc[-1])

            di_plus_val = float(di_plus.iloc[-1])
            di_minus_val = float(di_minus.iloc[-1])

            # BUY
            if di_plus_val > di_minus_val and ema21_val > ema50_val:
                confidence = 72 + (8 if adx_val > 40 else 0)
                return {'direction': 'BUY', 'confidence': min(95, confidence), 'strategy': 'TREND_FOLLOWING'}

            # SELL
            elif di_minus_val > di_plus_val and ema21_val < ema50_val:
                confidence = 72 + (8 if adx_val > 40 else 0)
                return {'direction': 'SELL', 'confidence': min(95, confidence), 'strategy': 'TREND_FOLLOWING'}

        except:
            pass

        return None

    # ========================================================================
    # ANÁLISIS Y EJECUCIÓN DE TRADES
    # ========================================================================

    def analyze_signals(self, data: pd.DataFrame, i: int) -> Dict:
        """
        Analiza todas las estrategias y genera consenso

        Args:
            data: DataFrame completo
            i: Índice actual (vela)

        Returns:
            Señal de trading o None
        """
        signals = []

        # Ejecutar estrategias
        s1 = self.strategy_rsi_macd_reversion(data, i)
        if s1:
            signals.append(s1)

        s2 = self.strategy_multi_timeframe(data, i)
        if s2:
            signals.append(s2)

        s3 = self.strategy_mean_reversion(data, i)
        if s3:
            signals.append(s3)

        s4 = self.strategy_trend_following(data, i)
        if s4:
            signals.append(s4)

        if not signals:
            return None

        # CONSENSO: Mínimo 2 estrategias
        buy_signals = [s for s in signals if s['direction'] == 'BUY']
        sell_signals = [s for s in signals if s['direction'] == 'SELL']

        consensus_req = STRATEGIES_CONFIG['consensus_required']

        if len(buy_signals) >= consensus_req:
            avg_confidence = np.mean([s['confidence'] for s in buy_signals])
            return {
                'direction': 'BUY',
                'confidence': avg_confidence,
                'strategies': [s['strategy'] for s in buy_signals],
                'n_strategies': len(buy_signals)
            }
        elif len(sell_signals) >= consensus_req:
            avg_confidence = np.mean([s['confidence'] for s in sell_signals])
            return {
                'direction': 'SELL',
                'confidence': avg_confidence,
                'strategies': [s['strategy'] for s in sell_signals],
                'n_strategies': len(sell_signals)
            }

        return None

    def execute_trade(self, signal: Dict, entry_data: pd.DataFrame,
                     entry_idx: int, full_data: pd.DataFrame) -> Dict:
        """
        Ejecuta un trade simulado

        Args:
            signal: Señal de trading
            entry_data: Datos hasta el punto de entrada
            entry_idx: Índice de entrada
            full_data: Todos los datos (para simular el futuro)

        Returns:
            Resultado del trade
        """
        entry_price = float(entry_data['Close'].iloc[-1])
        entry_time = entry_data.index[-1]

        # Calcular stops con ATR
        atr_stops = self.indicators.get_atr_stops(entry_data, signal['direction'])

        sl = atr_stops['stop_loss']
        tp = atr_stops['take_profit']

        # Simular el trade (mirar velas futuras)
        max_hold = 100  # Máximo 100 velas (100 horas)
        exit_price = None
        exit_reason = None
        exit_idx = None

        for j in range(entry_idx + 1, min(entry_idx + max_hold, len(full_data))):
            bar = full_data.iloc[j]

            if signal['direction'] == 'BUY':
                # Check stop loss
                if bar['Low'] <= sl:
                    exit_price = sl
                    exit_reason = 'SL'
                    exit_idx = j
                    break
                # Check take profit
                elif bar['High'] >= tp:
                    exit_price = tp
                    exit_reason = 'TP'
                    exit_idx = j
                    break
            else:  # SELL
                # Check stop loss
                if bar['High'] >= sl:
                    exit_price = sl
                    exit_reason = 'SL'
                    exit_idx = j
                    break
                # Check take profit
                elif bar['Low'] <= tp:
                    exit_price = tp
                    exit_reason = 'TP'
                    exit_idx = j
                    break

        # Si no alcanzó TP/SL, cerrar al precio actual
        if exit_price is None:
            exit_idx = min(entry_idx + max_hold, len(full_data) - 1)
            exit_price = float(full_data.iloc[exit_idx]['Close'])
            exit_reason = 'TIMEOUT'

        # Calcular PnL
        if signal['direction'] == 'BUY':
            pnl_pct = (exit_price - entry_price) / entry_price
        else:
            pnl_pct = (entry_price - exit_price) / entry_price

        # Position size (simplificado - 1% del capital)
        position_size = 0.01
        pnl_amount = self.risk_manager.capital * position_size * pnl_pct

        # Actualizar capital
        self.risk_manager.capital += pnl_amount

        return {
            'entry_time': entry_time,
            'entry_price': entry_price,
            'exit_time': full_data.index[exit_idx],
            'exit_price': exit_price,
            'exit_reason': exit_reason,
            'direction': signal['direction'],
            'pnl_pct': pnl_pct * 100,
            'pnl_amount': pnl_amount,
            'capital': self.risk_manager.capital,
            'confidence': signal['confidence'],
            'strategies': signal['strategies']
        }

    # ========================================================================
    # EJECUCIÓN DEL BACKTEST
    # ========================================================================

    def run(self, symbol: str = 'EURUSD=X') -> Dict:
        """
        Ejecuta el backtest completo

        Args:
            symbol: Par a testear

        Returns:
            Resultados del backtest
        """
        print(f"\n{'='*70}")
        print(f"INICIANDO BACKTEST: {symbol}")
        print(f"{'='*70}")

        # Descargar datos
        data = self.fetch_historical_data(symbol)
        if data is None or len(data) < 100:
            print("❌ Datos insuficientes")
            return None

        print(f"\n🔍 Analizando {len(data)} velas...")

        # Resetear
        self.trades = []
        self.equity_curve = [self.initial_capital]
        self.risk_manager.capital = self.initial_capital

        # Escanear cada vela
        trades_count = 0
        for i in range(100, len(data)):
            # Equity curve
            self.equity_curve.append(self.risk_manager.capital)

            # Analizar señales
            signal = self.analyze_signals(data, i)

            if signal:
                # Ejecutar trade
                trade = self.execute_trade(signal, data.iloc[:i+1], i, data)
                self.trades.append(trade)
                trades_count += 1

                result_emoji = "✅" if trade['pnl_amount'] > 0 else "❌"
                print(f"{result_emoji} Trade #{trades_count}: {trade['direction']} | "
                      f"PnL: {trade['pnl_pct']:.2f}% (${trade['pnl_amount']:.2f}) | "
                      f"Capital: ${trade['capital']:.2f}")

        print(f"\n{'='*70}")
        print(f"BACKTEST COMPLETADO")
        print(f"{'='*70}")

        # Calcular métricas
        self.metrics = self.calculate_metrics()

        return self.metrics

    # ========================================================================
    # MÉTRICAS DE PERFORMANCE
    # ========================================================================

    def calculate_metrics(self) -> Dict:
        """Calcula todas las métricas de performance"""

        if not self.trades:
            return {'error': 'No trades'}

        trades_df = pd.DataFrame(self.trades)

        # Básicas
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['pnl_amount'] > 0])
        losing_trades = len(trades_df[trades_df['pnl_amount'] < 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        # PnL
        total_pnl = trades_df['pnl_amount'].sum()
        avg_win = trades_df[trades_df['pnl_amount'] > 0]['pnl_amount'].mean() if winning_trades > 0 else 0
        avg_loss = abs(trades_df[trades_df['pnl_amount'] < 0]['pnl_amount'].mean()) if losing_trades > 0 else 0

        # Profit Factor
        gross_profit = trades_df[trades_df['pnl_amount'] > 0]['pnl_amount'].sum()
        gross_loss = abs(trades_df[trades_df['pnl_amount'] < 0]['pnl_amount'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # ROI
        final_capital = self.risk_manager.capital
        roi = (final_capital - self.initial_capital) / self.initial_capital

        # Drawdown
        equity_series = pd.Series(self.equity_curve)
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max
        max_drawdown = abs(drawdown.min())

        # Sharpe Ratio (simplificado)
        returns = trades_df['pnl_pct'].values
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0

        # Sortino Ratio (solo downside deviation)
        negative_returns = returns[returns < 0]
        downside_std = negative_returns.std() if len(negative_returns) > 0 else returns.std()
        sortino_ratio = (returns.mean() / downside_std) * np.sqrt(252) if downside_std > 0 else 0

        # Expectancy
        expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)

        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'initial_capital': self.initial_capital,
            'final_capital': final_capital,
            'roi': roi,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'expectancy': expectancy,
            'best_trade': trades_df['pnl_amount'].max(),
            'worst_trade': trades_df['pnl_amount'].min()
        }

    def print_report(self):
        """Imprime reporte detallado"""
        m = self.metrics

        print(f"\n{'='*70}")
        print("📊 REPORTE DE BACKTEST")
        print(f"{'='*70}")

        print(f"\n💰 CAPITAL:")
        print(f"  Inicial:      ${m['initial_capital']:,.2f}")
        print(f"  Final:        ${m['final_capital']:,.2f}")
        print(f"  Ganancia:     ${m['total_pnl']:,.2f}")
        print(f"  ROI:          {m['roi']*100:.2f}%")

        print(f"\n📈 TRADES:")
        print(f"  Total:        {m['total_trades']}")
        print(f"  Ganadores:    {m['winning_trades']} ({m['win_rate']*100:.1f}%)")
        print(f"  Perdedores:   {m['losing_trades']}")

        print(f"\n💹 PERFORMANCE:")
        print(f"  Avg Win:      ${m['avg_win']:.2f}")
        print(f"  Avg Loss:     ${m['avg_loss']:.2f}")
        print(f"  Profit Factor: {m['profit_factor']:.2f}")
        print(f"  Expectancy:   ${m['expectancy']:.2f}")

        print(f"\n📊 MÉTRICAS AVANZADAS:")
        print(f"  Max Drawdown: {m['max_drawdown']*100:.2f}%")
        print(f"  Sharpe Ratio: {m['sharpe_ratio']:.2f}")
        print(f"  Sortino Ratio: {m['sortino_ratio']:.2f}")

        print(f"\n🎯 MEJORES/PEORES:")
        print(f"  Mejor Trade:  ${m['best_trade']:.2f}")
        print(f"  Peor Trade:   ${m['worst_trade']:.2f}")

        # Evaluación
        print(f"\n{'='*70}")
        print("📋 EVALUACIÓN:")
        print(f"{'='*70}")

        issues = []
        if m['win_rate'] < 0.50:
            issues.append("⚠️  Win rate bajo (<50%)")
        if m['profit_factor'] < 1.5:
            issues.append("⚠️  Profit factor bajo (<1.5)")
        if m['max_drawdown'] > 0.20:
            issues.append("⚠️  Drawdown alto (>20%)")
        if m['sharpe_ratio'] < 1.0:
            issues.append("⚠️  Sharpe ratio bajo (<1.0)")

        if not issues:
            print("✅ Estrategia ACEPTABLE para trading en vivo")
            print("✅ Todas las métricas cumplen estándares profesionales")
        else:
            print("❌ Estrategia necesita OPTIMIZACIÓN antes de usar en vivo:")
            for issue in issues:
                print(f"   {issue}")

        print(f"{'='*70}\n")

    def save_results(self, filename: str = 'backtest_results.json'):
        """Guarda resultados en JSON"""
        results = {
            'metrics': self.metrics,
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }

        # Convertir datetime a string
        for trade in results['trades']:
            trade['entry_time'] = str(trade['entry_time'])
            trade['exit_time'] = str(trade['exit_time'])

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"💾 Resultados guardados en: {filename}")


# ============================================================================
# EJECUTAR BACKTEST
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("CLAUDE ADVANCED BOT - BACKTEST CON DATOS HISTÓRICOS")
    print("="*70)

    # Crear backtester
    backtester = Backtester(
        start_date='2023-01-01',
        end_date='2024-12-31',
        initial_capital=10000
    )

    # Ejecutar backtest
    results = backtester.run('EURUSD=X')

    if results:
        # Mostrar reporte
        backtester.print_report()

        # Guardar resultados
        backtester.save_results('backtest_results.json')

        print("\n✅ BACKTEST COMPLETADO")
    else:
        print("\n❌ BACKTEST FALLÓ")
