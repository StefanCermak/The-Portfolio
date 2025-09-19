import feedparser
import requests
import re
from bs4 import BeautifulSoup

import tools

RSS_FEEDS_TICKERS = [
    "https://www.wallstreet-online.de/rss/nachrichten-aktien-indizes.xml",
    "https://www.finanzen.net/rss/news",
    "https://www.wiwo.de/contentexport/feed/rss/schlagzeilen",
    "https://www.ad-hoc-news.de/rss/nachrichten.xml",
    "https://www.onvista.de/news/feed/rss.xml?orderBy=datetime&newsType%5B0%5D=marketreport&supplier%5B0%5D=dpa-AFX&tags%5B0%5D=Deutschland&",
    "https://api.boerse-frankfurt.de/v1/feeds/news.rss",
    "https://www.aktiencheck.de/rss/news.rss2",
    "https://www.aktiennews24.de/thema/news/feed/",
    "https://www.wallstreet-online.de/rss/board-dax.xml",
    "https://www.deraktionaer.de/aktionaer-news.rss",
    "https://www.derstandard.at/rss/wirtschaft",
    "https://www.diepresse.com/rss/",
    "https://www.tagesschau.de/infoservices/alle-meldungen-100~rss2.xml",
    "https://www.tagesschau.de/wirtschaft/index~rss2.xml",
    "https://rss.orf.at/news.xml"
    ]

HTML_CLEARNER_RE = re.compile('<.*?>')
MULTILINE_MULTI_SPACE_RE = re.compile(r'\s+')
LINK_CLEARNER_RE = re.compile(r'http\S+')
EMAIL_CLEARNER_RE = re.compile(r'\S+@\S+')
GET_SERVER_RE = re.compile(r'https://(.*?)/')


@tools.persistent_timed_cache("fetch_full_article.json", ttl_seconds=3600*24)  # 1 hour cache
def fetch_full_article(url: str) -> str | None:
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


class RssEntry:
    def __init__(self, title: str, link: str, summary: str):
        self.title = title
        self.summary = summary
        self.link = link
        self.article = None

        self.clean_summary()
        self.fetch_full_article()

    @property
    def server(self) -> str:
        match = re.match(GET_SERVER_RE, self.link)
        return match.group(1) if match else "unknown"

    def clean_summary(self) -> None:
        # Remove HTML tags from summary
        cleantext = self.summary.replace("&nbsp;", " ")
        cleantext = re.sub(HTML_CLEARNER_RE, '', cleantext)
        cleantext = re.sub(MULTILINE_MULTI_SPACE_RE, ' ', cleantext).strip()
        self.summary = cleantext

    def fetch_full_article(self) -> None:
        self.article = fetch_full_article(self.link)


class RssCrawler:
    def __init__(self, rss_feeds: list[str] = None):
        if rss_feeds is None:
            rss_feeds = RSS_FEEDS_TICKERS
        self.rss_feeds = rss_feeds
        self.rss_entries: list[RssEntry] = []
        self.rss_filters: list[str] = []
        self.crawl_rss_feeds()

    def crawl_rss_feeds(self):
        for rss_feed in self.rss_feeds:
            self.fetch_rss_feed(rss_feed)

    def fetch_rss_feed(self, rss_url: str) -> None:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
        response = requests.get(rss_url, headers=headers)
        feed = feedparser.parse(response.content)
        for feed_entry in feed.entries:
            title = feed_entry.get('title', '')
            summary = feed_entry.get('summary', '')
            link = feed_entry.get('link', '')
            new_feed_entry = RssEntry(title, link, summary)
            self.rss_entries.append(new_feed_entry)

    def __iter__(self):
        for entry in self.rss_entries:
            if not self.rss_filters:
                yield entry
            else:
                filter_collection = (entry.title + " " + \
                                     entry.summary if entry.summary else "" + " " + \
                                     entry.article if entry.article else ""
                                     ).lower()
                if any(f.lower() in filter_collection for f in self.rss_filters):
                    yield entry


if __name__ == "__main__":
    crawler = RssCrawler()
    crawler.rss_filters = ["AAPL", "Apple"]
    for entry in crawler:
        print(entry.title)
        print(entry.link)
        if entry.article:
            print(tools.wrap_text_with_preferred_breaks(entry.article, 80))
        else:
            print(tools.wrap_text_with_preferred_breaks(entry.summary,
                                                        80) if entry.summary else "No article/summary available.")
        print("-----")
