import random
import time
from types import TracebackType
from typing import Optional, Type
from urllib.parse import urljoin
from aiohttp import ClientSession

from .gigyaModels import GetJWTResponse, LoginResponse, SocializeGetIdsResponse

def current_milli_time():
    return round(time.time() * 1000)

class GigyaClient:
    def __init__(self, client_session: ClientSession, domain: str, api_key: str) -> None:
        self._client_session = client_session
        self._close_session = False
        self._domain = domain
        self._api_key = api_key

    def _get_session(self):
        if self._client_session is None:
            self._client_session = ClientSession()
            self._close_session = True

    def _generate_nonce():
        return f'{current_milli_time()}_{random.randrange(1000000000, 10000000000)}'

    async def get_ids(self):
        #https://socialize.eu1.gigya.com/socialize.getIDs
        url = f'https://socialize.{self._domain}/socialize.getIDs'
        async with await self._client_session.get(
            url,
            data={
                "apiKey": self._api_key,
                "format": "json",
                "httpStatusCodes": False,
                "nonce": self._generate_nonce(),
                "sdk": "Android_6.2.1",
                "targetEnv": "mobile"
                }) as response:

            data: SocializeGetIdsResponse = await response.json()
            return data

    async def login(self, gmid: str, username: str, password: str, ucid: str):
        #https://accounts.eu1.gigya.com/accounts.login
        url = f'https://accounts.{self._domain}/accounts.login'
        async with await self._client_session.get(
            url,
            data={
                "apiKey": self._api_key,
                "format": "json",
                "gmid": gmid,
                "httpStatusCodes": False,
                "loginID": username,
                "nonce": self._generate_nonce(),
                "password": password,
                "sdk": "Android_6.2.1",
                "targetEnv": "mobile",
                "ucid": ucid
            }) as response:

            data: LoginResponse = await response.json()
            return data

    async def getJWT(self, gmid: str, sessionToken: str, ucid: str):
        #https://accounts.eu1.gigya.com/accounts.getJWT
        url = f'https://accounts.{self._domain}/accounts.getJWT'
        sig = "TODO"
        timestampSeconds = "TODO"
        async with await self._client_session.get(
            url,
            data={
                "apiKey": self._api_key,
                "fields": "country",
                "format": "json",
                "gmid": gmid,
                "httpStatusCodes": False,
                "nonce": self._generate_nonce(),
                "oauth_token": sessionToken,
                "sdk": "Android_6.2.1",
                "sig": sig,
                "targetEnv": "mobile",
                "timestamp": timestampSeconds,
                "ucid": ucid
            }) as response:

            data: GetJWTResponse = await response.json()
            return data

    async def close(self):
        if self._client_session and self._close_session:
            await self._client_session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]) -> Optional[bool]:
        await self.close()

