import unittest
from src.core.scraper import Scraper

class TestScraper(unittest.TestCase):
    def test_scrape_valid_url(self):
        scraper = Scraper("http://example.com")
        results = scraper.scrape("http://example.com")
        self.assertIsInstance(results, list)
