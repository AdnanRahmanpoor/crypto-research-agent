import httpx
import logging
from typing import List, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

async def fetch_crypto_news(coin_name: str) -> List[Dict[str, Any]]:
	"""
	Fetches real-time crypto news from GNews.io
	Optimized for LLM context windows (max 10 articles)
	"""
	if not settings.GNEWS_API_KEY:
		logger.warning("GNEWS_API_KEY not found. Returning mock data.")
		return [{"headline": f"Mock: No API key provided for {coin_name}", "source": "Local"}]

	url = "https://gnews.io/api/v4/search"
	params = {
		"q": f"{coin_name} crypto",
		"lang": "en",
		"max": 10, # articles limit
		"apikey": settings.GNEWS_API_KEY
	}

	try:
		async with httpx.AsyncClient() as client:
			response = await client.get(url, params = params, timeout = 10.0)
			response.raise_for_status()
			data = response.json()

			# extract specific fields to save token
			articles = []
			for article in data.get("articles", []):
				articles.append({
					"headline": article.get("title"),
					"snippet": article.get("description"),
					"source": article.get("source", {}).get("name"),
					"published_at": article.get("publishedAt"),
					})

			logger.info(f"Successfully fetched {len(articles)} articles for {coin_name}")
			return articles
	except httpx.HTTPStatusError as e:
		logger.error(f"GNews API HTTP Error: {e.response.status_code} - {e.response.text}")
		return [{"error": f"API Error: {e.response.status_code}"}]

	except Exception as e:
		logger.error(f"Failed to fetch GNews data for {coin_name}: {e}")
		return [{"error": str(e)}]