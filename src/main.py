from notion_api import fetch_first_row
from llm_client import call_llm
from mastodon_client import publish_post
from post_generator import generate_post
from image_gen import generate_image

def main():
    content, examples = fetch_first_row()
    post_text = generate_post(content, examples)
    image_path = generate_image(post_text)
    print("Generated Post:\n", post_text)  # Preview before posting
    publish_post(post_text, image_path=image_path)
    print("Post published to Mastodon!")

if __name__ == "__main__":
    main()
