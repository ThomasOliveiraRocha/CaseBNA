from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.crud import get_cached_scrape, save_scrape
from app.scraping import scrape_data
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import UrlRequest  # <--- importa aqui

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/scrape")
def scrape(payload: UrlRequest, db: Session = Depends(get_db)):
    url = payload.url
    cached = get_cached_scrape(db, url)
    if cached:
        return {"source": "cache", "data": cached.content}
    data = scrape_data(url)
    save_scrape(db, url, data)
    return {"source": "scraped", "data": data}

@app.post("/analyze")
def analyze(payload: UrlRequest, db: Session = Depends(get_db)):
    url = payload.url
    cached = get_cached_scrape(db, url)
    if not cached:
        raise HTTPException(status_code=404, detail="URL não processada ainda. Faça scrape primeiro.")
    
    content = cached.content

    title = content.get("title", "Sem título")
    h1 = content.get("headings", {}).get("h1", [])
    h2 = content.get("headings", {}).get("h2", [])
    h3 = content.get("headings", {}).get("h3", [])
    emails = content.get("emails", [])
    phones = content.get("phones", [])
    paragraphs = content.get("paragraphs", [])
    meta_desc = content.get("meta_description", "")

    resumo = f"""
Análise Comercial da Página

Título da Página:
{title}

Descrição (meta tag):
{meta_desc or "Não encontrada."}

Estrutura de Conteúdo:
- {len(h1)} títulos H1
- {len(h2)} títulos H2
- {len(h3)} títulos H3
- {len(paragraphs)} parágrafos extraídos

Contatos:
- E-mails encontrados: {", ".join(emails) if emails else "Nenhum"}
- Telefones encontrados: {", ".join(phones) if phones else "Nenhum"}

Trecho do conteúdo:
{" ".join(paragraphs[:3])[:500]}...
""".strip()

    return {"resumo": resumo}
