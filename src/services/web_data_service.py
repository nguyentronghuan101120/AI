import requests
from dotenv import load_dotenv
import os

load_dotenv('.env.local')  # Specify the correct file name

jina_api_key = os.getenv("jina_api_key")
brave_search_api_key = os.getenv("brave_search_api_key")

#TODO: Use this for free search
# def search_web_with_duckduckgo(search_query: str) -> list[dict[str, str]]:
#     """
#     Performs a web search using the provided search query and returns structured results.
#     This search totally free but it's does not have high accuracy.

#     Parameters:
#     search_query (str): The search query string to look up

#     Returns:
#     list[dict[str, str]]: A list of dictionaries containing search results with 'title', 'link', and 'snippet' keys.
#     """
#     headers = {
#         'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
#     }
    
#     try:
#         response = requests.get(
#             f'https://html.duckduckgo.com/html/?q={search_query}',
#             headers=headers,
#             timeout=10  # Add timeout to prevent hanging
#         )
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.text, 'html.parser')
#         results = soup.find_all('div', class_='result')[:10]  # Limit to first 10 results immediately
        
#         return [
#             {
#                 'title': title_tag.text,
#                 'link': title_tag['href'],
#                 'snippet': snippet_tag.text if (snippet_tag := result.find('a', class_='result__snippet')) else 'No description available'
#             }
#             for result in results
#             if (title_tag := result.find('a', class_='result__a'))
#         ]
        
#     except requests.exceptions.RequestException as e:
#         print(f"Error during web search: {e}")
#         return []
    
def web_search_with_3rd_party(search_query: str) -> list[dict[str, str]]:
    """
    Performs a web search using the Brave Search API and returns structured results.
    
    This function makes an API call to Brave Search to retrieve web search results for the given query.
    The results are limited to 10 items by default and include title, URL, and description for each result.
    
    Parameters:
        search_query (str): The search query string to look up on the web.
        
    Returns:
        list[dict[str, str]]: A list of dictionaries containing search results, where each dictionary has:
            - 'title': The title of the search result (str)
            - 'link': The URL of the search result (str)
            - 'description': A brief description of the search result (str)
            
    Note:
        If the API call fails or no results are found, an empty list is returned.
        The function requires a valid Brave Search API key to be set in the environment variables.
    """
    from bs4 import BeautifulSoup
    
    
    url = f"https://api.search.brave.com/res/v1/web/search"
    
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": brave_search_api_key
    }
    
    params = {
        "q": search_query,
        "count": 10,
        "offset": 0,
        "filter": "web"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        
        for item in data.get("web", {}).get("results", []):
            results.append({
                "title": item.get("title", "No title available"),
                "link": item.get("url", "No link available"),
                "description": item.get("description", "No description available")
            })
            
        return results
    
    except requests.exceptions.RequestException as e:   
        print(f"Error during web search: {e}")
        return []

def read_web_url(url: str) -> str:
    """
    Fetches the content from a specified URL using the Jina API.

    This function sends a GET request to the Jina API with the provided URL
    and returns the content of the response. If an error occurs during the
    request, it returns an error message.

    Parameters:
    url (str): The URL path to append to the Jina API base URL.

    Returns:
    str: The content of the response if successful, or an error message if
    the request fails.
    """
    try:
        response = requests.get(
            f"https://r.jina.ai/{url}",
            headers={"Authorization": f"Bearer {jina_api_key}"}
        )
        response.raise_for_status()  # Raise an error for bad responses
        content = response.text
    except requests.exceptions.RequestException as e:
        content = f"An error occurred: {e}"

    return content
