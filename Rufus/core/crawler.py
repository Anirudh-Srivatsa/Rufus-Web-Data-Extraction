from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import asyncio
import requests
from typing import Dict, List, Optional
import logging

class WebCrawler:
    def __init__(self, headless: bool = True):
        self.logger = logging.getLogger(__name__)
        self.setup_selenium(headless)
        self.links = []

    def setup_selenium(self, headless: bool):
        """Setup Selenium WebDriver for dynamic content"""
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=options)

    async def crawl(self, url: str) -> Dict:
        """Enhanced crawler with dynamic content support"""
        try:
            # Regular request first for efficiency
            response = await self._make_request(url)
            
            # Check if page might have dynamic content
            if self._might_have_dynamic_content(response):
                content = await self._handle_dynamic_content(url)
            else:
                content = response
            
            # Extract links
            self.links = self._extract_links(content)
            
            # Extract structured data
            structured_data = self._extract_structured_data(content)
            
            return {
                "url": url,
                "content": content,
                "structured_data": structured_data,
                "links": self.links
            }

        except Exception as e:
            self.logger.error(f"Error crawling {url}: {str(e)}")
            raise

    async def _make_request(self, url: str) -> str:
        """Make a regular HTTP request to fetch the page content"""
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Error making request to {url}: {str(e)}")
            raise

    async def _handle_dynamic_content(self, url: str) -> str:
        """Handle JavaScript-rendered content"""
        try:
            # Use Selenium for dynamic content
            self.driver.get(url)
            
            # Wait for dynamic content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(("tag name", "body"))
            )
            
            # Allow for additional rendering time
            await asyncio.sleep(2)
            
            # Get rendered content
            return self.driver.page_source
            
        except Exception as e:
            self.logger.error(f"Error handling dynamic content: {str(e)}")
            raise

    def _extract_links(self, content: str) -> List[str]:
        """Extract links from the page content"""
        soup = BeautifulSoup(content, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', href=True)]
        return links

    def _extract_structured_data(self, content: str) -> Dict:
        """Extract structured data like Schema.org markup"""
        soup = BeautifulSoup(content, 'html.parser')
        structured_data = {
            "schema_org": self._extract_schema_org(soup),
            "meta_tags": self._extract_meta_tags(soup),
            "open_graph": self._extract_open_graph(soup)
        }
        return structured_data

    def _extract_schema_org(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract Schema.org structured data"""
        schema_data = {}
        schema_tags = soup.find_all('script', type='application/ld+json')
        for tag in schema_tags:
            try:
                data = json.loads(tag.string)
                if isinstance(data, list):
                    schema_data.update({item.get('@type'): item for item in data})
                else:
                    schema_data[data.get('@type')] = data
            except Exception as e:
                self.logger.error(f"Error parsing schema data: {str(e)}")
        return schema_data

    def _extract_meta_tags(self, soup: BeautifulSoup) -> Dict:
        """Extract meta tags from the page"""
        meta_tags = {}
        for tag in soup.find_all('meta'):
            name = tag.get('name')
            property_name = tag.get('property')
            content = tag.get('content')
            if name:
                meta_tags[name] = content
            elif property_name:
                meta_tags[property_name] = content
        return meta_tags

    def _extract_open_graph(self, soup: BeautifulSoup) -> Dict:
        """Extract Open Graph metadata"""
        og_data = {}
        for tag in soup.find_all('meta'):
            if tag.get('property', '').startswith('og:'):
                og_data[tag.get('property')] = tag.get('content')
        return og_data

    def _might_have_dynamic_content(self, content: str) -> bool:
        """Basic heuristic to determine if a page might have dynamic content"""
        return '<script' in content.lower()  # Adjust logic as needed
