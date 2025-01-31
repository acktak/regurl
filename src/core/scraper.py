import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class Scraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited = set()

    def scrape(self, url, regex=None):
        """Scrape the provided URL and apply a regex filter if provided."""
        results = []
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Apply regex if provided
            if regex:
                results += regex.findall(response.text)

            # Explore further links
            for link in soup.find_all("a", href=True):
                absolute_url = urljoin(url, link["href"])
                if absolute_url not in self.visited and self.base_url in absolute_url:
                    self.visited.add(absolute_url)
                    results += self.scrape(absolute_url, regex)
        except Exception as e:
            print(f"Error scraping {url}: {e}")
        return results
