from binance.api import API


class Spot(API):
    def __init__(self, base_url: str, api_key: str):
        super().__init__(base_url, api_key)

    def ticker_price(self, symbol: str):
        url_path = "/api/v3/ticker/price"
        params = {"symbol": symbol}
        return self.query(url_path, "GET", params)

    def ping(self):
        url_path = "/api/v3/ping"
        return self.query(url_path, "GET")
