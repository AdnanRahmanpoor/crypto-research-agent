import asyncio
import json
from app.tools.market_data import fetch_coin_market_data
from app.tools.technical_data import fetch_technical_indicators


async def main():
	print("--- Testing Market Data Tool (CoinGecko) ---")
	market_data = await fetch_coin_market_data("solana")
	print(json.dumps(market_data, indent=2))

	print("--- Testing Technical Data Tool (yfinance) ---")
	tech_data = fetch_technical_indicators("SOL")
	print(json.dumps(tech_data, indent=2))

if __name__ == '__main__':
	asyncio.run(main())