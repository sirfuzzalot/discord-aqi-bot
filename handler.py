import os
import datetime
from typing import Union, List

import httpx

from lib.airnow import AirNow, Forecast, Observation


def aqi_report(event = None, context = None):
    """Send an Air Quality report to a Discord Channel"""

    if "AQI_BOT_AIRNOW_API_TOKEN" not in os.environ:
        raise EnvironmentError("Missing AQI_BOT_AIRNOW_API_TOKEN")
    AQI_BOT_AIRNOW_API_TOKEN = os.environ["AQI_BOT_AIRNOW_API_TOKEN"]

    if "AQI_BOT_AIRNOW_ZIP_CODE" not in os.environ:
        raise EnvironmentError("Missing AQI_BOT_AIRNOW_ZIP_CODE")
    AQI_BOT_AIRNOW_ZIP_CODE = os.environ["AQI_BOT_AIRNOW_ZIP_CODE"]

    if "AQI_BOT_DISCORD_BOT_URL" not in os.environ:
        raise EnvironmentError("Missing AQI_BOT_DISCORD_BOT_URL")
    AQI_BOT_DISCORD_BOT_URL = os.environ["AQI_BOT_DISCORD_BOT_URL"]

    if "AQI_BOT_MORNING_RANGE_UTC" not in os.environ:
        raise EnvironmentError("Missing AQI_BOT_MORNING_RANGE_UTC")
    AQI_BOT_MORNING_RANGE_UTC = os.environ["AQI_BOT_MORNING_RANGE_UTC"]

    morning_range = [int(x) for x in AQI_BOT_MORNING_RANGE_UTC.split(",")]
    airnow = AirNow(AQI_BOT_AIRNOW_API_TOKEN, httpx.Client())

    current = airnow.get_current(AQI_BOT_AIRNOW_ZIP_CODE)
    forecast = airnow.get_forecast(AQI_BOT_AIRNOW_ZIP_CODE)

    message = render_message(
        current,
        forecast,
        morning_range
    )

    response = httpx.post(
        AQI_BOT_DISCORD_BOT_URL,
        json={ "content": message }
    )
    response.raise_for_status()


def render_message(
    current: Observation,
    forecasts: List[Forecast],
    morning_range: List[int]
) -> str:
    """Renders a formatted message of current AQI data"""
    return f"""
{get_title_block(current.date_observed.strftime('%A'), is_evening(morning_range))}
```markdown
Current AQI
-------------------------------------
Recorded: {current.datetime_observed}
Location: {current.reporting_area}

{get_aqi_rows(current)}

{"".join([get_forecast_block(f) for f in forecasts])}
```
    """

def is_evening(morning_range: List[int]) -> bool:
    """Returns True if current time is not between 15:00 and 19:00 UTC"""
    current_datetime = datetime.datetime.now(datetime.timezone.utc)
    start_morning = datetime.datetime.combine(
        current_datetime.date(),
        datetime.time(hour=morning_range[0]),
        datetime.timezone.utc
    )
    end_morning = datetime.datetime.combine(
        current_datetime.date(),
        datetime.time(hour=morning_range[1]),
        datetime.timezone.utc
    )
    is_eve = True
    if start_morning <= current_datetime <= end_morning:
        is_eve = False
    return is_eve


def get_title_block(day: str, is_evening: bool) -> str:
    """renders the title block"""
    if is_evening:
        title = "🎮 " + day + " Evening 😴"
    else:
        title = "🥞 " + day + " Morning 🍳"
    return f"""
```
{title} \u21B4
```
    """


def get_forecast_block(forecast: Forecast) -> str:
    """Renders a forecast block"""
    return f"""
Forecast AQI
-------------------------------------
Forecast For: {forecast.date_forecast}
Location: {forecast.reporting_area}

{get_aqi_rows(forecast)}

    """


def get_aqi_rows(aqi_data: Union[Observation,Forecast]) -> str:
    """Generate AQI table rows"""
    rows = ""
    for metric in aqi_data:
        if metric:
            row = f'{metric.name.rjust(8)}  |'
            row += f'  {str(metric.AQI).ljust(8)}\n'
            rows += row

    return rows.rstrip("\n")


if __name__ == "__main__":
    import json
    with open("./env.json") as config:
        config_data = json.loads(config.read())
    for key, value in config_data.items():
        os.environ[key] = value
    aqi_report()

