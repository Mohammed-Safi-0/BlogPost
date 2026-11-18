import os
from huggingface_hub import InferenceClient
from django.conf import settings

client = InferenceClient(
    provider="hf-inference",
    api_key=settings.HUGGINGFACE_API_KEY,
)
def generate_summary(title: str, content: str) -> str:

    text = f"Title: {title}\n\nContent:\n{content}"

    result = client.summarization(
        text,
        model="facebook/bart-large-cnn",
    )

    return result.summary_text.strip()