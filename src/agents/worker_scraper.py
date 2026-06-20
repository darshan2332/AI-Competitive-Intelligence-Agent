from src.tools.scraper_tool import ScraperTool
from src.utils.logger import logger

class WorkerScraper:
    def __init__(self):
        self.scraper = ScraperTool()

    def scrape_competitor(self, pricing_url: str, features_url: str) -> dict:
        """
        Scrapes both pricing and features pages, returning raw cleaned text.
        """
        logger.info(f"Starting scrape for pricing: {pricing_url} and features: {features_url}")
        
        pricing_raw = ""
        features_raw = ""

        try:
            pricing_raw = self.scraper.fetch_page_markdown(pricing_url)
        except Exception as e:
            logger.error(f"Error scraping pricing page {pricing_url}: {e}")

        try:
            features_raw = self.scraper.fetch_page_markdown(features_url)
        except Exception as e:
            logger.error(f"Error scraping features page {features_url}: {e}")

        return {
            "pricing_raw": pricing_raw,
            "features_raw": features_raw
        }
