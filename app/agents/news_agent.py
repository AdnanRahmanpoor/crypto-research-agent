# app/agents/news_agent.py
from app.core.llm_client import llm_client
from app.config import settings
from app.core.state import ResearchState
from app.tools.news_fetcher import fetch_crypto_news
import logging

logger = logging.getLogger(__name__)

async def run_news_agent(state: ResearchState) -> ResearchState:
    logger.info(f"📰 News Agent: Fetching live headlines for {state.coin_id}...")
    headlines = await fetch_crypto_news(state.coin_id)

    if any("error" in h for h in headlines):
        state.news_summary = f"Failed to fetch news: {headlines[0].get('error')}"
        return state

    # Format the data cleanly for the LLM
    news_context = "\n".join([
        f"- [{h['source']}] {h['headline']}: {h.get('snippet', 'No details')}" 
        for h in headlines
    ])

    # 1. STRICT SYSTEM PROMPT
    system_prompt = """You are a strict, professional Crypto Market News Analyst. 
    You will be provided with a list of recent news headlines and snippets.
    Your ONLY job is to analyze these specific headlines and identify the overarching narrative, potential price catalysts, and macro risks.
    
    RULES:
    1. DO NOT output generic greetings like "How can I help you?" or "Just one word".
    2. DO NOT ask the user for more information.
    3. Output ONLY the news analysis based on the provided text.
    4. If the provided text is empty or irrelevant, state "No relevant news catalysts identified."
    """

    user_prompt = f"""
    RECENT LIVE HEADLINES FOR {state.symbol}:
    {news_context}
    
    Provide your professional news analysis now.
    """

    try:
        # First Attempt
        response = await llm_client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        
        analysis = response.choices[0].message.content
        
        # 2. SEMANTIC GUARDRAIL: Detect if the LLM fell into the chatbot trap
        chatbot_triggers = ["how can i help", "just one word", "what's your prompt", "share a prompt"]
        if any(trigger in analysis.lower() for trigger in chatbot_triggers):
            logger.warning("⚠️ News Agent: LLM fell into chatbot greeting trap. Retrying with stricter prompt...")
            
            # Retry with a much shorter, aggressive prompt (no system message to avoid confusion)
            retry_prompt = f"Analyze these crypto headlines for {state.symbol}. Output ONLY the analysis, absolutely no greetings or conversational text:\n{news_context}"
            
            response = await llm_client.chat.completions.create(
                model=settings.DEEPSEEK_MODEL,
                messages=[{"role": "user", "content": retry_prompt}],
                temperature=0.1 # Drop temperature to force strict compliance
            )
            analysis = response.choices[0].message.content

        state.news_summary = analysis
        logger.info("✅ News Agent: Live news analysis complete.")
        
    except Exception as e:
        logger.error(f"News Agent LLM call failed: {e}")
        state.news_summary = "Failed to generate news analysis."
        
    return state