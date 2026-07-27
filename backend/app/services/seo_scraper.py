import time
import re
import httpx
from bs4 import BeautifulSoup


async def fetch_and_parse(url: str) -> dict:
    """Fetch a URL and extract basic on-page SEO signals."""
    headers = {"User-Agent": "SEO-GEO-Dashboard-Bot/1.0 (+https://github.com/)"}
    async with httpx.AsyncClient(timeout=15, follow_redirects=True, headers=headers) as client:
        start = time.time()
        resp = await client.get(url)
        load_time = round(time.time() - start, 3)
        resp.raise_for_status()
        html = resp.text

    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("title")
    title_text = title_tag.text.strip() if title_tag else None

    meta_desc = soup.find("meta", attrs={"name": "description"})
    meta_desc_text = meta_desc.get("content", "").strip() if meta_desc else None

    h1_tag = soup.find("h1")
    h1_text = h1_tag.text.strip() if h1_tag else None

    h2_tags = soup.find_all("h2")
    h2_list = [h.get_text(strip=True) for h in h2_tags[:10] if h.get_text(strip=True)]

    text_content = soup.get_text(" ", strip=True)
    word_count = len(re.findall(r"\w+", text_content))

    images = soup.find_all("img")
    images_count = len(images)

    links = soup.find_all("a")
    links_count = len(links)

    return {
        "html": html,
        "title": title_text,
        "meta_description": meta_desc_text,
        "h1": h1_text,
        "h2": h2_list,
        "word_count": word_count,
        "images_count": images_count,
        "links_count": links_count,
        "load_time": load_time,
    }
