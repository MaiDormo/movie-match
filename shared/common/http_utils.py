import requests
from typing import Dict, Any, Optional


def make_request(
    url: str,
    method: str = "get",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    auth: Optional[tuple] = None,
    timeout: int = 10
) -> Dict[str, Any]:
    """
    Generic HTTP request handler.
    Raises exceptions on error—caller handles them.
    """
    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json=data,
        auth=auth,
        timeout=timeout
    )
    response.raise_for_status()
    return response.json()
