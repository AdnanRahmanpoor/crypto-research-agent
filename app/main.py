from fastapi import FastAPI
from app.api.v1.router import api_router
import logging

logging.basicConfig(level = logging.INFO, format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title = "Multi-Agent Crypto Research Assistant", version = "1.0.0")
app.include_router(api_router, prefix = "/api/v1")

@app.get("/")
def health():
	return {"status": "healthy", "message": "Multi-Agent Research Platform Online"}