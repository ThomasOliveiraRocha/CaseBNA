from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ScrapedSite(Base):
    __tablename__ = "scraped_sites"
    url = Column(String, primary_key=True)
    content = Column(JSON)
    scraped_at = Column(DateTime, default=datetime.utcnow)
