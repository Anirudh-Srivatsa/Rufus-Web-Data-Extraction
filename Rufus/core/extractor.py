from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
import re
from dataclasses import dataclass
import json
from urllib.parse import urlparse

from Rufus.logger import get_logger
from Rufus.exception import ExtractorException
import sys


@dataclass
class ExtractedContent:
    """Data class to store extracted content in a structured format"""
    url: str
    title: str
    main_content: str
    metadata: Dict[str, Any]
    sections: List[Dict[str, str]]
    links: List[str]
    relevance_score: float

class ContentExtractionError(ExtractorException):
    """Raised when content extraction fails"""
    def __init__(self, message: str, error_detail: str):
        super().__init__(message)
        self.error_detail = error_detail
    pass

class ContentCleaningError(ExtractorException):
    """Raised when content cleaning fails"""
    pass

class ContentExtractor:
    def __init__(self):
        self.logger = get_logger(__name__)  # Ensure the logger is initialized

    def extract(self, html_content: str, url: str) -> ExtractedContent:
        try:
            # Ensure that html_content is a string
            if isinstance(html_content, dict):
                html_content = html_content.get('content', '')

            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract title
            title = soup.title.string if soup.title else ''
            title = self._clean_text(title)

            # Extract metadata
            metadata = self._extract_metadata(soup)

            # Extract main content
            main_content = self._extract_main_content(soup)

            # Extract sections
            sections = self._extract_sections(soup)

            # Extract links
            links = [a.get('href') for a in soup.find_all('a', href=True)]

            # Calculate relevance
            relevance_score = self._calculate_relevance(main_content, metadata)

            extracted_content = ExtractedContent(
                url=url,
                title=title,
                main_content=main_content,
                metadata=metadata,
                sections=sections,
                links=links,
                relevance_score=relevance_score
            )

            self.logger.info(f"Successfully extracted content from {url}")
            return extracted_content

        except Exception as e:
            self.logger.error(f"Content extraction failed for {url}: {str(e)}")
            raise ContentExtractionError(f"Failed to extract content from {url}: {str(e)}", str(e))
        """
        Initialize the content extractor.
        
        Args:
            instructions (str, optional): Specific instructions for content extraction
        """
        '''self.logger = rufus_logger
        self.instructions = instructions
        self.important_tags = {
            'article', 'main', 'section', 'div', 'p', 'h1', 'h2', 'h3',
            'table', 'ul', 'ol', 'dl'
        }
        # Common patterns for boilerplate content
        self.boilerplate_patterns = [
            r'cookie[s]?\s*policy',
            r'privacy\s*policy',
            r'terms\s*(?:of\s*)?(?:use|service)',
            r'copyright\s*©?\s*\d{4}',
            r'all\s*rights\s*reserved',
        ]
        self.boilerplate_regex = re.compile('|'.join(self.boilerplate_patterns), re.IGNORECASE)'''

    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing extra whitespace and normalizing content.
        
        Args:
            text (str): Text to clean
            
        Returns:
            str: Cleaned text
        """
        try:
            # Remove extra whitespace
            text = ' '.join(text.split())
            # Remove special characters
            text = re.sub(r'[\r\n\t]+', ' ', text)
            # Normalize quotes
            text = text.replace('"', '"').replace('"', '"')
            # Remove multiple spaces
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        except Exception as e:
            self.logger.error(f"Text cleaning failed: {str(e)}")
            raise ContentCleaningError(f"Failed to clean text: {str(e)}")

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Extract metadata from HTML meta tags.
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            
        Returns:
            Dict[str, str]: Extracted metadata
        """
        metadata = {}
        try:
            # Extract meta tags
            meta_tags = soup.find_all('meta')
            for tag in meta_tags:
                # Get common metadata
                if tag.get('name'):
                    metadata[tag['name']] = tag.get('content', '')
                elif tag.get('property'):
                    metadata[tag['property']] = tag.get('content', '')
                    
            # Extract OpenGraph metadata
            og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
            for tag in og_tags:
                metadata[tag['property']] = tag.get('content', '')
                
            return metadata
        except Exception as e:
            self.logger.warning(f"Metadata extraction partial or failed: {str(e)}")
            return metadata

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """
        Extract main content from HTML while filtering out boilerplate.
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            
        Returns:
            str: Main content
        """
        try:
            # Try to find main content container
            main_content = None
            priority_tags = ['main', 'article', 'div[role="main"]']
            
            for tag in priority_tags:
                main_content = soup.find(tag)
                if main_content:
                    break
            
            if not main_content:
                # Fallback to content heuristics
                main_content = soup.find('div', {'class': re.compile(
                    r'(content|main|article|post|entry)', re.IGNORECASE)})
            
            if not main_content:
                # Last resort: use body
                main_content = soup.find('body')
                
            content_text = main_content.get_text() if main_content else ''
            return self._clean_text(content_text)
            
        except Exception as e:
            self.logger.error(f"Main content extraction failed: {str(e)}")
            raise ContentExtractionError(f"Failed to extract main content: {str(e)}")

    def _extract_sections(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Extract content sections with their headers.
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            
        Returns:
            List[Dict[str, str]]: List of sections with headers and content
        """
        sections = []
        try:
            headers = soup.find_all(['h1', 'h2', 'h3'])
            for header in headers:
                section_content = []
                current = header.find_next_sibling()
                while current and current.name not in ['h1', 'h2', 'h3']:
                    if current.name in self.important_tags:
                        section_content.append(self._clean_text(current.get_text()))
                    current = current.find_next_sibling()
                
                sections.append({
                    'header': self._clean_text(header.get_text()),
                    'content': ' '.join(section_content)
                })
            
            return sections
        except Exception as e:
            self.logger.error(f"Section extraction failed: {str(e)}")
            return []

    def _calculate_relevance(self, content: str, metadata: Dict[str, str]) -> float:
        """
        Calculate content relevance score based on instructions.
        
        Args:
            content (str): Extracted content
            metadata (Dict[str, str]): Content metadata
            
        Returns:
            float: Relevance score between 0 and 1
        """
        if not self.instructions:
            return 1.0
            
        try:
            # Simple relevance scoring based on keyword matching
            # This could be enhanced with more sophisticated NLP techniques
            keywords = self.instructions.lower().split()
            content_lower = content.lower()
            metadata_text = ' '.join(metadata.values()).lower()
            
            # Count keyword occurrences
            content_matches = sum(1 for keyword in keywords if keyword in content_lower)
            metadata_matches = sum(1 for keyword in keywords if keyword in metadata_text)
            
            # Calculate weighted score
            max_score = len(keywords) * 2  # Both content and metadata
            actual_score = content_matches + (metadata_matches * 0.5)
            
            return min(actual_score / max_score, 1.0)
            
        except Exception as e:
            self.logger.warning(f"Relevance calculation failed: {str(e)}")
            return 0.5

    def extract(self, html_content: str, url: str) -> ExtractedContent:
        """
        Extract and structure content from HTML.
        
        Args:
            html_content (str): Raw HTML content
            url (str): Source URL
            
        Returns:
            ExtractedContent: Structured content
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else ''
            title = self._clean_text(title)
            
            # Extract metadata
            metadata = self._extract_metadata(soup)
            
            # Extract main content
            main_content = self._extract_main_content(soup)
            
            # Extract sections
            sections = self._extract_sections(soup)
            
            # Extract links
            links = [a.get('href') for a in soup.find_all('a', href=True)]
            
            # Calculate relevance
            relevance_score = self._calculate_relevance(main_content, metadata)
            
            extracted_content = ExtractedContent(
                url=url,
                title=title,
                main_content=main_content,
                metadata=metadata,
                sections=sections,
                links=links,
                relevance_score=relevance_score
            )
            
            self.logger.info(f"Successfully extracted content from {url}")
            return extracted_content
            
        except Exception as e:
            self.logger.error(f"Content extraction failed for {url}: {str(e)}")
            raise ContentExtractionError(f"Failed to extract content from {url}: {str(e)}")

if __name__ == "__main__":
    # Test the extractor
    test_html = """
    <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test content">
        </head>
        <body>
            <main>
                <h1>Main Header</h1>
                <p>Test paragraph</p>
            </main>
        </body>
    </html>
    """
    
    extractor = ContentExtractor(instructions="test content")
    try:
        result = extractor.extract(test_html, "https://example.com")
        print(json.dumps(result.__dict__, indent=2))
    except ExtractorException as e:
        print(f"Extraction failed: {str(e)}")