from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class NavigationSuggestion:
    url: str
    relevance_score: float
    exploration_priority: float
    rationale: str

class NavigationPlanner:
    def __init__(self, depth_penalty_factor: float = 1.0):
        self.depth_penalty_factor = depth_penalty_factor
    
    async def suggest_paths(
        self,
        current_content: str,
        available_links: List[Dict[str, str]],
        search_goal: str
    ) -> List[NavigationSuggestion]:
        # Implementation from previous RufusAIEngine
        pass