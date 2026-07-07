from openai import AsyncOpenAI
from app.config import settings

llm_client = AsyncOpenAI(
	api_key=settings.DEEPSEEK_API_KEY,
	base_url=settings.DEEPSEEK_MODEL,
	)