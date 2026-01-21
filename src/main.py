from notion_api import fetch_first_row
from post_generator import generate_post
from image_gen import generate_image
from mastodon_client import publish_post
from telegram_client import send_review_message, wait_for_decision


def main():
    # 1. Fetch content
    content, examples = fetch_first_row()

    # 2. Generate post + image (but DO NOT publish yet)
    post_text = generate_post(content, examples)
    image_path = generate_image(post_text)

    # 3. Send to Telegram for human review
    send_review_message(post_text)
    decision = wait_for_decision()

    # 4. Gate publishing on approval
    if decision["decision"] == "approve":
        publish_post(post_text, image_path=image_path)
        print("✅ Post approved and published")

    else:
        print("❌ Post rejected:", decision["reason"])
        print("🗑️ Post discarded (not published)")


if __name__ == "__main__":
    main()
