from base64 import b64decode
from datetime import datetime, timedelta
from json import loads
from types import TracebackType
from typing import Optional, Type
from urllib.parse import urljoin
from aiohttp import ClientSession

from .gigyaClient import GigyaClient
from .apiModels import AuthResponse, ClientCredTokenResponse, UserTokenResponse

API_KEY_ELECTROLUX = "2AMqwEV5MqVhTKrRCyYfVF8gmKrd2rAmp7cUsfky"
API_KEY_AEG = "PEdfAP7N7sUc95GJPePDU54e2Pybbt6DZtdww7dz"
CLIENT_SECRET_ELECTROLUX = "8UKrsKD7jH9zvTV7rz5HeCLkit67Mmj68FvRVTlYygwJYy4dW6KF2cVLPKeWzUQUd6KJMtTifFf4NkDnjI7ZLdfnwcPtTSNtYvbP7OzEkmQD9IjhMOf5e1zeAQYtt2yN"
CLIENT_SECRET_AEG = "G6PZWyneWAZH6kZePRjZAdBbyyIu3qUgDGUDkat7obfU9ByQSgJPNy8xRo99vzcgWExX9N48gMJo3GWaHbMJsohIYOQ54zH2Hid332UnRZdvWOCWvWNnMNLalHoyH7xU"
CLIENT_ID_ELECTROLUX = "ElxOneApp"
CLIENT_ID_AEG = "AEGOneApp"
BRAND_ELECTROLUX = "electrolux"
BRAND_AEG = "aeg"

BASE_URL = "https://api.ocp.electrolux.one"

def decodeJwt(token: str):
    token_payload = token.split(".")[1]
    token_payload_decoded = str(b64decode(token_payload + "=="), "utf-8")
    payload: dict = loads(token_payload_decoded)
    return payload

class UserToken:
    def __init__(self, token: UserTokenResponse) -> None:
        self.token = token
        self.expiresAt = datetime.now() + timedelta(seconds=token['expiresIn'])
        pass

class OneAppApi:
    _regional_base_url: Optional[str] = None
    _regional_websocket_base_url: Optional[str] = None
    _gigya_client: Optional[GigyaClient] = None

    def __init__(self, client_session: ClientSession) -> None:
        self._client_session = client_session
        self._close_session = False
        pass

    def _get_session(self):
        if self._client_session is None:
            self._client_session = ClientSession()
            self._close_session = True

    def _get_base_url(self):
        if self._regional_base_url is None:
            return BASE_URL
        return self._regional_base_url

    def _api_headers_base():
        return { "x-api-key": API_KEY_ELECTROLUX }

    async def _fetch_login_client_credentials(self):
        #https://api.ocp.electrolux.one/one-account-authorization/api/v1/token
        url = urljoin(self._get_base_url(), "one-account-authorization/api/v1/token")
        async with await self._get_session().get(url, json={ "grantType": "client_credentials", "clientId": CLIENT_ID_ELECTROLUX, "clientSecret": CLIENT_SECRET_ELECTROLUX, "scope": "" }, headers=self._api_headers_base()) as response:
            data: ClientCredTokenResponse = await response.json()
            return data

    async def _fetch_exchange_login_user(self, idToken: str):
        #https://api.ocp.electrolux.one/one-account-authorization/api/v1/token
        url = urljoin(self._get_base_url(), "one-account-authorization/api/v1/token")
        decodedToken = decodeJwt(idToken)
        headers = self._api_headers_base()
        headers["Origin-Country-Code"] = decodedToken["country"]
        async with await self._get_session().get(url, json={ "grantType": "urn:ietf:params:oauth:grant-type:token-exchange", "clientId": CLIENT_ID_ELECTROLUX, "idToken": idToken, "scope": "" }, headers=headers) as response:
            token: UserTokenResponse = await response.json()
            return UserToken(token)

    async def _fetch_refresh_token_user(self, token: UserToken):
        #https://api.ocp.electrolux.one/one-account-authorization/api/v1/token
        url = urljoin(self._get_base_url(), "one-account-authorization/api/v1/token")
        async with await self._get_session().get(url, json={ "grantType": "refresh_token", "clientId": CLIENT_ID_ELECTROLUX, "refreshToken": token.token["refreshToken"], "scope": "" }, headers=self._api_headers_base()) as response:
            token: UserTokenResponse = await response.json()
            return UserToken(token)

    async def _fetch_identity_providers(self, username: str):
        #https://api.ocp.electrolux.one/one-account-user/api/v1/identity-providers?brand=electrolux&email={{username}}
        url = urljoin(self._get_base_url(), "one-account-user/api/v1/identity-providers")
        async with await self._get_session().get(url, params={ "brand": "electrolux", "email": username }, headers=self._api_headers_base()) as response:
            data: list[AuthResponse] = await response.json()
            return data

    async def _init_identity_provider(self, username: str):
        data = await self._fetch_identity_providers(username)
        self._regional_base_url: str = data[0]["httpRegionalBaseUrl"]
        self._regional_websocket_base_url: str = data[0]["webSocketRegionalBaseUrl"]
        gigyaDomain = data[0]["domain"]
        gigyaApiKey: str = data[0]["apiKey"]
        if self._gigya_client is not None:
            await self._gigya_client.close()
        self._gigya_client = GigyaClient(self._get_session(), gigyaDomain, gigyaApiKey)

    async def close(self) -> None:
        if self._client_session and self._close_session:
            await self._client_session.close()
        if self._gigya_client:
            await self._gigya_client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]) -> Optional[bool]:
        """TODO return true if want to suppress exception"""
        await self.close()
