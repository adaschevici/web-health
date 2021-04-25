import re
from typing import Optional, Dict
import requests
from icecream import ic


def _fetch(url: str):
    return requests.get(url, timeout=(5, 30))


def gather(url: str, regex: Optional[str] = None) -> Dict[str, str]:
    """
    Makes request and returns kafka json payload for producer to put into kafka
    """
    response = _fetch(url)
    if regex is None:
        return {
            "name": url,
            "elapsed": response.elapsed.total_seconds(),
            "status": response.status_code,
        }
    re_compiled = re.compile(regex, re.IGNORECASE)
    found_in_page = re_compiled.search(response.text) is not None
    return {
        "name": url,
        "elapsed": response.elapsed.total_seconds(),
        "status": response.status_code,
        "content_found": found_in_page
    }
