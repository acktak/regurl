# Documentation

## Introduction
Cette application est un projet Python pour extraire des informations d'une page web correspondant à une expression régulière donnée.

## Structure du projet
Voici la structure du projet :
.
├── docs/
│   └── doc.md
├── src/
│   ├── core/
│   │   ├── scraper.py
│   │   └── regex_utils.py
│   └── gui/
│       └── app.py
├── tests/
│   └── test_scraper.py
├── main.py
├── README.md
└── requirements.txt


## Modules

### `src/core/scraper.py`
Ce module contient la classe [`Scraper`](../src/core/scraper.py) qui permet de récupérer toutes les pages d'un site web et d'appliquer un filtre regex si fourni.

#### Classe `Scraper`
- `__init__(self, base_url)`: Initialise le scraper avec une URL de base.
- `scrape(self, url, regex=None)`: Récupère le contenu de l'URL fournie et applique un filtre regex si fourni.

### `src/core/regex_utils.py`
Ce module contient la classe [`RegexUtils`](../src/core/regex_utils.py) qui fournit des expressions régulières prédéfinies et une méthode pour récupérer une expression régulière par nom.

#### Classe `RegexUtils`
- `PREDEFINED_PATTERNS`: Dictionnaire contenant des expressions régulières prédéfinies.
- `get_pattern(name)`: Méthode statique pour récupérer une expression régulière par nom.

### `src/gui/app.py`
Ce module contient la classe [`TkinterApp`](../src/gui/app.py) qui crée une interface graphique pour interagir avec le scraper et les expressions régulières.

#### Classe `TkinterApp`
- `__init__(self, root)`: Initialise l'application Tkinter.
- `create_widgets(self)`: Crée les widgets de l'interface utilisateur.
- `analyze(self)`: Analyse l'URL fournie et applique l'expression régulière.
- `export_csv(self)`: Exporte les résultats de l'analyse dans un fichier CSV.

## Tests
Les tests unitaires sont définis dans le fichier [`tests/test_scrapper.py`](../tests/test_scrapper.py).

### `tests/test_scrapper.py`
Ce fichier contient des tests pour la classe [`Scraper`](../src/core/scraper.py).

#### Classe `TestScraper`
- `test_scrape_valid_url(self)`: Teste la méthode `scrape` avec une URL valide.


## Configuration de l'environnement virtuel
Pour créer et activer un environnement virtuel, suivez les étapes ci-dessous :

1. Créez un environnement virtuel :
    ```sh
    python -m venv venv
    ```

2. Activez l'environnement virtuel :
    - Sur Windows :
        ```sh
        .\venv\Scripts\activate
        ```
    - Sur macOS et Linux :
        ```sh
        source venv/bin/activate
        ```

3. Installez les dépendances :
    ```sh
    pip install -r requirements.txt
    ```

4. Lancez l'application :
    ```sh
    python main.py
    ```

5. Pour désactiver l'environnement virtuel :
    ```sh
    deactivate
    ```
