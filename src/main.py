from notion_api import fetch_first_row
from post_generator import generate_post
from image_gen import generate_image
from mastodon_client import publish_post
from telegram_client import send_review_message, wait_for_decision
from rag.retriever import retrieve_context

def main():
    # 1. Fetch content
    content, examples = fetch_first_row()

    # 2. Retrieve relevant Notion context (RAG)
    context = retrieve_context(content, k=5)

    # 3. Generate post + image (but DO NOT publish yet)
    post_text = generate_post(content, examples, context)
    image_path = generate_image(post_text)

    # 4. Send to Telegram for human review
    send_review_message(post_text)
    decision = wait_for_decision()

    # 5. Gate publishing on approval
    if decision["decision"] == "approve":
        publish_post(post_text, image_path=image_path)
        print("✅ Post approved and published")
    else:
        print("❌ Post rejected:", decision["reason"])
        print("🗑️ Post discarded (not published)")

if __name__ == "__main__":
    main()
