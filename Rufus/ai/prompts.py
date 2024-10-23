from langchain.prompts import PromptTemplate

ANALYSIS_PROMPT = PromptTemplate(
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

NAVIGATION_PROMPT = PromptTemplate(
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