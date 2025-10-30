from weather import get_weather
import responses
import json
from pathlib import Path


@responses.activate
def test_weather():
    # Load the mock response
    test_dir = Path(__file__).parent
    with open(f"{test_dir}/test_fixtures/openweather.json", "r") as f:
        mock_body = f.read()

    responses.add(
        responses.GET,
        "https://api.openweathermap.org/data/2.5/weather",
        json=json.loads(mock_body),
        status=200,
        content_type="application/json",
    )

    result = get_weather("London")
    assert (
        "The weather in London is scattered clouds with a temperature of 6.9C."
        == result
    )
