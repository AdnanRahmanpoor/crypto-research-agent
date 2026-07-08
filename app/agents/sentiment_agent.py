from app.config import settings
from app.core.llm_client import llm_client
from app.core.state import ResearchState
from app.tools.market_data import fetch_coin_market_data
import json
import logging

logger = logging.getLogger(__name__)

async def run_sentiment_agent(state: ResearchState) -> ResearchState:
	logger.info(f"Sentiment Agent: Gaugin market psychology for {state.symbol}...")
	data = await fetch_coin_market_data(state.coin_id)
	sentiment_pct = data.get("sentiment_votes_up_percentage", "N/A")

	prompt = f"""You are a Crypto Sentiment & Behavioral Analyst. Based on the following data for {state.symbol}, assess the current market psychology:
		Market Data: {json.dumps(data)}
		Retail Sentiment (CoinGecko Upvotes): {sentiment_pct}%
		PRovide a clear sentiment verdict (Bullish, Neutral, or Bearish) with a 2-sentence justification based on price action, volume, and retail behavior."""

	response = await llm_client.chat.completions.create(
		model = settings.DEEPSEEK_MODEL,
		messages = [{"role": "user", "content": prompt}],
		temperature = 0.2
	)

	state.sentiment_score = response.choices[0].message.content
	logger.info("Sentiment Agent: Complete.")
	return state
