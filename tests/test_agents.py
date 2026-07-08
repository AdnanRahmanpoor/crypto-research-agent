import asyncio
from app.core.state import ResearchState
from app.agents.technical_agent import run_technical_agent
from app.agents.market_agent import run_market_agent

async def main():
    # 1. Initialize the State
    print("🧠 Initializing Research State for Solana (SOL)...")
    state = ResearchState(coin_id="solana", symbol="SOL")
    
    # 2. Run the Technical Agent
    print("\n--- Running Technical Agent ---")
    state = await run_technical_agent(state)
    print("Technical Analysis Output:")
    print(state.technical_analysis)
    
    # 3. Run the Market Agent
    print("\n--- Running Market Agent ---")
    state = await run_market_agent(state)
    print("On-Chain/Market Output:")
    print(state.on_chain_metrics)

if __name__ == "__main__":
    asyncio.run(main())