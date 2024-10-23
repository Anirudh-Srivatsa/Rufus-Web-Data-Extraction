# rufus/client.py

import asyncio
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .core.crawler import WebCrawler
from .core.extractor import ContentExtractor
from .core.synthesizer import DocumentSynthesizer
from .ai.engine import RufusAIEngine
from Rufus.logger import get_logger
from .config.default import AI_CONFIG
from Rufus.ai.llm import SimpleLLM

@dataclass
class SearchResult:
    """Container for search results"""
    url: str
    content: str
    relevance_score: float
    metadata: Dict
    timestamp: datetime

class RufusClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[Dict] = None,
        output_dir: Optional[str] = None,
        llm: Optional[SimpleLLM] = None  # Accept llm as an argument
    ):
        self.api_key = api_key
        self.config = config or AI_CONFIG
        self.output_dir = Path(output_dir) if output_dir else Path("./output")
        self.output_dir.mkdir(exist_ok=True)

        # Initialize components
        self.logger = get_logger(__name__)
        self.crawler = WebCrawler()
        self.extractor = ContentExtractor()
        self.synthesizer = DocumentSynthesizer()
        
        valid_params = {
            "api_key": api_key,
            "relevance_threshold": self.config.get("relevance_threshold", 0.7),
            "llm": llm  # Pass the llm argument here
        }
        
        self.ai_engine = RufusAIEngine(**valid_params)
        
        
    async def scrape(
        self,
        url: str,
        instructions: str,
        max_pages: int = 100,
        min_relevance: float = 0.7,
        output_format: str = "json"
    ) -> List[Dict]:
        """
        Main method to scrape and analyze web content based on instructions.
        
        Args:
            url: Starting URL to crawl
            instructions: Natural language instructions for the search
            max_pages: Maximum number of pages to crawl
            min_relevance: Minimum relevance score (0-1) for including content
            output_format: Format for output documents ("json", "text", "markdown")
            
        Returns:
            List of documents matching the search criteria
        """
        self.logger.info(f"Starting search with instructions: {instructions}")
        results = []
        visited_urls = set()
        urls_to_visit = [url]
        
        try:
            while urls_to_visit and len(visited_urls) < max_pages:
                current_url = urls_to_visit.pop(0)
                
                if current_url in visited_urls:
                    continue
                    
                # Crawl page
                self.logger.debug(f"Crawling: {current_url}")
                page_content = await self.crawler.crawl(current_url)
                visited_urls.add(current_url)
                
                # Extract content
                extracted_content = self.extractor.extract(page_content, current_url)
                
                # Analyze relevance
                content_score = await self.ai_engine.analyze_content_relevance(
                    extracted_content,
                    instructions,
                    current_url
                )
                
                # Store relevant content
                if content_score.relevance_score >= min_relevance:
                    results.append(SearchResult(
                        url=current_url,
                        content=extracted_content,
                        relevance_score=content_score.relevance_score,
                        metadata={
                            "topic_match": content_score.topic_match,
                            "information_density": content_score.information_density
                        },
                        timestamp=datetime.now()
                    ))
                    
                    # Get navigation suggestions
                    next_pages = await self.ai_engine.suggest_navigation_paths(
                        extracted_content,
                        self.crawler.get_links(),
                        instructions
                    )
                    
                    # Add promising URLs to queue
                    for page in next_pages:
                        if (page["url"] not in visited_urls and 
                            page["relevance_score"] > min_relevance):
                            urls_to_visit.append(page["url"])
                
            # Synthesize results
            documents = self.synthesizer.synthesize(
                results,
                format=output_format
            )
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"rufus_results_{timestamp}.{output_format}"
            self.synthesizer.save(documents, output_file)
            
            self.logger.info(
                f"Search complete. Found {len(documents)} relevant documents. "
                f"Saved to {output_file}"
            )
            
            return documents
            
        except Exception as e:
            self.logger.error(f"Error during scraping: {str(e)}")
            raise


    async def scrape_multiple(
        self,
        urls: List[str],
        instructions: str,
        **kwargs
    ) -> List[Dict]:
        """
        Scrape multiple URLs in parallel.
        """
        tasks = [
            self.scrape(url, instructions, **kwargs)
            for url in urls
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out errors and flatten results
        documents = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Error in parallel scraping: {str(result)}")
            else:
                documents.extend(result)
                
        return documents
    
    def scan(
        self,
        url: str,
        instructions: str,
        **kwargs
    ) -> List[Dict]:
        """
        Synchronous version of scrape() for easier usage.
        """
        return asyncio.run(self.scrape(url, instructions, **kwargs))
    
    def scan_multiple(
        self,
        urls: List[str],
        instructions: str,
        **kwargs
    ) -> List[Dict]:
        """
        Synchronous version of scrape_multiple() for easier usage.
        """
        return asyncio.run(self.scrape_multiple(urls, instructions, **kwargs))

# Example usage
if __name__ == "__main__":
    async def main():
        # Initialize client
        client = RufusClient(api_key="your-key-here")
        
        # Single URL example
        documents = await client.scrape(
            "https://www.sfgov.com",
            instructions="Find information about HR policies and procedures",
            max_pages=50,
            min_relevance=0.8
        )
        
        # Multiple URLs example
        urls = [
            "https://www.sfgov.com/hr",
            "https://www.sfgov.com/jobs"
        ]
        
        documents = await client.scrape_multiple(
            urls,
            instructions="Gather information about job postings and requirements"
        )
        
    asyncio.run(main())