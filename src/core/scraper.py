import requests
import re
import threading
import queue
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

class Scraper:
    def __init__(self, base_url, regex, recursive=False, default_regex=False, result_queue=None, stop_event=None):
        self.base_url = base_url
        self.regex = regex
        self.recursive = recursive
        self.default_regex = default_regex  
        self.result_queue = result_queue or queue.Queue()  # File pour stocker les résultats
        self.match = []
        self.stop_event = stop_event

    def search_regex(self):
        """Recherche les regex en mode récursif ou non et met les résultats dans la queue"""
        url_list = self.extract_urls() if self.recursive else [self.base_url]

        regex_list = [self.regex] if self.regex else []
        if self.default_regex:
            regex_list += ["\\d{3}-\\d{3}-\\d{4}", "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"]  # Ex: téléphone et email

        for url in url_list:

            if self.stop_event.is_set():  # Vérifier si Stop est activé
                logging.info("[INFO] Recherche stoppée.")
                return
            logging.info(f"[INFO] Scraping {url}...")
            page_content = self.fetch_page(url)
            if page_content:
                for regex in regex_list:
                    matches = re.findall(regex, page_content)
                    for match in matches:
                        if self.stop_event.is_set():  # Vérifier STOP à chaque boucle
                            logging.info("[INFO] Arrêt en cours...")
                            return
                        result = {'url': url, 'regex': regex, 'match':match}
                        self.match.append(result)
                        self.result_queue.put(result)  # Envoie le résultat à la GUI

    def fetch_page(self, url):
        """Télécharge la page HTML"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logging.error(f"Erreur lors du téléchargement de {url}: {e}")
            # Envoyer l'erreur dans la queue pour l'afficher dans l'interface
            self.result_queue.put({'error': f"Invalid URL : {url}"})
            return None
            return None

    def extract_urls(self):
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            urls = set()
            for link in soup.find_all('a', href=True):
                url = urljoin(self.base_url, link['href'])
                if re.match(self.base_url,url):
                    urls.add(url)
            return list(urls)
        except requests.RequestException as e:
            logging.error(f"Error fetching {self.base_url}: {e}")
            return set()

    def start(self):
        """Lance la recherche dans un thread séparé"""
        thread = threading.Thread(target=self.search_regex)
        thread.start()
        
    def stop(self):
        self.stop =True