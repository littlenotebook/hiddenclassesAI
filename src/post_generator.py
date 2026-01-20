from llm_client import call_llm

def generate_post(content, examples):
    prompt = f"""
You are HiddenClasses, an AI that creates playful, exploratory career posts.

Context:
{content}

Example posts:
{examples}

Write ONE Mastodon post (max 500 characters), playful, curious, and encouraging.
"""
    # send prompt to LLM here and return text
    return call_llm(prompt)+f"\n\n⚠️This post was generated using AI."
