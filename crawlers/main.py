from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime

# Import crawlers
# from g2b.crawler import G2BCrawler (Disabled)
from kepco.crawler import KEPCOCrawler, SearchConfig

app = FastAPI(title="CarbonFlow Crawler API")

class SearchRequest(BaseModel):
    keyword: str
    days: int = 30

@app.get("/")
def health_check():
    return {"status": "ok", "service": "carbonflow-crawler"}

# @app.post("/crawl/g2b")
# def crawl_g2b(request: SearchRequest):
#     """G2B 나라장터 공고 검색"""
#     try:
#         with G2BCrawler() as crawler:
#             results = crawler.search_tenders(keyword=request.keyword)
#             return {"count": len(results), "results": results}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/crawl/kepco")
async def crawl_kepco(request: SearchRequest):
    """KEPCO SRM 공고 검색"""
    try:
        config = SearchConfig(
            keywords=[request.keyword],
            start_date=None, # Defaults in crawler
            end_date=None
        )
        async with KEPCOCrawler(headless=True) as crawler:
            results = await crawler.search(config)
            return {"count": len(results), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
