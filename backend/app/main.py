from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.crud import get_cached_scrape, save_scrape
from app.scraping import scrape_data
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import UrlRequest
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Security
from app import auth, crud, schemas
from app.models import ScrapedSite  # para o painel admin funcionar

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = auth.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    return payload
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
#------------------------------------------------------------------
#------------------------autenticacao------------------------------  
#------------------------------------------------------------------   
@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Usuário já existe")
    crud.create_user(db, user.username, user.password)
    return {"msg": "Usuário criado com sucesso"}

@app.post("/login", response_model=schemas.TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    token = auth.create_access_token(data={"sub": user.username, "is_admin": user.is_admin})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/admin/sites")
def admin_sites(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Acesso restrito ao administrador")
    
    sites = db.query(ScrapedSite).order_by(ScrapedSite.scraped_at.desc()).all()
    return [{"url": s.url, "scraped_at": s.scraped_at.isoformat()} for s in sites]


#------------------------------------------------------------------
#--------------------------Busca-----------------------------------  
#------------------------------------------------------------------  
@app.post("/scrape")
def scrape(payload: UrlRequest, db: Session = Depends(get_db)):
    url = payload.url
    cached = get_cached_scrape(db, url)
    if cached:
        return {"source": "cache", "data": cached.content}
    data = scrape_data(url)
    save_scrape(db, url, data)
    return {"source": "scraped", "data": data}

#------------------------------------------------------------------
#------------------------Resumo------------------------------------  
#------------------------------------------------------------------  
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

    # Construindo as recomendações de forma clara e prática
    email_info = "Email disponível: {}".format(", ".join(emails)) if emails else "Email não identificado"
    phone_info = "Telefone disponível: {}".format(", ".join(phones)) if phones else "Telefone não identificado"
    content_richness = ("A página contém conteúdo detalhado, com {} parágrafos, o que indica informações úteis para análise."
                        .format(len(paragraphs)) if len(paragraphs) > 30 else
                        "Conteúdo limitado, pode não ser suficiente para análises detalhadas.")
    title_structure = ("A página possui {} títulos H1 e {} títulos H2, indicando boa estrutura para navegação e SEO."
                       .format(len(h1), len(h2)) if (len(h1) + len(h2)) > 0 else
                       "A estrutura de títulos está fraca, o que pode dificultar navegação e análise.")
    
    trecho = " ".join(paragraphs[:3]).strip()
    if len(trecho) > 500:
        trecho = trecho[:500] + "..."

    resumo = f"""
Análise Comercial da Página

Título da Página:
{title}

Descrição:
{meta_desc or "Não encontrada."}

Resumo do Conteúdo:
- {len(h1)} título(s) H1
- {len(h2)} título(s) H2
- {len(h3)} título(s) H3
- {len(paragraphs)} parágrafo(s) extraídos

Informações de Contato:
- {email_info}
- {phone_info}

Trecho Relevante do Conteúdo:
{trecho}

Recomendações para a equipe de vendas:
- {email_info}, permite contato direto para negociações ou dúvidas.
- {phone_info}, pode exigir abordagem alternativa se ausente.
- {content_richness}
- {title_structure}

Conclusão:
Este site apresenta dados que podem ser úteis para prospecção e abordagem comercial, com contatos e informações suficientes para embasar conversas.
""".strip()

    return {"resumo": resumo}

