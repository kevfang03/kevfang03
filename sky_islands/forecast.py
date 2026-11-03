"""Philadelphia's weather right now, from Open-Meteo (free, no key).

The banner only needs a rough picture: what the sky is doing, the temperature, and today's
real sunrise and sunset. If the feed fails, the world is drawn clear with estimated sun
times instead, so a weather outage never stops the hourly redraw.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlencode

from .clock import PHILLY
from .net import Get, get_json

LAT, LON = 39.9526, -75.1652  # Philadelphia City Hall
URL = "https://api.open-meteo.com/v1/forecast?" + urlencode({
    "latitude": LAT, "longitude": LON, "current": "temperature_2m,weather_code",
    "daily": "sunrise,sunset", "temperature_unit": "fahrenheit",
    "timezone": "America/New_York", "forecast_days": 1,
})

KINDS = ("clear", "cloudy", "fog", "rain", "storm", "snow")


@dataclass(frozen=True)
class Forecast:
    kind: str  # one of KINDS
    temp_f: int
    sunrise: datetime
    sunset: datetime


def kind_for(code: int) -> str:
    """Fold a WMO weather code into the few skies the banner can draw."""
    if code in (0, 1):
        return "clear"
    if code in (2, 3):
        return "cloudy"
    if code in (45, 48):
        return "fog"
    if code in (71, 73, 75, 77, 85, 86):
        return "snow"
    if code >= 95:
        return "storm"
    if 51 <= code <= 67 or 80 <= code <= 82:
        return "rain"
    return "cloudy"


def parse(data: dict) -> Forecast:
    now, daily = data["current"], data["daily"]

    def local(value: str) -> datetime:
        return datetime.fromisoformat(value).replace(tzinfo=PHILLY)

    return Forecast(kind_for(int(now["weather_code"])), round(now["temperature_2m"]),
                    local(daily["sunrise"][0]), local(daily["sunset"][0]))


def fetch_forecast(get: Get = get_json) -> Forecast | None:
    """The weather now, or None if the feed is down or answers with something unexpected."""
    try:
        return parse(get(URL))
    except Exception as err:  # noqa: BLE001 - any failure just means a clear sky
        print(f"weather unavailable, drawing a clear sky ({type(err).__name__})")
        return None
