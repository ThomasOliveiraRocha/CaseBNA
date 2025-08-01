from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.crud import get_cached_scrape, save_scrape
from app.scraping import scrape_data
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import UrlRequest
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Security, Body
from app import auth, crud, schemas
from app.models import ScrapedSite  
import re
from collections import Counter


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
ADMIN_CREATION_PASSWORD = "admin123"

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

@app.get("/me")
def read_users_me(current_user=Depends(get_current_user)):
    return current_user

@app.get("/admin/sites")
def admin_sites(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Acesso restrito ao administrador")
    
    sites = db.query(ScrapedSite).order_by(ScrapedSite.scraped_at.desc()).all()
    return [{"url": s.url, "scraped_at": s.scraped_at.isoformat()} for s in sites]

@app.post("/create-admin")
def create_admin(
    username: str = Body(...),
    password: str = Body(...),
    admin_password: str = Body(...),
    db: Session = Depends(get_db),
):
    if admin_password != ADMIN_CREATION_PASSWORD:
        raise HTTPException(status_code=403, detail="Senha de admin inválida")

    if crud.get_user_by_username(db, username):
        raise HTTPException(status_code=400, detail="Usuário já existe")

    crud.create_user(db, username, password, is_admin=True)
    return {"msg": f"Usuário admin '{username}' criado com sucesso"}


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
#--------------------------Separar Palavras------------------------  
#------------------------------------------------------------------ 
STOPWORDS = {
    "de", "a", "o", "que", "e", "do", "da", "em", "um", "para", "com", "não", "uma",
    "os", "no", "se", "na", "por", "mais", "as", "dos", "como", "mas", "foi", "ao",
    "ele", "das", "tem", "à", "seu", "sua", "ou", "ser", "quando", "muito", "há",
    "nos", "já", "está", "eu", "também", "só", "pelo", "pela", "até", "isso", "ela",
    "entre", "era", "depois", "sem", "mesmo", "aos", "ter", "seus", "quem", "nas",
    "me", "esse", "eles", "estão", "você", "tinha", "foram", "essa", "num", "nem",
    "suas", "meu", "às", "minha", "têm", "numa", "pelos", "elas", "havia", "seja",
    "qual", "será", "nós", "tenho", "lhe", "deles", "essas", "esses", "pelas",
    "este", "fosse", "dele", "tu", "te", "vocês", "vos", "lhes", "meus", "minhas",
    "teu", "tua", "teus", "tuas", "nosso", "nossa", "nossos", "nossas", "dela",
    "delas", "esta", "estes", "estas", "aquele", "aquela", "aqueles", "aquelas",
    "isto", "aquilo", "estou", "está", "estamos", "estão", "estive", "esteve",
    "estivemos", "estiveram", "estava", "estávamos", "estavam", "estivera",
    "estivéramos", "hei", "há", "havemos", "hão", "houve", "houvemos", "houveram",
    "houvera", "houvéramos", "haja", "hajamos", "hajam", "houve", "houvemos",
    "houverem", "houverei", "houverá", "houveremos", "houverão", "houveria",
    "houveríamos", "houvesse", "houvéssemos", "houvessem", "havendo", "hedes",
    "hei", "há", "houvemos", "houveram", "off"
}

def extract_topics(headings):
    # Junta todas as headings numa lista e separa as palavras
    words = []
    for h in headings:
        for w in re.findall(r'\b\w+\b', h.lower()):
            if w not in STOPWORDS and len(w) > 2:
                words.append(w)
    counter = Counter(words)
    # Pega as 5 palavras mais comuns como "temas"
    top_words = [word for word, count in counter.most_common(5)]
    return top_words

#------------------------------------------------------------------
#------------------------Resumo------------------------------------  
#------------------------------------------------------------------  
@app.post("/analyze")
def analyze(payload: UrlRequest, db: Session = Depends(get_db)):
    import re
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
    paragraphs = content.get("paragraphs", []) or []
    meta_desc = content.get("meta_description", "")
    all_headings = h1 + h2 + h3
    texto_conteudo = " ".join(paragraphs).lower()
    whatsapp_links = content.get("whatsapp_links", [])
    keywords_detected = content.get("keywords_detected", [])
    has_form = content.get("has_form", False)

    # Conjunto maior de palavras irrelevantes para ramo/produtos (stopwords + extras)
    PALAVRAS_DESCARTADAS = STOPWORDS.union({
        "categoria", "frete", "grátis", "brasil", "pagamento", "oferta", "loja", "produto",
        "serviço", "item", "curso", "consult", "promoção", "site", "online", "compre", "agora",
        "entrega", "desconto", "parcelamento"
    })

    def extract_ramo_from_title(title):
        import re

        # Lista básica e genérica de termos de nichos mais comuns, para tentar identificar ramo
        nichos_comuns = [
            "moda", "roupa", "roupas", "calçado", "calçados",
            "eletrônico", "eletrônicos", "tecnologia", "alimentação", "alimentos",
            "cosmético", "cosméticos", "educação", "serviço", "serviços",
            "imóvel", "imóveis", "automóvel", "automóveis", "esporte", "esportes",
            "brinquedo", "brinquedos", "livro", "livros", "jogos", "game", "games",
            "bebida", "bebidas", "ferramenta", "ferramentas", "casa", "casas"
        ]

        # Stopwords básicas para título, além das já existentes
        stopwords_title = set([
            "loja", "site", "online", "ecommerce", "comércio", "virtual", "oficial",
            "br", "ofertas", "oferta", "promoção", "promoções", "desconto",
            "frete", "grátis", "compre", "agora", "melhor", "para", "de", "do", "da",
            "e", "a", "o", "em", "no", "na"
        ])

        # Limpar título: tirar caracteres especiais e quebrar em palavras
        palavras = re.findall(r'\b\w+\b', title.lower())

        # Filtrar stopwords do título
        palavras_filtradas = [p for p in palavras if p not in stopwords_title and len(p) > 2]

        # Procurar nicho comum nas palavras filtradas
        for p in palavras_filtradas:
            if p in nichos_comuns:
                return p.capitalize()

        # Se não achou nicho, usar as primeiras palavras relevantes (até 3)
        if palavras_filtradas:
            return " ".join(palavras_filtradas[:3]).capitalize()

        return "Indefinido"


    # === No seu código analyze ===
    temas = extract_topics(all_headings)

    # Filtrar temas removendo palavras descartadas
    temas_filtrados = [t for t in temas if t not in PALAVRAS_DESCARTADAS]

    # Tentar ramo pelos temas filtrados
    ramo = next((t.capitalize() for t in temas_filtrados), None)

    # Se não encontrou ramo válido nos temas, extrai do título
    if not ramo or ramo == "Indefinido":
        ramo = extract_ramo_from_title(title)

    # Produtos em destaque (produtos_venda)
    produtos_venda = temas_filtrados
    if not produtos_venda:
        produtos_venda = temas[:3]  # fallback

    # === Contato ===
    contato_email = ", ".join(emails) if emails else None
    contato_telefone = ", ".join(phones) if phones else None
    whatsapps = ", ".join(whatsapp_links) if whatsapp_links else None

    if not any([contato_email, contato_telefone, whatsapps]):
        contato_info = "Nenhum contato direto (email, telefone ou WhatsApp) encontrado. Verifique canais alternativos como chat, redes sociais ou formulários."
    else:
        contato_info = ""
        if contato_email:
            contato_info += f"Emails: {contato_email}. "
        if contato_telefone:
            contato_info += f"Telefones: {contato_telefone}. "
        if whatsapps:
            contato_info += f"WhatsApp(s): {whatsapps}. "

    # === Horário de atendimento ===
    horario_atendimento = None
    for p in paragraphs:
        if re.search(r'\b(?:segunda|terça|quarta|quinta|sexta|sábado|domingo)\b', p.lower()):
            horario_atendimento = p.strip()
            break

    # === Ticket médio ===
    raw_prices = []
    for p in paragraphs + h2 + h3:
        matches = re.findall(r"R\$ ?\d{1,3}(?:\.\d{3})*(?:,\d{2})?", p)
        raw_prices.extend(matches)

    # Remover duplicados e normalizar os valores
    def parse_price(p):
        return float(p.replace("R$", "").replace(".", "").replace(",", ".").strip())

    unique_prices = sorted(set(parse_price(p) for p in raw_prices if "0,00" not in p))
    ticket_medio_fmt = [f"R$ {p:,.2f}".replace(".", "X").replace(",", ".").replace("X", ",") for p in unique_prices]

    # === CTA ===
    cta_present = any(
        frase in texto_conteudo
        for frase in ["compre agora", "fale conosco", "contate-nos", "solicite orçamento", "entre em contato"]
    )
    cta_text = "Sim" if cta_present else "Não"

    # === Perguntas estratégicas ===
    perguntas = []
    for palavra in temas[:5]:
        perguntas.append(f"- O que o site comunica sobre '{palavra}'?")
    if not any([contato_email, contato_telefone, whatsapps]):
        perguntas.append("- Como contatar o cliente, considerando que não há telefone, email ou WhatsApp visíveis?")
    if ticket_medio_fmt:
        faixa_menor = ticket_medio_fmt[0]
        faixa_maior = ticket_medio_fmt[-1]
        perguntas.append(f"- Qual a faixa de preços praticada? Ex: de {faixa_menor} a {faixa_maior}")
    perguntas.append(f"- O site parece incentivar a conversão direta? (Chamada para ação: {cta_text})")

    # === Montar resumo ===
    resumo = f"""
Análise Comercial da Página: {title}

Meta descrição:
{meta_desc or 'Não encontrada.'}

Ramo de atuação sugerido:
{ramo}

Temas principais extraídos das headings:
{', '.join(temas) if temas else "Nenhum tema claro identificado."}

Possíveis produtos ou serviços em destaque:
- {'; '.join(produtos_venda) if produtos_venda else 'Não identificado'}

Contatos encontrados:
{contato_info}

Outros meios de contato mencionados no texto:
{', '.join(keywords_detected) if keywords_detected else 'Nenhum termo específico encontrado.'}

Formulário de contato detectado:
{"Sim" if has_form else "Não"}

Horário de atendimento:
{horario_atendimento or 'Não identificado'}

Faixas de preço encontradas (possível ticket médio):
{', '.join(ticket_medio_fmt) if ticket_medio_fmt else 'Não identificado'}

Possui chamada para ação?
{cta_text}

Perguntas estratégicas para a equipe de vendas:
{chr(10).join(perguntas)}
""".strip()

    return {"resumo": resumo}
