from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

BASE_URL = "https://www.doshermanas.es"
LIST_URL = "https://www.doshermanas.es/noticias/notas-de-prensa/"

UA = "Mozilla/5.0 (RSS generator) Python"
TIMEOUT = 20

def pick_items(html: str):
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main") or soup.find("div", {"id": "content"}) or soup.body

    items = []
    seen = set()

    for a in main.find_all("a", href=True):
        title = " ".join(a.get_text(" ", strip=True).split())
        if not title:
            continue

        url = urljoin(BASE_URL, a["href"].strip())

        # Nos quedamos con enlaces que parezcan artículos/noticias
        if "/noticias/" not in url:
            continue

        key = (title, url)
        if key in seen:
            continue
        seen.add(key)
        items.append((title, url))

    return items[:30]

def main():
    r = requests.get(LIST_URL, headers={"User-Agent": UA}, timeout=TIMEOUT)
    r.raise_for_status()

    items = pick_items(r.text)
    if not items:
        raise SystemExit("No se pudieron extraer items. Hay que ajustar selectores.")

    fg = FeedGenerator()
    fg.id(LIST_URL)
    fg.title("Dos Hermanas - Notas de prensa (RSS no oficial)")
    fg.link(href=LIST_URL, rel="alternate")
    fg.link(href=urljoin(BASE_URL, "/rss.xml"), rel="self")
    fg.language("es")
    fg.description("Feed generado automáticamente a partir del listado de notas de prensa.")

    now = datetime.now(timezone.utc)

    for title, url in items:
        fe = fg.add_entry()
        fe.id(url)
        fe.title(title)
        fe.link(href=url)
        fe.published(now)
        fe.updated(now)

    with open("rss.xml", "wb") as f:
        f.write(fg.rss_str(pretty=True))

    print(f"OK: generado rss.xml con {len(items)} items")

if __name__ == "__main__":
    main()
