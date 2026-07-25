import logging
import pandas as pd
import requests
from bs4 import BeautifulSoup

def extract_weather_from_sinoptik(city: str = "sofia") -> pd.DataFrame:
    url = "https://www.sinoptik.bg/sofia-bulgaria-100727011"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0"
        )
    }

    logging.info(f"Requesting weather data from {city}")

    try:
        response = requests.get(url=url, headers=headers, timeout=10)
    except Exception:
        logging.info(f"Network error fetching weather data from {url}")
        raise

    temperature = None
    feel = None

    try:
        soup = BeautifulSoup(response.content, features="html.parser")

        temp_node = soup.find(name="span", class_="wfCurrentTemp")
        feel_node = soup.find(name="span", class_="wfCurrentFeelTemp")

        temperature = temp_node.text.strip() if temp_node else None
        feel = feel_node.text.strip() if feel_node else None

        if temperature is None or feel is None:
            raise ValueError("could not parse weather data from Sinoptik HTML")

    except Exception:
        logging.error(f"Parsing error for Sinoptik weather data from {url}")

    df = pd.DataFrame({
        "city": [city.capitalize()],
        "temperature": [temperature],
        "feel": [feel],
    })

    logging.info(f"Sinoptik weather data extracted from {city}")
    return df