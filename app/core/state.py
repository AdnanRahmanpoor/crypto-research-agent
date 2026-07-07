from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ResearchState(BaseModel):
	"""
	The shared memory space for the multi-agent workflow.
	Agents will populate these fields concurrently
	"""
	# inputs
	coin_id: str = Field(..., description="The CoinGecko ID (eg. 'bitcoin', 'solana')")
	symbol: str = Field(..., description="The ticker symbol (eg. 'btc', 'sol')")

	# Agent output
	news_summary: Optional[str] = None
	technical_analysis: Optional[str] = None
	on_chain_metrics: Optional[str] = None
	sentiment_score: Optional[str] = None

	# Final Output
	final_report: Optional[str] = None

	# Metadata
	created_at: datetime = Field(default_factory=datetime.utcnow)
	status: str = Field(default="PENDING") # PENDING, RUNNING, COMPLETED, FAILED