
from typing import TypedDict

class UserTokenResponse(TypedDict):
    accessToken: str
    expiresIn: int
    tokenType: str
    refreshToken: str
    scope: str

class ClientCredTokenResponse(TypedDict):
    accessToken: str
    expiresIn: int
    tokenType: str
    scope: str

class AuthResponse(TypedDict):
    domain: str
    apiKey: str
    brand: str
    httpRegionalBaseUrl: str
    webSocketRegionalBaseUrl: str
    dataCenter: str
