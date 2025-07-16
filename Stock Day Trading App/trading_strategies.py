"""
Trading Strategies Module
Contains various automated trading strategies and technical analysis functions.
"""

import pandas as pd
import numpy as np
import yfinance as yf
import ta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Signal:
    """Trading signal data structure"""
    symbol: str
    action: str  # 'BUY', 'SELL', 'HOLD'
    strength: float  # 0.0 to 1.0
    price: float
    timestamp: datetime
    strategy: str
    reason: str
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class TechnicalIndicators:
    """Technical analysis indicators"""
    
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        return ta.momentum.RSIIndicator(data['Close'], window=period).rsi()
    
    @staticmethod
    def calculate_macd(data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD"""
        macd = ta.trend.MACD(data['Close'], window_fast=fast, window_slow=slow, window_sign=signal)
        return macd.macd(), macd.macd_signal(), macd.macd_diff()
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.DataFrame, period: int = 20, std: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        bb = ta.volatility.BollingerBands(data['Close'], window=period, window_dev=std)
        return bb.bollinger_hband(), bb.bollinger_lband(), bb.bollinger_mavg()
    
    @staticmethod
    def calculate_moving_averages(data: pd.DataFrame, periods: List[int]) -> Dict[str, pd.Series]:
        """Calculate multiple moving averages"""
        ma_dict = {}
        for period in periods:
            ma_dict[f'SMA_{period}'] = ta.trend.SMAIndicator(data['Close'], window=period).sma_indicator()
            ma_dict[f'EMA_{period}'] = ta.trend.EMAIndicator(data['Close'], window=period).ema_indicator()
        return ma_dict
    
    @staticmethod
    def calculate_stochastic(data: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator"""
        stoch = ta.momentum.StochasticOscillator(data['High'], data['Low'], data['Close'], 
                                                window=k_period, smooth_window=d_period)
        return stoch.stoch(), stoch.stoch_signal()
    
    @staticmethod
    def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        return ta.volatility.AverageTrueRange(data['High'], data['Low'], data['Close'], window=period).average_true_range()

class TradingStrategies:
    """Trading strategy implementations"""
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
        
    def scalping_strategy(self, symbol: str, timeframe: str = "1m") -> Signal:
        """
        Scalping strategy based on short-term momentum and volatility
        """
        try:
            # Get recent data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1h", interval=timeframe)
            
            if len(data) < 50:
                return Signal(symbol, "HOLD", 0.0, data['Close'].iloc[-1], datetime.now(), "SCALPING", "Insufficient data")
            
            # Calculate indicators
            rsi = self.indicators.calculate_rsi(data)
            macd, macd_signal, macd_diff = self.indicators.calculate_macd(data)
            bb_upper, bb_lower, bb_middle = self.indicators.calculate_bollinger_bands(data)
            atr = self.indicators.calculate_atr(data)
            
            current_price = data['Close'].iloc[-1]
            current_rsi = rsi.iloc[-1]
            current_macd = macd.iloc[-1]
            current_macd_signal = macd_signal.iloc[-1]
            current_atr = atr.iloc[-1]
            
            # Scalping logic
            signal_strength = 0.0
            action = "HOLD"
            reason = ""
            
            # RSI conditions
            if current_rsi < 30:
                signal_strength += 0.3
                reason += "Oversold RSI; "
            elif current_rsi > 70:
                signal_strength -= 0.3
                reason += "Overbought RSI; "
            
            # MACD conditions
            if current_macd > current_macd_signal and macd_diff.iloc[-1] > 0:
                signal_strength += 0.3
                reason += "MACD bullish crossover; "
            elif current_macd < current_macd_signal and macd_diff.iloc[-1] < 0:
                signal_strength -= 0.3
                reason += "MACD bearish crossover; "
            
            # Bollinger Bands conditions
            if current_price < bb_lower.iloc[-1]:
                signal_strength += 0.2
                reason += "Price below lower BB; "
            elif current_price > bb_upper.iloc[-1]:
                signal_strength -= 0.2
                reason += "Price above upper BB; "
            
            # Volume confirmation
            if data['Volume'].iloc[-1] > data['Volume'].rolling(10).mean().iloc[-1]:
                signal_strength += 0.2
                reason += "High volume; "
            
            # Determine action
            if signal_strength >= 0.5:
                action = "BUY"
                stop_loss = current_price - (current_atr * 2)
                take_profit = current_price + (current_atr * 3)
            elif signal_strength <= -0.5:
                action = "SELL"
                stop_loss = current_price + (current_atr * 2)
                take_profit = current_price - (current_atr * 3)
            else:
                action = "HOLD"
                stop_loss = None
                take_profit = None
            
            return Signal(
                symbol=symbol,
                action=action,
                strength=abs(signal_strength),
                price=current_price,
                timestamp=datetime.now(),
                strategy="SCALPING",
                reason=reason.strip(),
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
        except Exception as e:
            logger.error(f"Error in scalping strategy: {e}")
            return Signal(symbol, "HOLD", 0.0, 0.0, datetime.now(), "SCALPING", f"Error: {e}")
    
    def swing_trading_strategy(self, symbol: str, timeframe: str = "1h") -> Signal:
        """
        Swing trading strategy based on trend following and support/resistance
        """
        try:
            # Get historical data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="30d", interval=timeframe)
            
            if len(data) < 100:
                return Signal(symbol, "HOLD", 0.0, data['Close'].iloc[-1], datetime.now(), "SWING", "Insufficient data")
            
            # Calculate indicators
            ma_dict = self.indicators.calculate_moving_averages(data, [20, 50, 200])
            rsi = self.indicators.calculate_rsi(data, period=14)
            macd, macd_signal, macd_diff = self.indicators.calculate_macd(data)
            
            current_price = data['Close'].iloc[-1]
            sma_20 = ma_dict['SMA_20'].iloc[-1]
            sma_50 = ma_dict['SMA_50'].iloc[-1]
            sma_200 = ma_dict['SMA_200'].iloc[-1]
            current_rsi = rsi.iloc[-1]
            
            # Swing trading logic
            signal_strength = 0.0
            action = "HOLD"
            reason = ""
            
            # Trend analysis
            if current_price > sma_20 > sma_50 > sma_200:
                signal_strength += 0.4
                reason += "Strong uptrend; "
            elif current_price < sma_20 < sma_50 < sma_200:
                signal_strength -= 0.4
                reason += "Strong downtrend; "
            
            # RSI conditions
            if 40 < current_rsi < 60:
                signal_strength += 0.2
                reason += "Neutral RSI; "
            elif current_rsi < 30:
                signal_strength += 0.3
                reason += "Oversold RSI; "
            elif current_rsi > 70:
                signal_strength -= 0.3
                reason += "Overbought RSI; "
            
            # MACD trend confirmation
            if macd_diff.iloc[-1] > 0 and macd_diff.iloc[-2] < 0:
                signal_strength += 0.3
                reason += "MACD turning positive; "
            elif macd_diff.iloc[-1] < 0 and macd_diff.iloc[-2] > 0:
                signal_strength -= 0.3
                reason += "MACD turning negative; "
            
            # Support/Resistance levels
            recent_high = data['High'].rolling(20).max().iloc[-1]
            recent_low = data['Low'].rolling(20).min().iloc[-1]
            
            if current_price > recent_high * 0.98:
                signal_strength += 0.2
                reason += "Breaking resistance; "
            elif current_price < recent_low * 1.02:
                signal_strength -= 0.2
                reason += "Breaking support; "
            
            # Determine action
            if signal_strength >= 0.6:
                action = "BUY"
                stop_loss = sma_50
                take_profit = current_price + (current_price - sma_50) * 2
            elif signal_strength <= -0.6:
                action = "SELL"
                stop_loss = sma_50
                take_profit = current_price - (sma_50 - current_price) * 2
            else:
                action = "HOLD"
                stop_loss = None
                take_profit = None
            
            return Signal(
                symbol=symbol,
                action=action,
                strength=abs(signal_strength),
                price=current_price,
                timestamp=datetime.now(),
                strategy="SWING",
                reason=reason.strip(),
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
        except Exception as e:
            logger.error(f"Error in swing trading strategy: {e}")
            return Signal(symbol, "HOLD", 0.0, 0.0, datetime.now(), "SWING", f"Error: {e}")
    
    def mean_reversion_strategy(self, symbol: str, timeframe: str = "15m") -> Signal:
        """
        Mean reversion strategy based on Bollinger Bands and RSI
        """
        try:
            # Get historical data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="5d", interval=timeframe)
            
            if len(data) < 50:
                return Signal(symbol, "HOLD", 0.0, data['Close'].iloc[-1], datetime.now(), "MEAN_REVERSION", "Insufficient data")
            
            # Calculate indicators
            bb_upper, bb_lower, bb_middle = self.indicators.calculate_bollinger_bands(data)
            rsi = self.indicators.calculate_rsi(data)
            stoch_k, stoch_d = self.indicators.calculate_stochastic(data)
            
            current_price = data['Close'].iloc[-1]
            current_bb_upper = bb_upper.iloc[-1]
            current_bb_lower = bb_lower.iloc[-1]
            current_bb_middle = bb_middle.iloc[-1]
            current_rsi = rsi.iloc[-1]
            current_stoch_k = stoch_k.iloc[-1]
            current_stoch_d = stoch_d.iloc[-1]
            
            # Mean reversion logic
            signal_strength = 0.0
            action = "HOLD"
            reason = ""
            
            # Bollinger Bands mean reversion
            bb_position = (current_price - current_bb_lower) / (current_bb_upper - current_bb_lower)
            
            if bb_position < 0.1:  # Near lower band
                signal_strength += 0.4
                reason += "Price near lower BB; "
            elif bb_position > 0.9:  # Near upper band
                signal_strength -= 0.4
                reason += "Price near upper BB; "
            
            # RSI mean reversion
            if current_rsi < 30:
                signal_strength += 0.3
                reason += "Oversold RSI; "
            elif current_rsi > 70:
                signal_strength -= 0.3
                reason += "Overbought RSI; "
            
            # Stochastic mean reversion
            if current_stoch_k < 20 and current_stoch_d < 20:
                signal_strength += 0.2
                reason += "Oversold stochastic; "
            elif current_stoch_k > 80 and current_stoch_d > 80:
                signal_strength -= 0.2
                reason += "Overbought stochastic; "
            
            # Volume confirmation
            avg_volume = data['Volume'].rolling(10).mean().iloc[-1]
            if data['Volume'].iloc[-1] > avg_volume * 1.5:
                signal_strength += 0.1
                reason += "High volume; "
            
            # Determine action
            if signal_strength >= 0.6:
                action = "BUY"
                stop_loss = current_bb_lower
                take_profit = current_bb_middle
            elif signal_strength <= -0.6:
                action = "SELL"
                stop_loss = current_bb_upper
                take_profit = current_bb_middle
            else:
                action = "HOLD"
                stop_loss = None
                take_profit = None
            
            return Signal(
                symbol=symbol,
                action=action,
                strength=abs(signal_strength),
                price=current_price,
                timestamp=datetime.now(),
                strategy="MEAN_REVERSION",
                reason=reason.strip(),
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
        except Exception as e:
            logger.error(f"Error in mean reversion strategy: {e}")
            return Signal(symbol, "HOLD", 0.0, 0.0, datetime.now(), "MEAN_REVERSION", f"Error: {e}")
    
    def breakout_strategy(self, symbol: str, timeframe: str = "1h") -> Signal:
        """
        Breakout strategy based on support/resistance levels and volume
        """
        try:
            # Get historical data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="30d", interval=timeframe)
            
            if len(data) < 100:
                return Signal(symbol, "HOLD", 0.0, data['Close'].iloc[-1], datetime.now(), "BREAKOUT", "Insufficient data")
            
            # Calculate indicators
            bb_upper, bb_lower, bb_middle = self.indicators.calculate_bollinger_bands(data)
            atr = self.indicators.calculate_atr(data)
            ma_dict = self.indicators.calculate_moving_averages(data, [20, 50])
            
            current_price = data['Close'].iloc[-1]
            current_bb_upper = bb_upper.iloc[-1]
            current_bb_lower = bb_lower.iloc[-1]
            current_atr = atr.iloc[-1]
            sma_20 = ma_dict['SMA_20'].iloc[-1]
            sma_50 = ma_dict['SMA_50'].iloc[-1]
            
            # Breakout logic
            signal_strength = 0.0
            action = "HOLD"
            reason = ""
            
            # Identify support and resistance levels
            recent_high = data['High'].rolling(20).max().iloc[-1]
            recent_low = data['Low'].rolling(20).min().iloc[-1]
            
            # Breakout detection
            breakout_threshold = current_atr * 0.5
            
            # Bullish breakout
            if current_price > recent_high + breakout_threshold:
                signal_strength += 0.5
                reason += "Bullish breakout; "
            # Bearish breakout
            elif current_price < recent_low - breakout_threshold:
                signal_strength -= 0.5
                reason += "Bearish breakout; "
            
            # Volume confirmation
            avg_volume = data['Volume'].rolling(10).mean().iloc[-1]
            current_volume = data['Volume'].iloc[-1]
            
            if current_volume > avg_volume * 2:
                signal_strength += 0.3
                reason += "High volume breakout; "
            elif current_volume < avg_volume * 0.5:
                signal_strength -= 0.2
                reason += "Low volume; "
            
            # Trend confirmation
            if current_price > sma_20 > sma_50:
                signal_strength += 0.2
                reason += "Uptrend confirmation; "
            elif current_price < sma_20 < sma_50:
                signal_strength -= 0.2
                reason += "Downtrend confirmation; "
            
            # Bollinger Bands breakout
            if current_price > current_bb_upper:
                signal_strength += 0.2
                reason += "BB upper breakout; "
            elif current_price < current_bb_lower:
                signal_strength -= 0.2
                reason += "BB lower breakout; "
            
            # Determine action
            if signal_strength >= 0.7:
                action = "BUY"
                stop_loss = recent_high
                take_profit = current_price + (current_price - recent_high) * 2
            elif signal_strength <= -0.7:
                action = "SELL"
                stop_loss = recent_low
                take_profit = current_price - (recent_low - current_price) * 2
            else:
                action = "HOLD"
                stop_loss = None
                take_profit = None
            
            return Signal(
                symbol=symbol,
                action=action,
                strength=abs(signal_strength),
                price=current_price,
                timestamp=datetime.now(),
                strategy="BREAKOUT",
                reason=reason.strip(),
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
        except Exception as e:
            logger.error(f"Error in breakout strategy: {e}")
            return Signal(symbol, "HOLD", 0.0, 0.0, datetime.now(), "BREAKOUT", f"Error: {e}")
    
    def custom_strategy(self, symbol: str, strategy_config: Dict) -> Signal:
        """
        Custom strategy based on user-defined parameters
        """
        try:
            # Get data based on config
            ticker = yf.Ticker(symbol)
            period = strategy_config.get('period', '5d')
            interval = strategy_config.get('interval', '15m')
            data = ticker.history(period=period, interval=interval)
            
            if len(data) < 20:
                return Signal(symbol, "HOLD", 0.0, data['Close'].iloc[-1], datetime.now(), "CUSTOM", "Insufficient data")
            
            # Apply custom logic based on config
            current_price = data['Close'].iloc[-1]
            
            # Example custom logic (can be extended)
            rsi = self.indicators.calculate_rsi(data)
            current_rsi = rsi.iloc[-1]
            
            signal_strength = 0.0
            action = "HOLD"
            reason = "Custom strategy"
            
            # Simple custom logic
            if current_rsi < strategy_config.get('rsi_oversold', 30):
                signal_strength = 0.8
                action = "BUY"
            elif current_rsi > strategy_config.get('rsi_overbought', 70):
                signal_strength = 0.8
                action = "SELL"
            
            return Signal(
                symbol=symbol,
                action=action,
                strength=signal_strength,
                price=current_price,
                timestamp=datetime.now(),
                strategy="CUSTOM",
                reason=reason,
                stop_loss=None,
                take_profit=None
            )
            
        except Exception as e:
            logger.error(f"Error in custom strategy: {e}")
            return Signal(symbol, "HOLD", 0.0, 0.0, datetime.now(), "CUSTOM", f"Error: {e}")

class RiskManager:
    """Risk management utilities"""
    
    @staticmethod
    def calculate_position_size(account_balance: float, risk_per_trade: float, 
                              entry_price: float, stop_loss: float) -> int:
        """Calculate position size based on risk management rules"""
        if stop_loss is None or entry_price == stop_loss:
            return 0
        
        risk_amount = account_balance * (risk_per_trade / 100)
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return 0
        
        position_size = risk_amount / price_risk
        return int(position_size)
    
    @staticmethod
    def check_daily_loss_limit(current_pnl: float, daily_limit: float) -> bool:
        """Check if daily loss limit has been reached"""
        return current_pnl <= -daily_limit
    
    @staticmethod
    def calculate_portfolio_risk(trades: List, current_prices: Dict[str, float]) -> Dict:
        """Calculate current portfolio risk metrics"""
        total_value = 0
        total_pnl = 0
        max_drawdown = 0
        
        for trade in trades:
            if trade.status == 'EXECUTED':
                current_price = current_prices.get(trade.symbol, trade.price)
                position_value = trade.quantity * current_price
                position_pnl = (current_price - trade.price) * trade.quantity
                
                total_value += position_value
                total_pnl += position_pnl
                
                if position_pnl < max_drawdown:
                    max_drawdown = position_pnl
        
        return {
            'total_value': total_value,
            'total_pnl': total_pnl,
            'max_drawdown': max_drawdown,
            'return_percent': (total_pnl / total_value * 100) if total_value > 0 else 0
        }