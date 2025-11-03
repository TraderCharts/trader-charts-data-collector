# config.py
"""
Configuration file for the Selenium CSV Downloader project.
Recommended structure for Python scripts, libraries, and microservices.
"""

__version__ = "4.3.1"

import os

# === General settings ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directory where CSVs will be downloaded
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", os.path.join(BASE_DIR, "downloads"))

# === Selenium settings ===
SELENIUM_TIMEOUT = int(os.getenv("SELENIUM_TIMEOUT", 20))
CHROME_WINDOW_SIZE = os.getenv("CHROME_WINDOW_SIZE", "1920,1080")
SELENIUM_HEADLESS = os.getenv("SELENIUM_HEADLESS", "True").lower() == "true"

# === MongoDB settings (sensitive information) ===
# Must be set in the environment or in .env.local; do not hardcode
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
BYMA_COLLECTION = os.getenv("BYMA_COLLECTION")
RSS_COLLECTION = os.getenv("RSS_COLLECTION")

# URLs / Feeds
HISTORICAL_URLS = [
    ("https://www.rava.com/perfil/DOLAR%20MEP", "Dolar MEP"),
    # add more URLs here
]

# using https://createfeed.fivefilters.org/?mode=feedcontrol
RSS_FEEDS = [
    {"sourceId": 1, "name": "clarin economia", "url": "https://www.clarin.com/rss/economia/"},
    {
        "sourceId": 2,
        "name": "lanacion economia",
        "url": "https://rss.app/feeds/1kL74AxcMUCjYsko.xml",
    },
    {
        "sourceId": 3,
        "name": "pagina12 economia",
        "url": "https://www.pagina12.com.ar/rss/secciones/economia/notas",
    },
    {
        "sourceId": 4,
        "name": "infobae economia",
        "url": "https://cdn.feedcontrol.net/13080/23180-IAH203wJ81I2f.xml",
    },
    # {"sourceId": 5,  "name": "ambito economia", "url": "https://api.rss2json.com/v1/api.json?rss_url=https://www.ambito.com/rss/pages/economia.xml"},
    # {"sourceId": 6,  "name": "ambito finanzas", "url": "https://api.rss2json.com/v1/api.json?rss_url=https://www.ambito.com/rss/pages/finanzas.xml"},
    # {"sourceId": 7,  "name": "perfil economia", "url": "https://www.perfil.com/feed/economia"},
    # {"sourceId": 8,  "name": "eleconomista economia", "url": "https://eleconomista.com.ar/economia/feed/"},
    {
        "sourceId": 9,
        "name": "eleconomista finanzas",
        "url": "https://eleconomista.com.ar/finanzas/feed/",
    },
    # {"sourceId": 10,  "name": "eleconomista negocios", "url": "https://eleconomista.com.ar/negocios/feed/"},
    {
        "sourceId": 11,
        "name": "laizquierdadiario",
        "url": "https://www.laizquierdadiario.com/spip.php?page=backend&id_mot=13",
    },
    # add more feeds here
]

FEEDS_UPDATE_HOURS = 6
