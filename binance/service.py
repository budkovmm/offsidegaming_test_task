import csv
import logging
import os
import time

from _decimal import Decimal
from dataclasses import dataclass, asdict, fields
from typing import Optional
from binance.errors import ClientError
from binance.spot import Spot


@dataclass
class PriceData:
    ticker: str
    price_in_btc: Decimal = Decimal(0)
    error: Optional[str] = None


class SpotService:
    """Service for getting prices"""
    def __init__(self, spot_client: Spot):
        self.client = spot_client
        self._logger = logging.getLogger(__name__)

    def get_prices(self, tickers: list[str]) -> list[PriceData]:
        btc_ticker = "BTC"
        self._logger.info(f"getting prices for: {tickers}")
        result = []
        for ticker in tickers:
            data = PriceData(ticker=ticker)
            try:
                response = self.client.ticker_price(ticker + btc_ticker)
                price = Decimal(response.get("price"))
                self._logger.info(f"price of {ticker} = {price}")
                data.price_in_btc = price

            except ClientError as err:
                self._logger.error(err)
                data.error = f"ERROR: {err.error_message}"
            finally:
                result.append(data)
        return result

    def check_connectivity(self):
        """Check binance API connectivity"""
        try:
            self.client.ping()
        except ConnectionError:
            raise Exception(f"{self.client.base_url} connectivity problems")

    def write_to_csv(self, data: list[PriceData]):
        sorted_data = self.sort_exchange_data_by_price(data)

        try:
            self._logger.info("start writing data to the file")
            timestr = time.strftime("%Y%m%d-%H%M%S")
            path = "./output/"
            os.makedirs(path, exist_ok=True)
            file_name = f"exchange_rates_{timestr}.csv"
            with open(path + file_name, "w") as f:
                flds = [field.name for field in fields(PriceData)]
                w = csv.DictWriter(f, flds)
                w.writeheader()
                w.writerows([asdict(prop) for prop in sorted_data])
            self._logger.info(f"data successfully wrote to the {file_name}")
        except IOError as err:
            self._logger.error("write data to csv failed", err)
            raise err

    @staticmethod
    def sort_exchange_data_by_price(data: list[PriceData]):
        return sorted(data, key=lambda d: d.price_in_btc)
