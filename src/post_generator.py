# src/post_generator.py
from llm_client import call_llm

def generate_post(content, examples, context=""):
    """
    Generate a Mastodon post using the content, example posts,
    and optional RAG context from Notion.
    """
    prompt = f"""
You are HiddenClasses, an AI that creates playful, exploratory career posts.

Context from Notion:
{context}

Content to post:
{content}

Example posts:
{examples}

Write ONE Mastodon post (max 500 characters), playful, curious, and encouraging.
"""
    # send prompt to LLM and return text
    return call_llm(prompt) + "\n\n⚠️This post was generated using AI."
