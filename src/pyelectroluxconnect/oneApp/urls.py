from typing import Any, Mapping, Optional, Union
from urllib.parse import quote_plus, urljoin
from multidict import CIMultiDict, CIMultiDictProxy, istr

from .const import CLIENT_ID_ELECTROLUX


class RequestParams:
    def __init__(
        self,
        method: str,
        url: str,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[
            Union[
                Mapping[Union[str, istr], str], CIMultiDict[str], CIMultiDictProxy[str]
            ]
        ] = None,
        json: Any = None,
    ) -> None:
        self.method = method
        self.url = url
        self.params = params
        self.headers = headers
        self.json = json


def multi_urljoin(*parts: str):
    return urljoin(
        parts[0], "/".join(quote_plus(part.strip("/"), safe="/") for part in parts[1:])
    )


def token_url(
    baseUrl: str,
    headers: dict[str, str],
    grantType: str,
    clientSecret: str | None = None,
    idToken: str | None = None,
    refreshToken: str | None = None,
):
    # https://api.ocp.electrolux.one/one-account-authorization/api/v1/token
    return RequestParams(
        "GET",
        urljoin(baseUrl, "one-account-authorization/api/v1/token"),
        None,
        headers,
        {
            "grantType": grantType,
            "clientId": CLIENT_ID_ELECTROLUX,
            "clientSecret": clientSecret,
            "idToken": idToken,
            "refreshToken": refreshToken,
            "scope": "",
        },
    )


def identity_providers_url(
    baseUrl: str, headers: dict[str, str], brand: str, username: str
):
    # https://api.ocp.electrolux.one/one-account-user/api/v1/identity-providers?brand=electrolux&email={{username}}
    return RequestParams(
        "GET",
        urljoin(baseUrl, "one-account-user/api/v1/identity-providers"),
        {"brand": brand, "email": username},
        headers,
        None,
    )


def current_user_metadata_url(baseUrl: str, headers: dict[str, str]):
    # https://api.ocp.electrolux.one/one-account-user/api/v1/users/current
    return RequestParams(
        "GET",
        urljoin(baseUrl, "one-account-user/api/v1/identity-providers"),
        None,
        headers,
        None,
    )


def list_appliances_url(baseUrl: str, headers: dict[str, str], includeMetadata: bool):
    # https://api.ocp.electrolux.one/appliance/api/v2/appliances?includeMetadata=true
    return RequestParams(
        "GET",
        urljoin(baseUrl, "appliance/api/v2/appliances"),
        {"includeMetadata": "true"} if includeMetadata else None,
        headers,
        None,
    )


def get_appliance_by_id(baseUrl: str, headers: dict[str, str], id: str):
    # https://api.ocp.electrolux.one/appliance/api/v2/appliances/{{Id}}
    return RequestParams(
        "GET",
        multi_urljoin(baseUrl, "appliance/api/v2/appliances", id),
        None,
        headers,
        None,
    )


def get_appliance_capabilities(baseUrl: str, headers: dict[str, str], id: str):
    # https://api.ocp.electrolux.one/appliance/api/v2/appliances/{{Id}}/capabilities
    return RequestParams(
        "GET",
        multi_urljoin(baseUrl, "appliance/api/v2/appliances", id, "capabilities"),
        None,
        headers,
        None,
    )


def get_appliances_info_by_ids(baseUrl: str, headers: dict[str, str], ids: list[str]):
    # POST https://api.ocp.electrolux.one/appliance/api/v2/appliances/info
    return RequestParams(
        "POST",
        multi_urljoin(baseUrl, "appliance/api/v2/appliances/info"),
        None,
        headers,
        {
            "applianceIds": ids,
        },
    )


def appliance_command(baseUrl: str, headers: dict[str, str], id: str, commandData: Any):
    # PUT https://api.ocp.electrolux.one/appliance/api/v2/appliances/{{Id}}/command
    return RequestParams(
        "PUT",
        multi_urljoin(baseUrl, "appliance/api/v2/appliances", id, "command"),
        None,
        headers,
        commandData,
    )
