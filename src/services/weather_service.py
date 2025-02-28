import requests

# NOTE: read this doc for more info: https://open-meteo.com/en/docs
def fetch_weather_data(latitude: float, longitude: float, unit: str = "metric"):
    """
    Fetches weather forecast data for a given location.

    This function retrieves weather forecast data for the specified latitude and longitude
    using the Open-Meteo API. The data includes daily maximum and minimum temperatures,
    as well as precipitation sums for a 7-day forecast period.

    Parameters:
    - latitude (float): The latitude of the location for which to fetch weather data.
    - longitude (float): The longitude of the location for which to fetch weather data.
    - unit (str, optional): The unit system to use for the weather data. Defaults to "metric".

    Returns:
    - dict: A dictionary containing the weather forecast data if the request is successful.
      If the request fails, a dictionary with an error message is returned.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "units": unit,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "forecast_days": 7,
        "timezone": "auto"
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Request failed with status code {response.status_code}"}

