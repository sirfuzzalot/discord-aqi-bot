import enum
import datetime
from typing import Optional, Any, List, Dict, Iterable
from dataclasses import dataclass

FORECAST_BASE_URL = "https://www.airnowapi.org/aq/forecast/zipCode/?format=application/json&"
OBSERVATION_BASE_URL = "https://www.airnowapi.org/aq/observation/zipCode/current/?format=application/json&"
TIMEZONE_LOOKUP = {
    "HST": -10,
    "HDT": -9,
    "AKST": -9,
    "AKDT": -8,
    "PST": -8,
    "PDT": -7,
    "MST": -7,
    "MDT": -6,
    "CST": -6,
    "CDT": -5,
    "EST": -5,
    "EDT": -4,
    "AST": -4,
    "ADT": -3
}


class NoDataError(Exception):
    """Exception indicating there was no air quality data available"""
    pass


class Severity(enum.Enum):
    """
    Severity of metric AQI
    """
    GOOD = 1
    MODERATE = 2
    USG = 3 # Unhealthy for Sensitive Groups
    UNHEALTHY = 4
    VERY_UNHEALTHY = 5
    HAZARDOUS = 6


@dataclass
class AQI:
    """
    AQI data for a metric

    Parameters:
        name (str): Display name of AQI Metric. Ex: PM2.5
        aqi (int): The AQI number for a metric.
        severity (Severity): The corresponding severity of the
            AQI number.
        is_action_day (bool): Indicates the severity is great enough
            requiring action.

    Attributes:
        name (str): Display name of AQI Metric. Ex: PM2.5
        AQI (int): The AQI number for a metric.
        severity (Severity): The corresponding severity of the
            AQI number.
        is_action_day (Optional[bool]): Indicates the severity is great enough
            requiring action. Only provided for Forecasts.
    """
    name: str
    AQI: int
    severity: Severity
    is_action_day: Optional[bool] = None


@dataclass
class Forecast:
    """
    Forecast information may include one or more metrics for
    air quality and associated meta-data.

    Parameters:
        date_issued (datetime.date): The date the data was issued.
        date_forecast (datetime.date): The date the predictions are valid for.
        reporting_area (str): The area the data is valid for.
        state_code (str): Two letter postal code for U.S. State.
        latitude (float): Geographic latitude of metric's source.
        longitude (float): Geographic longitude of metric's source.
        CO (AQI): AQI data for the CO metric.
        NO2 (AQI): AQI data for the NO2 metric.
        O3 (AQI): AQI data for the O3 metric.
        PM2_5 (AQI): AQI data for the PM2.5 metric.
        PM10 (AQI): AQI data for the PM10 metric.
        discussion (Optional[str]): Supplemental air quality information
            as a text block.

    Attributes:
        date_issued (datetime.date): The date the data was issued.
        date_forecast (datetime.date): The date the predictions are valid for.
        reporting_area (str): The area the data is valid for.
        state_code (str): Two letter postal code for U.S. State.
        latitude (float): Geographic latitude of metric's source.
        longitude (float): Geographic longitude of metric's source.
        CO (AQI): AQI data for the CO metric.
        NO2 (AQI): AQI data for the NO2 metric.
        O3 (AQI): AQI data for the O3 metric.
        PM2_5 (AQI): AQI data for the PM2.5 metric.
        PM10 (AQI): AQI data for the PM10 metric.
        discussion (Optional[str]): Supplemental air quality information
            as a text block.
    """
    date_issued: datetime.date
    date_forecast: datetime.date
    reporting_area: str
    state_code: str
    latitude: float
    longitude: float
    CO: AQI
    NO2: AQI
    O3: AQI
    PM2_5: AQI
    PM10: AQI
    discussion: Optional[str] = None

    def __iter__(self) -> Iterable[Optional[AQI]]:
        """Iterate over metrics"""
        return iter([self.CO, self.NO2, self.O3, self.PM2_5, self.PM10 ])


@dataclass
class Observation:
    """
    Observed air quality metrics and associated meta-data for a reporting
    area. Observation objects will contain on ly the metrics that are
    available at the time of query.

    Parameters:
        date_observed (datetime.date): The date the data was collected.
        hour_observed (int): The hour the data was collected.
        local_tz (str): The timezone where the data was collected.
        reporting_area (str): The area the data is valid for.
        state_code (str): Two letter postal code for U.S. State.
        latitude (float): Geographic latitude of metric's source.
        longitude (float): Geographic longitude of metric's source.
        CO (Optional[AQI]): AQI data for the CO metric.
        NO2 (Optional[AQI]): AQI data for the NO2 metric.
        O3 (Optional[AQI]): AQI data for the O3 metric.
        PM2_5 (Optional[AQI]): AQI data for the PM2.5 metric.
        PM10 (Optional[AQI]): AQI data for the PM10 metric.

    Attributes:
        datetime_observed (datetime.datetime): The datetime the data was
            collected with hour resolution.
        reporting_area (str): The area the data is valid for.
        state_code (str): Two letter postal code for U.S. State.
        latitude (float): Geographic latitude of metric's source.
        longitude (float): Geographic longitude of metric's source.
        CO (Optional[AQI]): AQI data for the CO metric.
        NO2 (Optional[AQI]): AQI data for the NO2 metric.
        O3 (Optional[AQI]): AQI data for the O3 metric.
        PM2_5 (Optional[AQI]): AQI data for the PM2.5 metric.
        PM10 (Optional[AQI]): AQI data for the PM10 metric.
    """
    date_observed: datetime.date
    hour_observed: int
    local_tz: str
    reporting_area: str
    state_code: str
    latitude: float
    longitude: float
    CO: Optional[AQI] = None
    NO2: Optional[AQI] = None
    O3: Optional[AQI] = None
    PM2_5: Optional[AQI] = None
    PM10: Optional[AQI] = None

    def __post_init__(self):
        """Build the datetime_observed attribute"""
        date = self.date_observed
        self.datetime_observed = datetime.datetime(
            date.year,
            date.month,
            date.day,
            self.hour_observed,
            tzinfo=get_timezone(self.local_tz)
        )

    def __iter__(self) -> Iterable[Optional[AQI]]:
        """Iterate over metrics"""
        return iter([self.CO, self.NO2, self.O3, self.PM2_5, self.PM10 ])


class AirNow:
    """
    Connection object to AirNow REST API

    Parameters:
        token (str): AirNow API authentication token.

    Parameters:
        token (str): AirNow API authentication token.
        client (Any): Any HTTP client implementing an interface
            the is requests compatible. Ex: requests, httpx.
    """
    def __init__(self, token: str, client: Any):
        self.client = client
        self.token = token

    def get_forecast(
        self,
        zip_code: str,
        date: datetime.date = datetime.date.today(),
        distance: int = 25,
    ) -> List[Forecast]:
        """
        Get a list of Forecast objects for the specified information.

        Parameters:
            zip_code (str): The U.S. postal zip code
            date (datetime.date): Defaults to current local date. The date
                of the day you want the forecast for.
            distance (int): The distance in miles from the zip code to
                look for data

        Returns:
            List[Forecasts]: A list of Forecast objects

        Raises:
            NoDataError: If an empty list is returned from the AirNow API.
        """
        formatted_date = date.strftime("%Y-%m-%d")
        url = (f"{FORECAST_BASE_URL}zipCode={zip_code}&date={formatted_date}"
                + f"&distance={distance}&API_KEY={self.token}")
        response = self.client.get(url)
        response.raise_for_status()
        data = response.json()
        if not data:
            raise NoDataError(f"No data for zip code {zip_code}.")
        return AirNow._build_forecasts(data)


    def get_current(
        self,
        zip_code: str,
        distance: int = 25
    ) -> Observation:
        """
        Gets current AQI data for the provided zip code.

        Parameters:
            zip_code (str): The U.S. postal zip code
            distance (int): The distance in miles from the zip code to
                look for data

        Returns:
            Observation: An Observation object with current AQI data.

        Raises:
            NoDataError: If an empty list is returned from the AirNow API.
        """
        url = (f"{OBSERVATION_BASE_URL}zipCode={zip_code}&distance={distance}"
                + f"&API_KEY={self.token}")
        response = self.client.get(url)
        response.raise_for_status()
        data = response.json()
        if not data:
            raise NoDataError(f"No data for zip code {zip_code}.")
        return AirNow._build_observation(data)

    @staticmethod
    def _build_forecasts(data: List[Dict[str,Any]]) -> List[Forecast]:
        """Builds a Forecast object from HTTP response data"""
        dates = {}
        for dp in data:
            dp_date = dp["DateForecast"]
            if dp_date in dates:
                dates[dp_date].append(dp)
            else:
                dates[dp_date] = [dp]

        forecasts = []
        for dp_list in dates.values():
            args: List[Any] = [
                datetime.date.fromisoformat(dp_list[0]["DateIssue"].rstrip()),
                datetime.date.fromisoformat(dp_list[0]["DateForecast"].rstrip()),
                dp_list[0]["ReportingArea"],
                dp_list[0]["StateCode"],
                dp_list[0]["Latitude"],
                dp_list[0]["Longitude"],
            ]
            kwargs = {}
            for dp in dp_list:
                aqi = AQI(
                    dp["ParameterName"],
                    dp["AQI"],
                    Severity(dp["Category"]["Number"]), dp["ActionDay"]
                )

                if dp["ParameterName"] == "PM2.5":
                    metric_name = "PM2_5"
                else:
                    metric_name = dp["ParameterName"]
                kwargs[metric_name] = aqi

            forecasts.append(Forecast(*args, **kwargs))

        return forecasts

    @staticmethod
    def _build_observation(data: List[Dict[str,Any]]) -> Observation:
        """Builds an Observation object from HTTP response data"""
        args: List[Any] = [
            datetime.date.fromisoformat(data[0]["DateObserved"].rstrip()),
            data[0]["HourObserved"],
            data[0]["LocalTimeZone"],
            data[0]["ReportingArea"],
            data[0]["StateCode"],
            data[0]["Latitude"],
            data[0]["Longitude"],
        ]
        kwargs = {}
        for dp in data:
            aqi = AQI(
                dp["ParameterName"],
                dp["AQI"],
                Severity(dp["Category"]["Number"])
            )

            if dp["ParameterName"] == "PM2.5":
                metric_name = "PM2_5"
            else:
                metric_name = dp["ParameterName"]
            kwargs[metric_name] = aqi

        return Observation(*args, **kwargs)


def get_timezone(tz: str) -> datetime.timezone:
    """Returns a timezone object for the provided tz"""
    offset = TIMEZONE_LOOKUP[tz]
    if offset < 0:
        delta = -datetime.timedelta(hours=abs(offset))
    else:
        delta = datetime.timedelta(hours=offset)
    return datetime.timezone(delta, tz)
