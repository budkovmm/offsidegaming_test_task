import json
import logging
import requests

from json import JSONDecodeError
from requests import Request
from binance.errors import ClientError, ServerError


class API:
    """API base class"""

    def __init__(self, base_url, api_key: str):
        """
        Parameters
        :param base_url: the API base url
        :param api_key: API key (How to Create API Keys on Binance https://www.binancezh.top/en/support/faq/how-to-create-api-keys-on-binance-360002502072)
        """
        self.base_url = base_url
        self.token = api_key
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json;charset=utf-8",
                "User-Agent": "pyscript",
                "X-MBX-APIKEY": api_key,
            }
        )

        self._logger = logging.getLogger(__name__)

    def query(self, url_path, http_method, payload=None):
        return self._send_request(url_path, http_method, params=payload)

    def _send_request(self, url_path, http_method, params=None, data=None):
        if params is None:
            params = {}

        url = self.base_url + url_path
        self._logger.debug(f"url: {url}")

        request = self._prepare_request(http_method, url, params, data)
        self._logger.debug(f"request: {request}")

        response = self.session.send(request)
        self._logger.debug(f"raw response: {response.text}")

        self._handle_exception(response)

        try:
            data = response.json()
        except ValueError:
            data = response.text
        result = {}

        if len(result) != 0:
            result["data"] = data
            return result

        return data

    def _prepare_request(self, http_method, url, params, data):
        req = Request(
            http_method, url, params=params, data=data, headers=self.session.headers
        )
        return self.session.prepare_request(req)

    @staticmethod
    def _handle_exception(response: requests.Response):
        status_code = response.status_code
        if status_code < 400:
            return
        if 400 <= status_code < 500:
            try:
                err = json.loads(response.text)
            except JSONDecodeError:
                raise ClientError(
                    status_code, None, response.text, None, response.headers
                )
            error_data = None
            if "data" in err:
                error_data = err["data"]
            raise ClientError(
                status_code, err["code"], err["msg"], response.headers, error_data
            )
        raise ServerError(status_code, response.text)
