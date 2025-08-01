import re
import requests
from bs4 import BeautifulSoup

def scrape_data(url: str) -> dict:
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    data = {}

    # Título
    data['title'] = soup.title.string.strip() if soup.title else 'Sem título'

    # Headings
    data['headings'] = {
        'h1': [h.get_text(strip=True) for h in soup.find_all('h1')],
        'h2': [h.get_text(strip=True) for h in soup.find_all('h2')],
        'h3': [h.get_text(strip=True) for h in soup.find_all('h3')],
    }

    # Meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    data['meta_description'] = meta_desc['content'].strip() if meta_desc and meta_desc.get('content') else ''

    # Parágrafos + elementos adicionais
    text_blocks = soup.find_all(['p', 'span', 'div', 'li', 'a'])
    data['paragraphs'] = [el.get_text(strip=True) for el in text_blocks if el.get_text(strip=True)]

    # Texto plano completo
    full_text = soup.get_text(separator=' ', strip=True).lower()

    # E-mails
    data['emails'] = list(set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", full_text)))

    # Telefones (com DDD e separadores)
    data['phones'] = list(set(re.findall(r"\(?\d{2,3}\)?[\s.-]?\d{4,5}[\s.-]?\d{4}", full_text)))

    # Links de WhatsApp
    whatsapp_links = [
        a['href'] for a in soup.find_all('a', href=True)
        if 'whatsapp' in a['href'] or 'wa.me' in a['href']
    ]
    data['whatsapp_links'] = list(set(whatsapp_links))

    # Palavras-chave úteis para contato
    keywords = ['whatsapp', 'televendas', 'sac', 'atendimento', 'contato', 'chat', 'telefone']
    encontrados = [k for k in keywords if k in full_text]
    data['keywords_detected'] = encontrados

    # Verifica se há formulários
    forms = soup.find_all('form')
    data['has_form'] = len(forms) > 0

    return data
