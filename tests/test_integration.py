import pytest
from Rufus.client import RufusClient
from Rufus.ai.llm import SimpleLLM

@pytest.mark.asyncio
async def test_full_functionality():
    api_key = "your-test-api-key"
    test_url = "https://jsonplaceholder.typicode.com/posts" # Use a valid URL for testing
    instructions = "Find information about HR policies and procedures"
    llm_instance = SimpleLLM(api_key="your-llm-key")  # Replace with your LLM initialization
    client = RufusClient(api_key=api_key, llm=llm_instance)
    
    documents = await client.scrape(
        url=test_url,
        instructions=instructions,
        max_pages=10,
        min_relevance=0.7
    )

    # Assertions to check if the output is as expected
    assert isinstance(documents, list)
    assert len(documents) > 0  # Check that documents are returned
    assert all('url' in doc for doc in documents)  # Check if each document has a URL