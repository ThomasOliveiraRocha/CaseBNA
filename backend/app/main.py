from fastapi import FastAPI, Query
from app.scraper import scrape_title

app = FastAPI()

@app.get("/scrape")
def scrape(url: str = Query(..., description="URL to scrape")):
    title = scrape_title(url)
    return {"url": url, "title": title}