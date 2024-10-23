# Example test_crawler.py
import pytest
from Rufus.core.crawler import WebCrawler


async def test_crawler_basic():
    crawler = WebCrawler()
    url = "https://example.com"
    result = await crawler.crawl(url)
    assert result is not None
    

'''def test_crawler_dynamic():
    crawler = WebCrawler()
    url = "https://dynamic-site.com"
    result = await crawler.crawl(url)
    assert result["dynamic_content"] is not None'''