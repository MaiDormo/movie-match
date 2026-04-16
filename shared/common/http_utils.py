import requests
from typing import Dict, Any, Optional, Union


def make_request(
    url: str,
    method: str = "get",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Union[Dict[str, Any], str]] = None,
    json: Optional[Dict[str, Any]] = None,
    auth: Optional[tuple] = None,
    timeout: int = 10,
) -> Dict[str, Any]:
    """
    Generic HTTP request handler.
    Raises exceptions on error—caller handles them.

    Args:
        data: For form-urlencoded body (application/x-www-form-urlencoded)
        json: For JSON body (application/json)
    """
    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        data=data,
        json=json,
        auth=auth,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()
