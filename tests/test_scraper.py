import unittest
from unittest.mock import patch, MagicMock
from src.core.scraper import Scraper
import queue
import threading

class TestScraper(unittest.TestCase):

    @patch('src.core.scraper.requests.get')
    def test_fetch_page_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test Page</body></html>"
        mock_get.return_value = mock_response

        scraper = Scraper(base_url="http://example.com", regex=None)
        result = scraper.fetch_page("http://example.com")
        self.assertEqual(result, "<html><body>Test Page</body></html>")

    @patch('src.core.scraper.requests.get')
    def test_fetch_page_http_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.HTTPError("HTTP Error")
        result_queue = queue.Queue()
        scraper = Scraper(base_url="http://example.com", regex=None, result_queue=result_queue)
        result = scraper.fetch_page("http://example.com")
        self.assertIsNone(result)
        self.assertFalse(result_queue.empty())
        self.assertIn("Http Error", result_queue.get()['error'])

    @patch('src.core.scraper.requests.get')
    def test_fetch_page_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection Error")
        result_queue = queue.Queue()
        scraper = Scraper(base_url="http://example.com", regex=None, result_queue=result_queue)
        result = scraper.fetch_page("http://example.com")
        self.assertIsNone(result)
        self.assertFalse(result_queue.empty())
        self.assertIn("Error Connecting", result_queue.get()['error'])

    @patch('src.core.scraper.requests.get')
    def test_extract_urls(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <body>
                <a href="/page1">Page 1</a>
                <a href="/page2">Page 2</a>
            </body>
        </html>
        """
        mock_get.return_value = mock_response

        scraper = Scraper(base_url="http://example.com", regex=None)
        urls = scraper.extract_urls()
        self.assertIn("http://example.com/page1", urls)
        self.assertIn("http://example.com/page2", urls)

    @patch('src.core.scraper.requests.get')
    def test_search_regex(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Test 123 Test 456"
        mock_get.return_value = mock_response

        result_queue = queue.Queue()
        scraper = Scraper(base_url="http://example.com", regex=r"Test \d+", result_queue=result_queue)
        scraper.search_regex()

        results = []
        while not result_queue.empty():
            results.append(result_queue.get())

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['match'], "Test 123")
        self.assertEqual(results[1]['match'], "Test 456")

    def test_stop_event(self):
        stop_event = threading.Event()
        result_queue = queue.Queue()
        scraper = Scraper(base_url="http://example.com", regex=r"Test \d+", result_queue=result_queue, stop_event=stop_event)

        stop_event.set()
        scraper.search_regex()

        self.assertTrue(result_queue.empty())

if __name__ == '__main__':
    unittest.main()