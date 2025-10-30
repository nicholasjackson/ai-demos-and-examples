import requests
import os
from pydantic import BaseModel, ValidationError, field_validator
from typing import List


class WeatherMain(BaseModel):
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int


class Weather(BaseModel):
    description: str
    main: str


class WeatherResponse(BaseModel):
    weather: List[Weather]
    main: WeatherMain

    @field_validator("weather")
    @classmethod
    def get_first_weather(cls, v):
        return v[0]


def get_weather(location: str) -> str:
    """Fetch weather information for a given location."""

    api_key = os.getenv("WEATHER_API_KEY")
    params = {
        "q": location,
        "appid": api_key,
    }

    url = "https://api.openweathermap.org/data/2.5/weather"
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return f"Could not retrieve weather for {location}, error: {response.content.decode('utf-8')}."

    try:
        weather_data = WeatherResponse.model_validate(response.json())
    except ValidationError as e:
        return f"Error parsing weather data for {location}: {e}"

    return f"The weather in {location} is {weather_data.weather.description} with a temperature of {kelvin_to_celsius(weather_data.main.temp)}C."


def kelvin_to_celsius(kelvin):
    temp = kelvin - 273.15
    return f"{temp:.1f}"
