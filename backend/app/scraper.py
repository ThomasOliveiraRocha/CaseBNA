import requests
from bs4 import BeautifulSoup

def scrape_title(url: str) -> str:
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.title.string if soup.title else "No title found"
    except Exception as e:
        return f"Error: {e}"
