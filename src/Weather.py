#############################################################
#                                                           #
# Weather Information Provided by: https://open-meteo.com   #
# Location Services Provided by: https://nominatim.org      #
#                                                           #
#############################################################

import httpx
import json

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "current": ["temperature_2m", "apparent_temperature", "wind_speed_10m", "wind_direction_10m",
                "dew_point_2m", "weather_code", "precipitation_probability"],
    "temperature_unit": "fahrenheit",
    "wind_speed_unit": "mph",
    "precipitation_unit": "inch",
    "forecast_days": 1
}

weatherCodes = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Fog",
    51: "Light Drizzle",
    53: "Drizzle",
    55: "Drizzle",
    56: "Freezing Drizzle",
    57: "Freezing Drizzle",
    61: "Light Rain",
    63: "Rain",
    65: "Heavy Rain",
    66: "Freezing Rain",
    67: "Freezing Rain",
    71: "Light Snow",
    73: "Snow",
    75: "Heavy Snow",
    77: "Snow Flurries",
    80: "Light Rain",
    81: "Rain",
    82: "Heavy Rain",
    85: "Snow",
    86: "Heavy Snow",
    95: "Thunderstorm",
    96: "Thunderstorm With Hail",
    99: "Thunderstorm With Hail",
}

def interpret_weather(weather):
    weatherString = ""
    temperatureUnit = {"fahrenheit": "°F", "celsius": "°C"}

    weatherString += f"Conditions: {weatherCodes[weather['current']['weather_code']]}. "
    weatherString += f"Temperature: {round(weather['current']['temperature_2m'])}{temperatureUnit[params['temperature_unit']]}. "
    weatherString += f"Feels Like: {round(weather['current']['apparent_temperature'])}{temperatureUnit[params['temperature_unit']]}. "
    weatherString += f"Dew Point: {round(weather['current']['dew_point_2m'])}{temperatureUnit[params['temperature_unit']]}. "
    weatherString += f"Chance of Precipitation: {round(weather['current']['precipitation_probability'])}%. "

    return weatherString

def get_location(locationName):

    apiURL = f"https://nominatim.openstreetmap.org/search?format=json&q={locationName}"
    geoResponse = httpx.get(
        url=apiURL,
        headers={"User-Agent": "WebSearch AI"},
        timeout=120
    )

    geoResponse.raise_for_status()

    geography = json.loads(geoResponse.text)

    # print(geography[0])

    params['longitude'] = geography[0]['lon']
    params['latitude'] = geography[0]['lat']

    return f"Location: {geography[0]['display_name']}. "



def get_weather(location = None, unit = None):
    params["temperature_unit"] = unit

    llmString = "\nCURRENT WEATHER RESULTS FROM API:\n"

    llmString += get_location(location)

    response = httpx.get(
        url=url,
        params=params
    )

    response.raise_for_status()

    weather = json.loads(response.text)

    llmString += interpret_weather(weather)

    return llmString
