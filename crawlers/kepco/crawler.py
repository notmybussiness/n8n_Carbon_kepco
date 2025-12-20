"""
CarbonFlow - KEPCO SRM 크롤러 V4 (Browser Agent 기반)
======================================================
Browser Agent 탐색 결과 기반 개선:
- 실제 발견된 네비게이션 경로 (정보공개 → 통합공고)
- 동적 ID 패턴 대응 (textfield-XXXX-inputEl)
- ExtJS 로딩 마스크 대기
- 첨부파일 탭 (공고문) 접근

사용법:
    python crawler.py --keyword "유연탄" --headed
"""
import os
import asyncio
import argparse
import json
import logging
import re
from datetime import datetime, timedelta
from typing import List, Optional
from dataclasses import dataclass, asdict
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Import Repository Integration
try:
    # Local development (run from workflow_n8n/ root)
    from crawlers.dto import TenderDTO, TenderSpecDTO, TenderSource, TenderStatus
    from crawlers.repository import SupabaseRepository
    from crawlers.kepco.parser import HWPParser
except ImportError:
    # Docker container (run from /app/)
    from dto import TenderDTO, TenderSpecDTO, TenderSource, TenderStatus
    from repository import SupabaseRepository
    from kepco.parser import HWPParser

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# =====================================================
# 데이터 모델
# =====================================================

@dataclass
class SearchConfig:
    """검색 설정"""
    keywords: List[str]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    max_results: int = 100
    
    @classmethod
    def default(cls):
        end = datetime.now()
        start = end - timedelta(days=30)
        return cls(
            keywords=["유연탄", "석탄", "연료탄"],
            start_date=start.strftime("%Y/%m/%d"),
            end_date=end.strftime("%Y/%m/%d"),
        )


@dataclass
class TenderResult:
    """입찰 공고 결과"""
    announcement_no: str
    title: str
    organization: str
    bid_method: str
    announce_date: str
    close_date: str
    status: str
    detail_url: str
    keyword_matched: str
    crawled_at: str
    attachments: List[str] = None


# =====================================================
# KEPCO SRM 크롤러 V4
# =====================================================

class KEPCOCrawler:
    """
    한전 전자조달시스템 (KEPCO SRM) 크롤러 - V4
    
    Browser Agent 탐색 결과 기반:
    - 정보공개 → 통합공고 네비게이션
    - 동적 ID 패턴 대응
    - ExtJS 로딩 마스크 대기
    """
    
    BASE_URL = "https://srm.kepco.net"
    SEARCH_URL = "https://srm.kepco.net/index.do"
    
    # 발견된 동적 ID 패턴 (숫자 부분은 변동됨)
    SELECTOR_PATTERNS = {
        # 입력 필드 - 동적 ID 패턴
        "search_input": "[id^='textfield-'][id$='-inputEl']",
        "search_button": ".x-btn-text:has-text('조회')",
        "search_button_fallback": "[id^='button-']:has-text('조회')",
        
        # 드롭다운 (검색 카테고리)
        "category_dropdown": "[id^='combo-'][id$='-inputEl']",
        
        # 날짜 입력
        "date_start": "[id^='ext-comp-'][id$='-inputEl']:nth-of-type(1)",
        "date_end": "[id^='ext-comp-'][id$='-inputEl']:nth-of-type(2)",
        
        # 그리드 결과
        "grid_view": "[id^='gridview-']",
        "grid_rows": ".x-grid-row",
        "grid_cells": ".x-grid-cell-inner",
        
        # 로딩 마스크
        "loading_mask": ".x-mask, .x-mask-loading",
        
        # 네비게이션 메뉴
        "menu_info": "#menuitem-1105-itemEl, .x-menu-item-text:has-text('통합공고')",
        
        # 상세 페이지
        "notice_tab": ".x-tab-inner:has-text('공고문')",
        "download_button": ".x-btn-text:has-text('공고문저장')",
    }
    
    def __init__(self, headless: bool = True, download_dir: str = "downloads"):
        self.headless = headless
        self.download_dir = download_dir
        self.browser: Optional[Browser] = None
        self.playwright = None
        
        # Initialize Supabase Repository
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.repo = SupabaseRepository(url, key) if url and key else None
        
        if not self.repo:
            logger.warning("Supabase URL/KEY not found in env. Data will not be saved to DB.")

        
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, *args):
        await self.close()
    
    async def start(self):
        """브라우저 시작 - 스텔스 설정"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
        )
        os.makedirs(self.download_dir, exist_ok=True)
        logger.info(f"Browser started (headless={self.headless})")
    
    async def close(self):
        """브라우저 종료"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser closed")
    
    async def _create_context(self):
        """브라우저 컨텍스트 생성"""
        return await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="ko-KR",
            timezone_id="Asia/Seoul",
            accept_downloads=True,
        )
    
    async def _wait_for_loading(self, page: Page, timeout: int = 10000):
        """ExtJS 로딩 마스크가 사라질 때까지 대기"""
        try:
            mask = page.locator(self.SELECTOR_PATTERNS["loading_mask"])
            await mask.wait_for(state="hidden", timeout=timeout)
        except PlaywrightTimeout:
            pass  # No loading mask or already hidden
    
    async def _navigate_to_announcements(self, page: Page):
        """통합공고 페이지로 이동 (정보공개 → 통합공고)"""
        logger.info("Navigating to 통합공고 page...")
        
        # 정보공개 메뉴 클릭 시도 (여러 방법)
        try:
            # 방법 1: 메뉴 자바스크립트로 직접 호출
            await page.evaluate("""
                () => {
                    // ExtJS 메뉴 시스템 직접 호출 시도
                    var menuItem = document.querySelector('[id*="menuitem"][id*="itemEl"]');
                    if (menuItem && menuItem.innerText.includes('통합공고')) {
                        menuItem.click();
                        return true;
                    }
                    // 정보공개 메뉴 찾기
                    var menus = document.querySelectorAll('.x-menu-item-text');
                    for (var m of menus) {
                        if (m.innerText.includes('통합공고')) {
                            m.click();
                            return true;
                        }
                    }
                    return false;
                }
            """)
        except Exception as e:
            logger.warning(f"Menu navigation via JS failed: {e}")
        
        # 페이지 로딩 대기
        await self._wait_for_loading(page)
        await asyncio.sleep(2)  # ExtJS 렌더링 대기
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((PlaywrightTimeout, Exception)),
        before_sleep=lambda rs: logger.warning(f"Retry attempt {rs.attempt_number}")
    )
    async def search(self, config: SearchConfig) -> List[TenderResult]:
        """입찰 공고 검색"""
        if not self.browser:
            await self.start()
        
        all_results = []
        context = await self._create_context()
        page = await context.new_page()
        
        try:
            # 메인 페이지 접속
            logger.info(f"Navigating to {self.SEARCH_URL}")
            await page.goto(self.SEARCH_URL, wait_until="domcontentloaded", timeout=30000)
            await self._wait_for_loading(page)
            await asyncio.sleep(3)  # ExtJS 초기화 대기
            
            # 통합공고 페이지로 이동
            await self._navigate_to_announcements(page)
            
            # 각 키워드로 검색
            for keyword in config.keywords:
                logger.info(f"Searching: {keyword}")
                results = await self._search_keyword(page, keyword, config)
                
                for r in results:
                    r.keyword_matched = keyword
                    
                all_results.extend(results)
                logger.info(f"Found {len(results)} results for '{keyword}'")
                
        except Exception as e:
            logger.error(f"Crawling error: {e}")
            timestamp = datetime.now().strftime('%H%M%S')
            await page.screenshot(path=f"{self.download_dir}/error_{timestamp}.png")
            raise
            
        finally:
            await context.close()
        
        # 중복 제거
        unique = {r.announcement_no: r for r in all_results}
        return list(unique.values())
    
    async def _search_keyword(self, page: Page, keyword: str, config: SearchConfig) -> List[TenderResult]:
        """키워드로 검색 - 동적 ID 패턴 대응"""
        results = []
        
        try:
            # 검색어 입력 (동적 ID 패턴 사용)
            search_input = page.locator(self.SELECTOR_PATTERNS["search_input"]).first
            await search_input.click()
            await search_input.fill("")
            await search_input.type(keyword, delay=50)
            
            # 날짜 범위 설정 (옵션)
            if config.start_date:
                try:
                    date_inputs = page.locator("[id*='ext-comp-'][id$='-inputEl']")
                    count = await date_inputs.count()
                    if count >= 2:
                        await date_inputs.nth(0).fill(config.start_date)
                        await date_inputs.nth(1).fill(config.end_date or datetime.now().strftime("%Y/%m/%d"))
                except Exception as e:
                    logger.debug(f"Date filter skipped: {e}")
            
            # 조회 버튼 클릭
            try:
                search_btn = page.locator(self.SELECTOR_PATTERNS["search_button"]).first
                await search_btn.click()
            except:
                # Fallback: ID 패턴으로 시도
                search_btn = page.locator(self.SELECTOR_PATTERNS["search_button_fallback"]).first
                await search_btn.click()
            
            # 결과 로딩 대기
            await self._wait_for_loading(page)
            await asyncio.sleep(2)
            
            # 결과 파싱
            results = await self._parse_results(page)
            
        except Exception as e:
            logger.warning(f"Search error for '{keyword}': {e}")
        
        return results
    
    async def _parse_results(self, page: Page) -> List[TenderResult]:
        """검색 결과 파싱 - 그리드에서 데이터 추출 및 DB 저장"""
        results = []
        
        try:
            # 그리드 행 가져오기
            rows = page.locator(self.SELECTOR_PATTERNS["grid_rows"])
            row_count = await rows.count()
            logger.debug(f"Found {row_count} grid rows")
            
            for i in range(min(row_count, 50)):
                row = rows.nth(i)
                cells = row.locator(self.SELECTOR_PATTERNS["grid_cells"])
                
                cell_count = await cells.count()
                if cell_count >= 5:
                    texts = []
                    for j in range(min(cell_count, 7)):
                        txt = await cells.nth(j).inner_text()
                        texts.append(txt.strip())
                    
                    if texts[0]:  # 공고번호 있음
                        tender_result = TenderResult(
                            announcement_no=texts[0] if len(texts) > 0 else "",
                            title=texts[1] if len(texts) > 1 else "",
                            organization=texts[2] if len(texts) > 2 else "",
                            bid_method=texts[3] if len(texts) > 3 else "",
                            announce_date=texts[4] if len(texts) > 4 else "",
                            close_date=texts[5] if len(texts) > 5 else "",
                            status=texts[6] if len(texts) > 6 else "",
                            detail_url=f"{self.BASE_URL}/notice/{texts[0]}",
                            keyword_matched="",
                            crawled_at=datetime.now().isoformat(),
                            attachments=[]
                        )
                        results.append(tender_result)

                        # Save to Supabase
                        if self.repo:
                            try:
                                # Parse dates safely
                                bid_clse_dt = None
                                if tender_result.close_date:
                                    try:
                                        # Format check: 2024/01/01 18:00
                                        bid_clse_dt = datetime.strptime(tender_result.close_date, "%Y/%m/%d %H:%M")
                                    except ValueError:
                                        pass

                                dto = TenderDTO(
                                    bid_ntce_no=tender_result.announcement_no,
                                    bid_ntce_ord="00", # Default
                                    source=TenderSource.KEPCO,
                                    bid_ntce_nm=tender_result.title,
                                    dminstt_nm=tender_result.organization,
                                    bid_clse_dt=bid_clse_dt,
                                    bid_ntce_dtl_url=tender_result.detail_url,
                                    status=TenderStatus.OPEN, # Default, logic can be improved
                                    raw_api_response=asdict(tender_result)
                                )
                                self.repo.upsert_tender(dto)
                                logger.info(f"Saved to DB: {tender_result.announcement_no}")
                            except Exception as db_err:
                                logger.error(f"DB Save Error: {db_err}")

        except Exception as e:
            logger.error(f"Parse Result Error: {e}")

        return results

    async def process_attachments(self, tender_id: str, file_paths: List[str]):
        """첨부파일(HWP) 처리 및 스펙 추출"""
        if not self.repo:
            return

        parser = HWPParser()
        for path in file_paths:
            if not os.path.exists(path):
                continue
                
            if path.lower().endswith('.hwp'):
                try:
                    logger.info(f"Parsing HWP: {path}")
                    text = parser.extract_text(path)
                    specs = parser.parse_specs(text)
                    
                    if specs:
                        logger.info(f"Extracted Specs: {specs}")
                        # DTO 생성
                        spec_dto = TenderSpecDTO(
                            tender_id=tender_id,
                            calorific_value=specs.get("gcv"),
                            sulfur_content=specs.get("sulfur"),
                            ash_content=specs.get("ash"),
                            moisture_content=specs.get("moisture"),
                            volatile_matter=specs.get("volatile"),
                        )
                        self.repo.upsert_tender_spec(spec_dto)
                except Exception as e:
                    logger.error(f"HWP Parsing failed for {path}: {e}")


# =====================================================
# CLI
# =====================================================

def main():
    parser = argparse.ArgumentParser(description="KEPCO SRM Crawler V4")
    parser.add_argument("--keyword", "-k", action="append", default=[])
    parser.add_argument("--days", "-d", type=int, default=30)
    parser.add_argument("--output", "-o", type=str, default="output")
    parser.add_argument("--headed", action="store_true", help="Show browser window")
    
    args = parser.parse_args()
    
    keywords = args.keyword if args.keyword else ["유연탄", "석탄", "연료탄"]
    
    end = datetime.now()
    start = end - timedelta(days=args.days)
    config = SearchConfig(
        keywords=keywords,
        start_date=start.strftime("%Y/%m/%d"),
        end_date=end.strftime("%Y/%m/%d")
    )
    
    logger.info("=" * 50)
    logger.info("KEPCO SRM Crawler V4 (Browser Agent Based)")
    logger.info("=" * 50)
    logger.info(f"Keywords: {keywords}")
    logger.info(f"Date range: {config.start_date} ~ {config.end_date}")
    
    async def _run():
        async with KEPCOCrawler(headless=not args.headed) as crawler:
            results = await crawler.search(config)
            
            logger.info(f"Total results: {len(results)}")
            
            os.makedirs(args.output, exist_ok=True)
            output_file = f"{args.output}/kepco_v4_results.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump([asdict(r) for r in results], f, ensure_ascii=False, indent=2)
            logger.info(f"Saved to: {output_file}")
    
    asyncio.run(_run())


if __name__ == "__main__":
    main()
