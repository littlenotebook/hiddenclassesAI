"""
reply_engine.py

Search Mastodon for career-related posts and generate thoughtful,
low-pressure replies as HiddenClasses using structured LLM outputs.
"""

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from mastodon import Mastodon
from openai import OpenAI
from pydantic import BaseModel

from notion_api import fetch_first_row

# ---------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------

load_dotenv(Path(__file__).parent.parent / ".env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MASTODON_ACCESS_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN")
MASTODON_BASE_URL = os.getenv("MASTODON_BASE_URL")

# ---------------------------------------------------------------------
# Search configuration (HiddenClasses-specific)
# ---------------------------------------------------------------------

SEARCH_KEYWORDS = [
    "career path",
    "career advice",
    "learning new skills",
    "side project",
    "freelance work",
    "nonlinear career",
    "creative work",
]

MAX_POSTS = 5
MIN_RELEVANCE_SCORE = 0.6

# ---------------------------------------------------------------------
# Structured LLM outputs
# ---------------------------------------------------------------------


class LLMResponse(BaseModel):
    response_text: str
    is_company_related: bool
    relevance_score: float
    reasoning: str


class LLMResponseBatch(BaseModel):
    responses: List[LLMResponse]


class GeneratedResponse(BaseModel):
    original_post_id: str
    original_post_content: str
    original_post_author: str
    response_text: str
    is_company_related: bool
    relevance_score: float
    reasoning: str


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def get_business_context() -> str:
    """Pull HiddenClasses description from Notion."""
    content, _ = fetch_first_row()
    return content


def search_mastodon(keywords: List[str]) -> List[dict]:
    """Search Mastodon and return unique recent posts."""
    mastodon = Mastodon(
        access_token=MASTODON_ACCESS_TOKEN,
        api_base_url=MASTODON_BASE_URL,
    )

    posts = []
    seen_ids = set()

    for keyword in keywords:
        results = mastodon.search(keyword, result_type="statuses")
        statuses = results.get("statuses", [])

        for status in statuses:
            if status["id"] in seen_ids:
                continue

            seen_ids.add(status["id"])
            posts.append(
                {
                    "id": str(status["id"]),
                    "content": status["content"],
                    "author": status["account"]["acct"],
                    "url": status["url"],
                }
            )

            if len(posts) >= MAX_POSTS:
                return posts

    return posts


def generate_responses(posts: List[dict], business_context: str) -> List[GeneratedResponse]:
    """Generate replies using structured output."""
    if not posts:
        return []

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    posts_text = "\n\n".join(
        f"Post {i + 1}:\n{p['content']}" for i, p in enumerate(posts)
    )

    completion = client.beta.chat.completions.parse(
        model="nvidia/nemotron-3-nano-30b-a3b:free",
        messages=[
            {
                "role": "system",
                "content": f"""
You are the voice of HiddenClasses.

HiddenClasses is an AI-run media project that surfaces overlooked,
adjacent, and unusual career paths and micro-skills.
Careers are framed as exploratory, non-linear, and optional.

About HiddenClasses:
{business_context}

Guidelines:
- Be curious, not corrective
- Avoid hustle or optimization language
- Never tell someone what they *should* do
- Replies should feel like a thoughtful side note
- Mention HiddenClasses only if genuinely relevant
- Max 400 characters
- Calm, warm, human tone

For each post:
- Decide whether replying makes sense
- Assign a relevance score (0.0–1.0)
- Explain your reasoning briefly
- Write the reply text
""",
            },
            {
                "role": "user",
                "content": f"""
Generate responses for the following Mastodon posts.
Return one response per post in order.

Posts:
{posts_text}
""",
            },
        ],
        response_format=LLMResponseBatch,
    )

    llm_responses = completion.choices[0].message.parsed.responses

    return [
        GeneratedResponse(
            original_post_id=post["id"],
            original_post_content=post["content"],
            original_post_author=post["author"],
            **llm_resp.model_dump(),
        )
        for post, llm_resp in zip(posts, llm_responses)
    ]


def post_reply(response: GeneratedResponse):
    """Post a reply to Mastodon."""
    mastodon = Mastodon(
        access_token=MASTODON_ACCESS_TOKEN,
        api_base_url=MASTODON_BASE_URL,
    )

    return mastodon.status_post(
        response.response_text,
        in_reply_to_id=int(response.original_post_id),
    )


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------


def main(post_replies: bool = False):
    print("Loading HiddenClasses context from Notion...")
    business_context = get_business_context()

    print("Searching Mastodon...")
    posts = search_mastodon(SEARCH_KEYWORDS)
    print(f"Found {len(posts)} posts")

    if not posts:
        print("No posts found.")
        return

    print("Generating replies with LLM...")
    responses = generate_responses(posts, business_context)

    print("\n" + "=" * 60)
    print("GENERATED REPLIES")
    print("=" * 60)

    for resp in responses:
        print(f"\n→ Replying to @{resp.original_post_author}")
        print(f"Relevance: {resp.relevance_score:.2f}")
        print(f"Reasoning: {resp.reasoning}")
        print("Reply:")
        print(resp.response_text)

        if (
            post_replies
            and resp.relevance_score >= MIN_RELEVANCE_SCORE
            and resp.response_text.strip()
        ):
            print("Posting reply...")
            result = post_reply(resp)
            print(f"Posted: {result['url']}")

    if not post_replies:
        print("\nDRY RUN — no replies posted.")
        print("Run with `--post` to publish replies.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Reply to relevant Mastodon posts as HiddenClasses"
    )
    parser.add_argument(
        "--post",
        action="store_true",
        help="Actually post replies (default: dry run)",
    )
    args = parser.parse_args()

    main(post_replies=args.post)
