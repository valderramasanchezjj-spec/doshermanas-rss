from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

BASE_URL = "https://www.doshermanas.es"
LIST_URL = "https://www.doshermanas.es/noticias/notas-de-prensa/"
FEED_URL = "https://valderramasanchezjj-spec.github.io/doshermanas-rss/rss.xml"

UA = "Mozilla/5.0"
TIMEOUT = 20

def get_article_data(url):
    r = requests.get(url, headers={"User-Agent": UA}, timeout=TIMEOUT)
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.find("h1")
    title = title.get_text(strip=True) if title else "Sin título"

    # Subtítulo o primer párrafo
    subtitle = soup.find("p")
    subtitle = subtitle.get_text(strip=True) if subtitle else ""

    # Imagen principal
    img = soup.find("img")
    img_url = urljoin(BASE_URL, img["src"]) if img and img.get("src") else None

    return title, subtitle, img_url


def main():
    r = requests.get(LIST_URL, headers={"User-Agent": UA}, timeout=TIMEOUT)
    soup = BeautifulSoup(r.text, "html.parser")

    fg = FeedGenerator()
    fg.id(FEED_URL)
    fg.title("Dos Hermanas - Notas de prensa")
    fg.link(href=LIST_URL, rel="alternate")
    fg.link(href=FEED_URL, rel="self")
    fg.language("es")
    fg.description("Feed automático generado desde la web oficial")

    links = soup.select("a[href*='/noticias/']")
    added = set()

    for a in links[:10]:
        url = urljoin(BASE_URL, a["href"])
        if url in added:
            continue
        added.add(url)

        title, subtitle, img_url = get_article_data(url)

        fe = fg.add_entry()
        fe.id(url)
        fe.title(title)
        fe.link(href=url)
        fe.description(subtitle)
        fe.published(datetime.now(timezone.utc))

        if img_url:
            fe.enclosure(img_url, 0, "image/jpeg")

    fg.rss_file("rss.xml")


if __name__ == "__main__":
    main()
