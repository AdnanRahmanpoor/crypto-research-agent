from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.orchestrator import run_research_workflow
from app.core.state import ResearchState
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/research", tags=["AI Research"])

class ResearchRequest(BaseModel):
	coin_id: str
	symbol: str

@router.post("/generate", response_model=ResearchState)
async def generate_report(req: ResearchRequest):
	"""Triggers the multi-agent concurrent research workflow."""
	logger.info(f"API Request: Research for {req.symbol}")
	result = await run_research_workflow(req.coin_id, req.symbol)

	if result.status == "FAILED":
		raise HTTPException(status_code=500, detail=result.final_report)
	return result

	