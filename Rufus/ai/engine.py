from typing import List, Dict, Optional, Union
import logging
from langchain.prompts import PromptTemplate
from langchain.llms import BaseLLM
from bs4 import BeautifulSoup
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from dataclasses import dataclass

@dataclass
class ContentScore:
    relevance_score: float
    topic_match: float
    information_density: float
    url: str
    summary: str

class RufusAIEngine:
    """
    AI engine for Rufus that handles LLM prompting, content analysis,
    and intelligent navigation decisions.
    """
    def __init__(
        self,
        llm: BaseLLM,  # Non-default parameter first
        api_key: Optional[str] = None,  # Default parameter second
        relevance_threshold: float = 0.7,
        max_tokens: int = 1000
    ):
        self.llm = llm
        self.api_key = api_key
        self.relevance_threshold = relevance_threshold
        self.max_tokens = max_tokens
        self.logger = logging.getLogger(__name__)
        
        # Initialize prompts
        self.analysis_prompt = PromptTemplate(
            input_variables=["content", "query"],
            template="""
            Analyze the following web content in relation to the search query.
            
            Content: {content}
            Query: {query}
            
            Provide an analysis covering:
            1. Relevance to query (0-1 scale)
            2. Key information points
            3. Suggested next search directions
            4. Content quality assessment
            
            Format your response as JSON.
            """
        )
        
        self.navigation_prompt = PromptTemplate(
            input_variables=["current_page", "links", "search_goal"],
            template="""
            Given the current page content and available links, determine the most promising
            navigation paths to achieve the search goal.
            
            Current Page Summary: {current_page}
            Available Links: {links}
            Search Goal: {search_goal}
            
            Rank the top 3 most relevant links and explain why they should be explored next.
            Format your response as JSON.
            """
        )

    async def analyze_content_relevance(
        self,
        content: str,
        query: str,
        url: str
    ) -> ContentScore:
        """
        Analyzes content relevance using both ML and LLM approaches.
        """
        try:
            # TF-IDF based relevance scoring
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([content, query])
            cosine_similarities = (tfidf_matrix * tfidf_matrix.T).A
            ml_relevance_score = cosine_similarities[0, 1]
            
            # LLM-based analysis
            prompt = self.analysis_prompt.format(content=content[:self.max_tokens], query=query)
            llm_response = await self.llm.agenerate([prompt])
            analysis = llm_response.generations[0].text
            
            # Calculate composite score
            information_density = len(set(content.split())) / len(content.split())
            topic_match = self._calculate_topic_match(content, query)
            
            return ContentScore(
                relevance_score=(ml_relevance_score + float(analysis['relevance'])) / 2,
                topic_match=topic_match,
                information_density=information_density,
                url=url,
                summary=analysis['key_information']
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing content relevance: {str(e)}")
            raise

    async def suggest_navigation_paths(
        self,
        current_content: str,
        available_links: List[Dict[str, str]],
        search_goal: str
    ) -> List[Dict[str, Union[str, float]]]:
        """
        Uses LLM to suggest the most promising navigation paths.
        """
        try:
            current_summary = self._summarize_content(current_content)
            prompt = self.navigation_prompt.format(
                current_page=current_summary,
                links=str(available_links),
                search_goal=search_goal
            )
            
            response = await self.llm.agenerate([prompt])
            suggestions = response.generations[0].text
            
            # Process and score suggestions
            scored_links = []
            for link in available_links:
                relevance = self._estimate_link_relevance(
                    link['text'],
                    link['url'],
                    search_goal
                )
                scored_links.append({
                    'url': link['url'],
                    'text': link['text'],
                    'relevance_score': relevance,
                    'exploration_priority': self._calculate_exploration_priority(
                        relevance,
                        link['depth']
                    )
                })
            
            return sorted(
                scored_links,
                key=lambda x: x['exploration_priority'],
                reverse=True
            )
            
        except Exception as e:
            self.logger.error(f"Error suggesting navigation paths: {str(e)}")
            raise

    def _summarize_content(self, content: str) -> str:
        """
        Creates a brief summary of the content for navigation decisions.
        """
        soup = BeautifulSoup(content, 'html.parser')
        main_content = ' '.join(soup.stripped_strings)
        return main_content[:500]  # Return first 500 chars as summary

    def _estimate_link_relevance(
        self,
        link_text: str,
        url: str,
        search_goal: str
    ) -> float:
        """
        Estimates the potential relevance of a link based on its text and URL.
        """
        # Simple TF-IDF based relevance scoring
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([f"{link_text} {url}", search_goal])
        cosine_similarities = (tfidf_matrix * tfidf_matrix.T).A
        return float(cosine_similarities[0, 1])

    def _calculate_exploration_priority(
        self,
        relevance: float,
        depth: int
    ) -> float:
        """
        Calculates exploration priority based on relevance and depth.
        """
        depth_penalty = 1 / (1 + depth)
        return relevance * depth_penalty

    def _calculate_topic_match(self, content: str, query: str) -> float:
        """
        Calculates how well the content matches the query topic.
        """
        # Create TF-IDF vectors for content and query
        vectorizer = TfidfVectorizer(stop_words='english')
        vectors = vectorizer.fit_transform([content, query])
        return float((vectors * vectors.T).A[0, 1])