from dataclasses import dataclass
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer

@dataclass
class ContentScore:
    relevance_score: float
    topic_match: float
    information_density: float
    url: str
    summary: str

class ContentAnalyzer:
    def __init__(self, vectorizer=None):
        self.vectorizer = vectorizer or TfidfVectorizer(stop_words='english')
    
    def analyze(self, content: str, query: str) -> ContentScore:
        # Implementation from previous RufusAIEngine
        pass