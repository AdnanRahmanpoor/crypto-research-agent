import yfinance as yf
import pandas as pd
import ta
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def fetch_technical_indicators(symbol: str) -> Dict[str, Any]:
	"""
	Downloads historical price data and calculates technical indicators.
	Tool used by: Technical Analysis Agent.
	"""
	yf_symbol = f"{symbol.upper()}-USD"

	try:
		# fetch 6months of daily data
		ticker = yf.Ticker(yf_symbol)
		df = ticker.history(period="6mo")

		if df.empty:
			return {"error": f"No historical data found for {yf_symbol}"}

		# calculate indicators using the 'ta' lib
		# 1. RSI
		df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()

		# 2. MACD
		macd = ta.trend.MACD(close=df['Close'])
		df['MACD'] = macd.macd()
		df['MACD_Signal'] = macd.macd_signal()

		# 3. MA
		df['SMA_50'] = ta.trend.SMAIndicator(close=df['Close'], window=50).sma_indicator()
		df['SMA_200'] = ta.trend.SMAIndicator(close=df['Close'], window=200).sma_indicator()

		# get latest values
		latest = df.iloc[-1]
		prev = df.iloc[-2]

		return {
			"symbol": yf_symbol,
			"current_price": round(latest['Close'], 2),
			"RSI_14": round(latest['RSI'], 2),
			"MACD": round(latest['MACD'], 4),
			"MACD_Signal": round(latest['MACD_Signal'], 4),
			"SMA_50": round(latest['SMA_50'], 2) if not pd.isna(latest['SMA_50']) else None,
			"SMA_200": round(latest['SMA_200'], 2) if not pd.isna(latest['SMA_200']) else None,
			"trend_signal": "BULLISH" if latest['MACD'] > latest['MACD_Signal'] else "BEARISH"
		}
	except Exception as e:
		logger.error(f"Failed to calculate technical indicators for {symbol}: {e}")
		return {"error": str(e)}