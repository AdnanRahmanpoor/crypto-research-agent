import asyncio
import logging
from app.core.state import ResearchState
from app.agents.technical_agent import run_technical_agent
from app.agents.market_agent import run_market_agent
from app.agents.news_agent import run_news_agent
from app.agents.sentiment_agent import run_sentiment_agent
from app.core.llm_client import llm_client
from app.config import settings

logger = logging.getLogger(__name__)

async def run_research_workflow(coin_id: str, symbol: str) -> ResearchState:
	state = ResearchState(coin_id = coin_id, symbol = symbol, status = "RUNNING")
	logger.info(f"Orchestrator: Starting concurrent research for {symbol}...")

	try:
		# 1. Concurrent execution: run all 4 agents at same time
		await asyncio.gather(
			run_technical_agent(state),
			run_market_agent(state),
			run_news_agent(state),
			run_sentiment_agent(state),
		)

		logger.info("Coordinator: Synthesizing final Daily Investment Report...")

		# 2. Coordination Prompt
		system_prompt = """You are a Senior Crypto Portfolio Manager at a top-tier hedge fund.
			You will receive analysis from 4 specialist agents. Synthesize them into a professional, data-driven Daily Investment Report.

			FORMAT EXACTLY AS MARKDOWN:
			# Daily Investment Report: {symbol}
			## Executive Summary
			## Technical View
			## Market Fundamentals & On-Chain
			## News & Catalysts
			## Market Sentiment
			## Risk Factors
			## Final Verdict
		"""

		user_prompt = f"""
		TECHNICAL ANALYSIS:
		{state.technical_analysis or "Data unavailable"}

		MARKET FUNDAMENTALS:
		{state.on_chain_metrics or "Data unavailable"}

		NEWS SUMMARY:
		{state.news_summary or "Data unavailable"}

		SENTIMENT ANALYSIS:
		{state.sentiment_score or "Data unavailable"}
		"""

		response = await llm_client.chat.completions.create(
			model = settings.DEEPSEEK_MODEL,
			messages = [
				{"role": "system", "content": system_prompt.replace("{symbol}", state.symbol)},
				{"role": "user", "content": user_prompt},
			],
			temperature = 0.5
		)

		state.final_report = response.choices[0].message.content
		state.status = "COMPLETED"
		logger.info("Orchestrator: Research workflow complete.")

	except Exception as e:
		logger.error(f"Orchestrator failed: {e}")
		state.status = "FAILED"
		state.final_report = f"Research workflow failed due to: {str(e)}"

	return state