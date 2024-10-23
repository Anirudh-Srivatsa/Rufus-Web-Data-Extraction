import pytest
import requests
from Rufus.client import RufusClient
from Rufus.ai.llm import SimpleLLM

@pytest.fixture
def client():
    """Create a RufusClient instance for testing."""
    llm_instance = SimpleLLM(api_key="your-llm-key")  # Create a valid LLM instance
    return RufusClient(api_key="your-test-key", llm=llm_instance)  # Pass llm instance

def test_scrape_json_placeholder(client):
    """Test scraping posts from JSONPlaceholder."""
    instructions = "Scrape data from JSON placeholder at https://jsonplaceholder.typicode.com/posts" 
    url = "https://jsonplaceholder.typicode.com/posts"
    
    # Assuming your RufusClient has a scan method to fetch the data
    result = client.scan(url,instructions)  # Adjust this based on how your client works
    
    # Check if the result is a list
    assert isinstance(result, list)
    
    # Check that we got a non-empty response
    assert len(result) > 0
    
    # Further validation: Check if the first item has expected keys
    first_post = result[0]
    assert "userId" in first_post
    assert "id" in first_post
    assert "title" in first_post
    assert "body" in first_post
