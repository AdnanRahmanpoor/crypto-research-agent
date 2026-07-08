from app.core.llm_client import llm_client
from app.config import settings
from app.core.state import ResearchState
from app.tools.market_data import fetch_coin_market_data
import json
import logging

logger = logging.getLogger(__name__)

async def run_market_agent(state: ResearchState) -> ResearchState:
	"""
	The On-Chain & Market Fundamentals Agent.
	Analyzes market cap, volume, supply dynamics, and community sentiment.
	"""
	logger.info(f"Market Agent: Analyzing on-chain metrics for {state.coin_id}...")

	# Execute tool
	market_data = await fetch_coin_market_data(state.coin_id)

	if "error" in market_data:
		state.on_chain_metrics = f"Error fetching market data: {market_data['error']}"
		return state

	# formulate prompt
	system_prompt = """You are an Expert On-Chain and Market Fundamentals Analyst.
    You analyze tokenomics, liquidity, volume, and community health.
    Look for red flags (e.g., massive inflation, low volume relative to market cap) or green flags (e.g., high developer activity, strong community).
    Provide a concise summary of the asset's fundamental health."""

	user_prompt = f"""
    Analyze the following market and on-chain data for {state.symbol} ({state.coin_id}):
    {json.dumps(market_data, indent=2)}
    
    Provide your fundamental analysis.
    """

    # call llm
	try:
		response = await llm_client.chat.completions.create(
    		model = settings.DEEPSEEK_MODEL,
    		messages = [
    			{"role": "system", "content": system_prompt},
    			{"role": "user", "content": user_prompt},
    		],
    		temperature = 0.4 # lower temp for strict, analytical reasoning
		)

		analysis = response.choices[0].message.content
		state.on_chain_metrics = analysis
		logger.info("Market Agent: Analysis Complete.")

	except Exception as e:
		logger.error(f"Market Agent LLM call failed: {e}")
		state.on_chain_metrics = "Failed to generate market analysis"

	return state
