"""
CLAUDE ADVANCED BOT - CONECTOR METATRADER 5
============================================
Conexión y ejecución de trades en MetaTrader 5
"""

import MetaTrader5 as mt5
from datetime import datetime
from typing import Dict, Optional, Tuple
import time


class MT5Connector:
    """Conecta y ejecuta trades en MetaTrader 5"""

    def __init__(self, account: int, password: str, server: str):
        """
        Inicializa conexión MT5

        Args:
            account: Número de cuenta MT5
            password: Contraseña
            server: Servidor del broker
        """
        self.account = account
        self.password = password
        self.server = server
        self.connected = False
        self.magic_number = 234000  # Identificador único del bot

    # ========================================================================
    # CONEXIÓN
    # ========================================================================

    def connect(self) -> Tuple[bool, str]:
        """
        Conecta a MetaTrader 5

        Returns:
            (conectado, mensaje)
        """
        try:
            # Inicializar MT5
            if not mt5.initialize():
                error = mt5.last_error()
                return False, f"MT5 initialize() falló: {error}"

            print(f"✅ MT5 inicializado")
            print(f"   Versión: {mt5.version()}")

            # Login
            authorized = mt5.login(
                login=self.account,
                password=self.password,
                server=self.server
            )

            if not authorized:
                error = mt5.last_error()
                mt5.shutdown()
                return False, f"Login falló: {error}"

            # Verificar cuenta
            account_info = mt5.account_info()
            if account_info is None:
                mt5.shutdown()
                return False, "No se pudo obtener info de cuenta"

            self.connected = True

            info_msg = f"""
✅ CONECTADO A MT5

Cuenta:   {account_info.login}
Broker:   {account_info.company}
Servidor: {account_info.server}
Balance:  ${account_info.balance:.2f}
Equity:   ${account_info.equity:.2f}
Margen:   ${account_info.margin:.2f}
Libre:    ${account_info.margin_free:.2f}
Nivel:    {account_info.margin_level:.2f}%

Modo:     {'DEMO' if account_info.trade_mode == 0 else 'REAL'}
"""
            return True, info_msg

        except Exception as e:
            return False, f"Error conectando: {e}"

    def disconnect(self):
        """Desconecta de MT5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            print("🔌 Desconectado de MT5")

    def check_connection(self) -> bool:
        """Verifica si la conexión está activa"""
        if not self.connected:
            return False

        try:
            account_info = mt5.account_info()
            return account_info is not None
        except:
            return False

    # ========================================================================
    # INFORMACIÓN DE CUENTA
    # ========================================================================

    def get_account_info(self) -> Optional[Dict]:
        """
        Obtiene información de la cuenta

        Returns:
            Dict con info de cuenta o None
        """
        try:
            info = mt5.account_info()
            if info is None:
                return None

            return {
                'login': info.login,
                'balance': info.balance,
                'equity': info.equity,
                'margin': info.margin,
                'margin_free': info.margin_free,
                'margin_level': info.margin_level,
                'profit': info.profit,
                'currency': info.currency,
                'leverage': info.leverage,
                'company': info.company,
                'server': info.server,
                'trade_mode': 'DEMO' if info.trade_mode == 0 else 'REAL'
            }
        except Exception as e:
            print(f"Error obteniendo info cuenta: {e}")
            return None

    # ========================================================================
    # INFORMACIÓN DE SÍMBOLOS
    # ========================================================================

    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """
        Obtiene información de un símbolo

        Args:
            symbol: Símbolo (ej: "EURUSD")

        Returns:
            Dict con info del símbolo o None
        """
        try:
            # Seleccionar símbolo
            if not mt5.symbol_select(symbol, True):
                print(f"⚠️ No se pudo seleccionar {symbol}")
                return None

            info = mt5.symbol_info(symbol)
            if info is None:
                return None

            return {
                'name': info.name,
                'bid': info.bid,
                'ask': info.ask,
                'spread': info.spread,
                'point': info.point,
                'digits': info.digits,
                'volume_min': info.volume_min,
                'volume_max': info.volume_max,
                'volume_step': info.volume_step,
                'trade_contract_size': info.trade_contract_size,
                'trade_mode': info.trade_mode
            }
        except Exception as e:
            print(f"Error obteniendo info símbolo: {e}")
            return None

    # ========================================================================
    # EJECUCIÓN DE TRADES
    # ========================================================================

    def open_trade(self, symbol: str, trade_type: str, volume: float,
                   sl: float, tp: float, comment: str = "") -> Dict:
        """
        Abre un trade en MT5

        Args:
            symbol: Símbolo (ej: "EURUSD")
            trade_type: "BUY" o "SELL"
            volume: Lotes (ej: 0.01 = micro lot)
            sl: Stop loss
            tp: Take profit
            comment: Comentario del trade

        Returns:
            Dict con resultado del trade
        """
        if not self.connected:
            return {'success': False, 'error': 'No conectado a MT5'}

        try:
            # Obtener info del símbolo
            symbol_info = self.get_symbol_info(symbol)
            if symbol_info is None:
                return {'success': False, 'error': f'Símbolo {symbol} no disponible'}

            # Precio actual
            if trade_type == "BUY":
                price = symbol_info['ask']
                order_type = mt5.ORDER_TYPE_BUY
            else:  # SELL
                price = symbol_info['bid']
                order_type = mt5.ORDER_TYPE_SELL

            # Normalizar volumen
            volume_min = symbol_info['volume_min']
            volume_max = symbol_info['volume_max']
            volume_step = symbol_info['volume_step']

            volume = max(volume_min, min(volume, volume_max))
            volume = round(volume / volume_step) * volume_step

            # Normalizar SL/TP
            point = symbol_info['point']
            digits = symbol_info['digits']

            sl = round(sl, digits)
            tp = round(tp, digits)

            # Crear request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "magic": self.magic_number,
                "comment": comment[:31],  # MT5 limita a 31 caracteres
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            # Enviar orden
            result = mt5.order_send(request)

            if result is None:
                error = mt5.last_error()
                return {'success': False, 'error': f'order_send falló: {error}'}

            # Verificar resultado
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return {
                    'success': False,
                    'error': f'Trade rechazado: {result.comment}',
                    'retcode': result.retcode
                }

            return {
                'success': True,
                'ticket': result.order,
                'volume': result.volume,
                'price': result.price,
                'bid': result.bid,
                'ask': result.ask,
                'comment': result.comment
            }

        except Exception as e:
            return {'success': False, 'error': f'Excepción: {e}'}

    def close_trade(self, ticket: int) -> Dict:
        """
        Cierra un trade por ticket

        Args:
            ticket: Número de ticket del trade

        Returns:
            Dict con resultado
        """
        if not self.connected:
            return {'success': False, 'error': 'No conectado a MT5'}

        try:
            # Obtener posición
            position = mt5.positions_get(ticket=ticket)

            if position is None or len(position) == 0:
                return {'success': False, 'error': f'Posición {ticket} no encontrada'}

            position = position[0]

            # Determinar tipo de orden opuesta
            if position.type == mt5.ORDER_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(position.symbol).bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(position.symbol).ask

            # Crear request de cierre
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": order_type,
                "position": ticket,
                "price": price,
                "magic": self.magic_number,
                "comment": "Close by bot",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            # Enviar orden
            result = mt5.order_send(request)

            if result is None:
                error = mt5.last_error()
                return {'success': False, 'error': f'Cierre falló: {error}'}

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return {
                    'success': False,
                    'error': f'Cierre rechazado: {result.comment}',
                    'retcode': result.retcode
                }

            return {
                'success': True,
                'ticket': ticket,
                'price': result.price,
                'comment': result.comment
            }

        except Exception as e:
            return {'success': False, 'error': f'Excepción: {e}'}

    # ========================================================================
    # GESTIÓN DE POSICIONES
    # ========================================================================

    def get_open_positions(self) -> list:
        """
        Obtiene todas las posiciones abiertas

        Returns:
            Lista de posiciones abiertas
        """
        if not self.connected:
            return []

        try:
            positions = mt5.positions_get()

            if positions is None:
                return []

            result = []
            for pos in positions:
                result.append({
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'BUY' if pos.type == 0 else 'SELL',
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'price_current': pos.price_current,
                    'sl': pos.sl,
                    'tp': pos.tp,
                    'profit': pos.profit,
                    'magic': pos.magic,
                    'comment': pos.comment,
                    'time': datetime.fromtimestamp(pos.time)
                })

            return result

        except Exception as e:
            print(f"Error obteniendo posiciones: {e}")
            return []

    def get_positions_count(self) -> int:
        """Cuenta posiciones abiertas"""
        return len(self.get_open_positions())

    # ========================================================================
    # TRAILING STOP
    # ========================================================================

    def update_trailing_stop(self, ticket: int, new_sl: float) -> Dict:
        """
        Actualiza el stop loss de una posición (trailing stop)

        Args:
            ticket: Ticket de la posición
            new_sl: Nuevo stop loss

        Returns:
            Dict con resultado
        """
        if not self.connected:
            return {'success': False, 'error': 'No conectado'}

        try:
            # Obtener posición
            positions = mt5.positions_get(ticket=ticket)

            if positions is None or len(positions) == 0:
                return {'success': False, 'error': f'Posición {ticket} no encontrada'}

            position = positions[0]

            # Normalizar SL
            symbol_info = self.get_symbol_info(position.symbol)
            new_sl = round(new_sl, symbol_info['digits'])

            # Crear request de modificación
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "sl": new_sl,
                "tp": position.tp,
                "position": ticket
            }

            # Enviar modificación
            result = mt5.order_send(request)

            if result is None:
                error = mt5.last_error()
                return {'success': False, 'error': f'Modificación falló: {error}'}

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return {
                    'success': False,
                    'error': f'Modificación rechazada: {result.comment}',
                    'retcode': result.retcode
                }

            return {
                'success': True,
                'ticket': ticket,
                'new_sl': new_sl,
                'comment': result.comment
            }

        except Exception as e:
            return {'success': False, 'error': f'Excepción: {e}'}

    # ========================================================================
    # CONVERSIÓN DE SÍMBOLOS
    # ========================================================================

    def convert_symbol(self, yahoo_symbol: str) -> str:
        """
        Convierte símbolo Yahoo a MT5

        Args:
            yahoo_symbol: Símbolo de Yahoo Finance (ej: "EURUSD=X")

        Returns:
            Símbolo MT5 (ej: "EURUSD")
        """
        # Remover sufijos
        symbol = yahoo_symbol.replace('=X', '')
        symbol = symbol.replace('/', '')

        # Mapeo específico si es necesario
        mapping = {
            'EURUSD': 'EURUSD',
            'GBPUSD': 'GBPUSD',
            'USDJPY': 'USDJPY'
        }

        return mapping.get(symbol, symbol)

    # ========================================================================
    # CÁLCULO DE LOTES
    # ========================================================================

    def calculate_lot_size(self, symbol: str, risk_amount: float,
                          sl_pips: float) -> float:
        """
        Calcula tamaño de lote basado en riesgo

        Args:
            symbol: Símbolo
            risk_amount: Cantidad a arriesgar en USD
            sl_pips: Stop loss en pips

        Returns:
            Tamaño de lote
        """
        try:
            symbol_info = self.get_symbol_info(symbol)
            if symbol_info is None:
                return symbol_info['volume_min']

            # Valor del pip
            point = symbol_info['point']
            contract_size = symbol_info['trade_contract_size']

            # Para forex, valor pip = point * contract_size
            pip_value = point * 10 * contract_size  # 10 porque pip = 10 points

            # Lot size = risk / (sl_pips * pip_value)
            lot_size = risk_amount / (sl_pips * pip_value)

            # Normalizar
            volume_min = symbol_info['volume_min']
            volume_max = symbol_info['volume_max']
            volume_step = symbol_info['volume_step']

            lot_size = max(volume_min, min(lot_size, volume_max))
            lot_size = round(lot_size / volume_step) * volume_step

            return lot_size

        except Exception as e:
            print(f"Error calculando lot size: {e}")
            return 0.01  # Micro lot por defecto


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("TEST DE CONEXIÓN MT5")
    print("=" * 70)

    # Crear conector
    mt5_connector = MT5Connector(
        account=206895,
        password="Xpuerta08!",
        server="FusionMarkets_demo"
    )

    # Conectar
    print("\n🔌 Conectando a MT5...")
    success, message = mt5_connector.connect()

    if success:
        print(message)

        # Info cuenta
        print("\n📊 Información de cuenta:")
        account_info = mt5_connector.get_account_info()
        if account_info:
            for key, value in account_info.items():
                print(f"  {key}: {value}")

        # Info símbolo
        print("\n💱 Información EURUSD:")
        symbol_info = mt5_connector.get_symbol_info("EURUSD")
        if symbol_info:
            for key, value in symbol_info.items():
                print(f"  {key}: {value}")

        # Posiciones abiertas
        print("\n📈 Posiciones abiertas:")
        positions = mt5_connector.get_open_positions()
        if positions:
            for pos in positions:
                print(f"  Ticket: {pos['ticket']} | {pos['symbol']} | "
                      f"{pos['type']} | Profit: ${pos['profit']:.2f}")
        else:
            print("  No hay posiciones abiertas")

        # Desconectar
        mt5_connector.disconnect()
        print("\n✅ Test completado")

    else:
        print(f"\n❌ Error: {message}")
