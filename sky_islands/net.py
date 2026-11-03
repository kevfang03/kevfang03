"""A small JSON GET for the keyless public feeds (weather and sports scores)."""

from __future__ import annotations

import json
import urllib.request
from collections.abc import Callable

Get = Callable[[str], dict]

TIMEOUT_S = 10


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "sky-islands-banner",
                                               "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        return json.load(resp)
