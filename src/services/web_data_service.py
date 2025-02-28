import requests
from dotenv import load_dotenv
import os

load_dotenv('.env.local')  # Specify the correct file name

jina_api_key = os.getenv("jina_api_key")

# TODO: Handle this later
# def search_web(search_query, api_key):
#     # Bing Search API endpoint
#     endpoint = "https://api.bing.microsoft.com/v7.0/search"
    
#     # Set up the headers with the API key
#     headers = {"Ocp-Apim-Subscription-Key": api_key}
    
#     # Set up the parameters for the search
#     params = {"q": search_query, "textDecorations": True, "textFormat": "HTML"}
    
#     try:
#         # Make the request to the Bing Search API
#         response = requests.get(endpoint, headers=headers, params=params)
#         response.raise_for_status()  # Raise an error for bad responses
#         search_results = response.json()
#     except requests.exceptions.RequestException as e:
#         search_results = f"An error occurred: {e}"
    
#     return search_results

def read_web_url(url_to_read: str) -> str:
    """
    Fetches the content from a specified URL using the Jina API.

    This function sends a GET request to the Jina API with the provided URL
    and returns the content of the response. If an error occurs during the
    request, it returns an error message.

    Parameters:
    url_to_read (str): The URL path to append to the Jina API base URL.

    Returns:
    str: The content of the response if successful, or an error message if
    the request fails.
    """
    try:
        response = requests.get(
            f"https://r.jina.ai/{url_to_read}",
            headers={"Authorization": f"Bearer {jina_api_key}"}
        )
        response.raise_for_status()  # Raise an error for bad responses
        content = response.text
    except requests.exceptions.RequestException as e:
        content = f"An error occurred: {e}"

    return content
