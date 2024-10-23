from typing import List, Dict, Union
import json
import markdown
from datetime import datetime
from pathlib import Path
import logging

class DocumentSynthesizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def synthesize(
        self,
        results: List[Dict],
        format: str = "json"
    ) -> Union[List[Dict], str]:
        """
        Synthesize crawled content into structured documents
        
        Args:
            results: List of search results
            format: Output format ("json", "markdown", "text")
            
        Returns:
            Structured documents in specified format
        """
        try:
            # Deduplicate and merge related content
            processed_results = self._process_results(results)
            
            # Structure the documents
            documents = self._structure_documents(processed_results)
            
            # Format according to specification
            if format.lower() == "json":
                return self._format_json(documents)
            elif format.lower() == "markdown":
                return self._format_markdown(documents)
            elif format.lower() == "text":
                return self._format_text(documents)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            self.logger.error(f"Error synthesizing documents: {str(e)}")
            raise
            
    def _process_results(self, results: List[Dict]) -> List[Dict]:
        """Process and deduplicate results"""
        seen_content = set()
        processed_results = []
        
        for result in results:
            # Create content fingerprint
            content_hash = hash(result["content"])
            
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                processed_results.append(result)
                
        return processed_results
        
    def _structure_documents(self, results: List[Dict]) -> List[Dict]:
        """Structure documents for RAG consumption"""
        documents = []
        
        for result in results:
            doc = {
                "url": result["url"],
                "timestamp": datetime.now().isoformat(),
                "content": result["content"],
                "metadata": {
                    "relevance_score": result.get("relevance_score", 0),
                    "source": "web",
                    "extracted_data": result.get("structured_data", {}),
                    "crawler_metadata": {
                        "depth": result.get("depth", 0),
                        "parent_url": result.get("parent_url", "")
                    }
                }
            }
            documents.append(doc)
            
        return documents
        
    def save(self, documents: Union[List[Dict], str], output_file: Path):
        """Save synthesized documents to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                if isinstance(documents, list):
                    json.dump(documents, f, indent=2, ensure_ascii=False)
                else:
                    f.write(documents)  
                    
            self.logger.info(f"Saved documents to {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving documents: {str(e)}")
            raise
