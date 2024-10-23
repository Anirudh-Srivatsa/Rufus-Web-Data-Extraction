# rufus/utils/helpers.py

from sentence_transformers import SentenceTransformer
import numpy as np

# Load a pre-trained model for generating embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')  # You can choose other models based on your needs

def compute_similarity(reference_text, candidate_text):
    """
    Computes cosine similarity between two texts using embeddings.
    
    Args:
        reference_text (str): The reference text for relevance.
        candidate_text (str): The candidate text to evaluate.

    Returns:
        float: Cosine similarity score between 0 and 1.
    """
    # Create embeddings
    reference_embedding = model.encode(reference_text, convert_to_tensor=True)
    candidate_embedding = model.encode(candidate_text, convert_to_tensor=True)

    # Compute cosine similarity
    cosine_similarity = np.dot(reference_embedding, candidate_embedding) / (np.linalg.norm(reference_embedding) * np.linalg.norm(candidate_embedding))
    
    return cosine_similarity.item()

def score_content(extracted_content, keywords):
    """
    Scores extracted content based on its relevance to a list of keywords.

    Args:
        extracted_content (str): The content extracted from the webpage.
        keywords (list): A list of keywords or phrases indicating relevance.

    Returns:
        float: Overall relevance score.
    """
    total_score = 0.0
    for keyword in keywords:
        score = compute_similarity(keyword, extracted_content)
        total_score += score

    # Normalize score by the number of keywords
    average_score = total_score / len(keywords) if keywords else 0
    return average_score
