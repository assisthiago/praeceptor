from urllib.parse import urlencode

import requests
from django.conf import settings
from rest_framework import status

HEADERS = {"User-Agent": "Praeceptor/1.0 (praeceptor@praeceptor.com)"}


class NominatimAPI:

    @staticmethod
    def search(zip_code: str) -> tuple:
        """Search for latitude and longitude from Nominatim API by zip code.

        Args:
            zip_code (str): CEP to be geocoded.
        Returns:
            tuple or None: Latitude and longitude as a tuple if successful, None otherwise.
        """
        url = f"{settings.NOMINATIM_ENDPOINT}/search"
        params = {
            "q": f"{zip_code}, Brasil",
            "format": "json",
            "addressdetails": 1,
            "limit": 1,
        }

        try:
            response = requests.get(
                url=url,
                headers=HEADERS,
                params=params,
                timeout=5,
            )
        except requests.RequestException:
            return "RequestException", "RequestException"
        except requests.Timeout:
            return "Timeout", "Timeout"

        if response.status_code == status.HTTP_200_OK:
            try:
                response = response.json()
                lat = float(response[0].get("lat", None))
                lon = float(response[0].get("lon", None))
                return lat, lon
            except (KeyError, ValueError, IndexError, Exception) as e:
                return "Error", "Error"

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return "Not Found", "Not Found"

        if response.status_code == status.HTTP_403_FORBIDDEN:
            return "Forbidden", "Forbidden"

        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            return "Too Many Requests", "Too Many Requests"

        if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            return "Internal Server Error", "Internal Server Error"

        return "Error", "Error"


class ViaCEPAPI:

    @staticmethod
    def search(zip_code: str) -> dict:
        """Search for address data from ViaCEP API by zip code.

        Args:
            zip_code (str): CEP to be consulted.
        Returns:
            dict or str: Address data as a dictionary if successful, error string otherwise.
        """
        url = f"{settings.VIACEP_ENDPOINT}/{zip_code}/json/"

        try:
            response = requests.get(
                url=url,
                headers=HEADERS,
                timeout=5,
            )
        except requests.RequestException:
            return "RequestException"
        except requests.Timeout:
            return "Timeout"

        if response.status_code == status.HTTP_200_OK:
            try:
                response = response.json()
                return dict(
                    street=response.get("logradouro"),
                    neighborhood=response.get("bairro"),
                    city=response.get("localidade"),
                    state=response.get("uf"),
                    region=response.get("regiao"),
                    country="Brasil",
                )
            except (KeyError, ValueError, IndexError, Exception) as e:
                return "Error"

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return "Not Found"

        if response.status_code == status.HTTP_403_FORBIDDEN:
            return "Forbidden"

        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            return "Too Many Requests"

        if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            return "Internal Server Error"

        return "Error"
