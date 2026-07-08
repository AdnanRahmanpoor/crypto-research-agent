from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.v1.router import api_router
from app.config import settings
import logging

logging.basicConfig(level = logging.INFO, format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title = "Multi-Agent Crypto Research Assistant", version = "1.0.0")

# api routes
app.include_router(api_router, prefix = "/api/v1")

# setup jinja2 templates
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory = str(BASE_DIR / "templates"))

@app.get("/", response_class = HTMLResponse)
async def home(request: Request):
	"""Serve the main frontend"""
	return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health():
	return {"status": "healthy", "message": "Multi-Agent Research Platform Online"}