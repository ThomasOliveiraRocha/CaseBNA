import re
import requests
from bs4 import BeautifulSoup

def scrape_data(url: str) -> dict:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    data = {}

    # Título
    data['title'] = soup.title.string if soup.title else 'Sem título'

    # Headings
    data['headings'] = {
        'h1': [h.get_text(strip=True) for h in soup.find_all('h1')],
        'h2': [h.get_text(strip=True) for h in soup.find_all('h2')],
        'h3': [h.get_text(strip=True) for h in soup.find_all('h3')],
    }

    # Meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    data['meta_description'] = meta_desc['content'] if meta_desc else ''

    # Parágrafos
    data['paragraphs'] = [p.get_text(strip=True) for p in soup.find_all('p')]

    # E-mails e telefones
    text = soup.get_text()
    data['emails'] = list(set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)))
    data['phones'] = list(set(re.findall(r"\(?\d{2,3}\)?[\s-]?\d{4,5}[-\s]?\d{4}", text)))

    return data
