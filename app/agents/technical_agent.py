from app.core.llm_client import llm_client
from app.config import settings
from app.core.state import ResearchState
from app.tools.technical_data import fetch_technical_indicators
import json
import logging

logger = logging.getLogger(__name__)

async def run_technical_agent(state: ResearchState) -> ResearchState:
	"""
	The Technical Analysis Agent.
	Fetches price data, calculates indicators, and uses the LLM to interpret the trend.
	"""
	logger.info(f"Technical Agent: Analyzing {state.symbol}...")

	# 1. Execute
	tech_data = fetch_technical_indicators(state.symbol)

	if "error" in tech_data:
		state.technical_analysis = f"Error fetching technical data: {tech_data['error']}"
		return state

	# 2. Formulate the prompt
	system_prompt = """You are a Senior Quantitative Technical Analyst at a top-tier crypto hedge fund.
    You are provided with real-time technical indicators for a cryptocurrency.
    Your task is to analyze the RSI, MACD, and Moving Averages to determine the short-term and medium-term trend.
    Be concise, professional, and data-driven. Provide a clear 'Bullish', 'Bearish', or 'Neutral' verdict at the end."""

	user_prompt = f"""
    Analyze the following technical data for {state.symbol}:
    {json.dumps(tech_data, indent=2)}
    
    Provide your technical analysis.
    """
    # 3. Call llm
	try:
		response = await llm_client.chat.completions.create(
    		model = settings.DEEPSEEK_MODEL,
    		messages = [
    			{"role": "system", "content": system_prompt},
    			{"role": "user", "content": user_prompt},
    		],
    		temperature = 0.3 # lower temp for strict, analytical reasoning
		)

		analysis = response.choices[0].message.content
		state.technical_analysis = analysis
		logger.info("Technical Agent: Analysis Complete.")

	except Exception as e:
		logger.error(f"Technical Agent LLM call failed: {e}")
		state.technical_analysis = "Failed to generate technical analysis"

	return state
