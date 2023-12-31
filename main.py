import json
import logging
import os

from dotenv import load_dotenv
from binance.service import SpotService
from binance.spot import Spot


if __name__ == '__main__':
    # Getting configs
    load_dotenv()
    log_level = os.getenv("LOG_LEVEL", "INFO")
    api_key = os.getenv("API_KEY", "")
    base_url = os.getenv("BASE_URL", "https://api.binance.com")
    tickers = json.loads(os.getenv("TICKERS", "[]"))

    # Initialize logger
    logging.basicConfig(level=log_level)
    logger = logging.getLogger(__name__)

    # Client and service initialization
    spot_client = Spot(base_url, api_key)
    spot_service = SpotService(spot_client)

    # Checking connectivity
    spot_service.check_connectivity()

    # Getting prices
    prices = spot_service.get_prices(tickers)

    # Write data to the csv file
    spot_service.write_to_csv(prices)

    # Log tickers with price lower than BTC
    logger.info(f"tickers with price lower than BTC {[x.ticker for x in prices if x.price_in_btc < 1]}")
