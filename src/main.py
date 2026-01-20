from notion_api import fetch_first_row
from llm_client import call_llm
from mastodon_client import publish_post
from post_generator import generate_post

def main():
    content, examples = fetch_first_row()
    post_text = generate_post(content, examples)
    print("Generated Post:\n", post_text)  # Preview before posting
    publish_post(post_text)
    print("Post published to Mastodon!")

if __name__ == "__main__":
    main()
