import httpx
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def fetch_coin_market_data(coin_id: str) -> Dict[str, Any]:
	"""
	Fetches real-time market and on-chain data from Coingecko.
	Tool used by: On-chain Agent, Sentiment Agent.
	"""
	url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
	params = {
		"localization": "false",
		"tickers": "false",
		"market_data": "true",
		"community_data": "true",
		"developer_data": "true",
		"sparkline": "false"
	}

	try:
		async with httpx.AsyncClient() as client:
			response = await client.get(url, params=params, timeout=10.0)
			response.raise_for_status()
			data = response.json()

			# Extract only the metrics we care about 
			market_data = data.get("market_data", {})

			return {
				"symbol": data.get("symbol", "").upper(),
				"current_price_usd": market_data.get("current_price", {}).get("usd"),
				"market_cap_usd": market_data.get("market_cap", {}).get("usd"),
				"total_volume_usd": market_data.get("total_volume", {}).get("usd"),
				"price_change_24h_pct": market_data.get("price_change_percentage_24h"),
				"price_change_7d_pct": market_data.get("price_change_percentage_7d"),
				"circulating_supply": market_data.get("circulating_supply"),
				"total_supply": market_data.get("total_supply"),
				"developer_score": market_data.get("developer_score"),
				"community_score": market_data.get("community_score"),
				"sentiment_votes_up_percentage": market_data.get("sentiment_votes_up_percentage"),
			}
	except Exception as e:
		logger.error(f"Failed to fetch CoinGecko data for {coin_id}: {e}")
		return {"error": str(e)}