from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
import re

import tools

STATIC_RESULTS = ['wikipedia.org', 'de.wikipedia.org', 'en.wikipedia.org']
STATIC_DOMAINS = '-site:' + ' -site:'.join(STATIC_RESULTS)

MULTILINE_MULTI_SPACE_RE = re.compile(r'\s+')
LINK_CLEARNER_RE = re.compile(r'http\S+')
EMAIL_CLEARNER_RE = re.compile(r'\S+@\S+')


@tools.persistent_timed_cache("fetch_full_webside.json", ttl_seconds=3600 * 24)  # 1 hour cache
def fetch_full_website(url: str) -> str | None:
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        article_text = ' '.join(p.get_text() for p in paragraphs)
        article_text = re.sub(MULTILINE_MULTI_SPACE_RE, ' ', article_text).strip()
        article_text = re.sub(LINK_CLEARNER_RE, '', article_text).strip()
        article_text = re.sub(EMAIL_CLEARNER_RE, '', article_text).strip()
        return article_text if article_text else None
    except requests.RequestException as e:
        print(f"Error fetching article from {url}: {e}")
        return None


def get_duckduckgo_result(company_name, count=5, fetch_full_article=1):
    with DDGS() as ddgs:
        results = ddgs.text(f"{company_name} News {STATIC_DOMAINS}", max_results=count)
        if results:
            return [(r.get('title'), fetch_full_website(r.get('href')) if idx < fetch_full_article else r.get('body'))
                    for idx, r in enumerate(results[:count]) if 'body' in r]
    return []


def WWW_Crawler(company_name, count=5, fetch_full_article=1):
    return get_duckduckgo_result(company_name, count, fetch_full_article)


if __name__ == "__main__":
    results = WWW_Crawler("Xpeng", 5, 1)
    for title, info in results:
        print(f"Title: {title}\nInfo: {info}\n")
