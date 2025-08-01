from app.models import ScrapedSite, User
from sqlalchemy.orm import Session
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Scraping
def get_cached_scrape(db: Session, url: str):
    return db.query(ScrapedSite).filter(ScrapedSite.url == url).first()

def save_scrape(db: Session, url: str, content: dict):
    db_item = ScrapedSite(url=url, content=content)
    db.add(db_item)
    db.commit()

# Usuários
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, password: str):
    hashed = pwd_context.hash(password)
    user = User(username=username, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)
