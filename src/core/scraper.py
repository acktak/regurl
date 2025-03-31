import requests
import re
import threading
import queue
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
from src.core.utils import RegexUtils

DEFAULT_REGEX = RegexUtils()

class Scraper:
    """
    A web scraper that searches for regex patterns in web pages, with optional recursive scraping.

    Attributes:
        base_url (str): The base URL to start scraping from.
        regex (str): The regex pattern to search for.
        recursive (bool): Whether to scrape recursively or not.
        result_queue (queue.Queue): Queue to store the scraping results.
        stop_event (threading.Event): Event to signal stopping the scraping process.
        default_regex (list): List of default regex patterns to use.
        match (list): List of matches found during scraping.
    """

    def __init__(self, base_url, regex, recursive=False, result_queue=None, stop_event=None, default_regex=None):
        """
        Initializes the Scraper instance.

        Args:
            base_url (str): The base URL to start scraping from.
            regex (str): The regex pattern to search for.
            recursive (bool, optional): Whether to scrape recursively. Defaults to False.
            result_queue (queue.Queue, optional): Queue to store the scraping results. Defaults to None.
            stop_event (threading.Event, optional): Event to signal stopping the scraping process. Defaults to None.
            default_regex (list, optional): List of default regex patterns to use. Defaults to None.
        """
        self.base_url = base_url
        self.regex = regex
        self.recursive = recursive
        self.result_queue = result_queue or queue.Queue()
        self.match = []
        self.stop_event = stop_event or threading.Event()
        self.default_regex = default_regex if default_regex is not None else []

    def search_regex(self):
        """
        Searches for regex patterns in web pages and stores the results in the queue.
        Handles recursive scraping if enabled.
        """
        url_list = self.extract_urls() if self.recursive else [self.base_url]
        if self.regex in ['Enter a regex...', '']:
            regex_list = []
        else :
            regex_list = [re.compile(self.regex)]
            
        regex_list.extend(self.default_regex)

        if len(regex_list) == 0 : 
            self.result_queue.put({'error': "Please enter a regex or select at least one default."})

        for url in url_list:
            if self.stop_event.is_set():
                logging.info("[INFO] Recherche stoppée.")
                return
            logging.info(f"[INFO] Scraping {url}...")
            page_content = self.fetch_page(url)
            if page_content:
                for regex in regex_list:
                    matches = regex.findall(page_content)
                    for match in matches:
                        if self.stop_event.is_set():
                            logging.info("[INFO] Arrêt en cours...")
                            return
                        result = {'url': url, 'regex': regex.pattern, 'match': match}
                        self.match.append(result)
                        self.result_queue.put(result)

    def fetch_page(self, url):
        """
        Downloads the HTML content of a web page.

        Args:
            url (str): The URL of the web page to fetch.

        Returns:
            str: The HTML content of the page, or None if an error occurs.
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.MissingSchema as e:
            logging.error(f"Erreur lors du téléchargement de {url}: {e}")
            if url == 'Enter an URL...':
                self.result_queue.put({'error': "Please enter an URL."})
            else:
                self.result_queue.put({'error': f"No scheme supplied. Perhaps you meant https://{url}"})
            return None
        except requests.exceptions.HTTPError as errh:
            logging.error(f"Erreur lors du téléchargement de {url}: {errh}")
            self.result_queue.put({'error': f"Http Error: {errh}"})
            return None
        except requests.exceptions.ConnectionError as errc:
            logging.error(f"Erreur lors du téléchargement de {url}: {errc}")
            self.result_queue.put({'error': f"Error Connecting: {errc}"})
            return None
        except requests.exceptions.Timeout as errt:
            logging.error(f"Erreur lors du téléchargement de {url}: {errt}")
            self.result_queue.put({'error': f"Timeout error: {errt}"})
            return None
        except requests.exceptions.RequestException as err:
            logging.error(f"Erreur lors du téléchargement de {url}: {err}")
            self.result_queue.put({'error': f"Unknown error: {err}"})
            return None

    def extract_urls(self):
        """
        Extracts all URLs from the base URL's HTML content.

        Returns:
            list: A list of URLs found on the base page.
        """
        try:
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error fetching base URL {self.base_url}: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        urls = set()

        for link in soup.find_all('a', href=True):
            try:
                url = urljoin(self.base_url, link['href'])
                if url.startswith(self.base_url):
                    urls.add(url)
            except Exception as e:
                logging.warning(f"Failed to process link {link['href']}: {e}")
                continue

        return list(urls)

    def start(self):
        """
        Starts the scraping process in a separate thread.
        """
        thread = threading.Thread(target=self.search_regex)
        thread.start()