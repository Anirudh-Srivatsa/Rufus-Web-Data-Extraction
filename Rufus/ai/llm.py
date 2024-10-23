from transformers import pipeline

class SimpleLLM:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = pipeline("text-generation", model="gpt2")  # Using GPT-2 as an example

    def generate_text(self, prompt: str) -> str:
        # Generate text using the model
        response = self.model(prompt, max_length=50, num_return_sequences=1)
        return response[0]['generated_text']
