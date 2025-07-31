from .models import ScrapedSite
from sqlalchemy.orm import Session

def get_cached_scrape(db: Session, url: str):
    return db.query(ScrapedSite).filter(ScrapedSite.url == url).first()

def save_scrape(db: Session, url: str, content: dict):
    db_item = ScrapedSite(url=url, content=content)
    db.add(db_item)
    db.commit()
