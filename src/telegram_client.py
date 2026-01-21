import os
import time
import requests

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_review_message(post_text: str) -> int:
    """Send post for approval with inline buttons."""
    payload = {
        "chat_id": CHAT_ID,
        "text": f"📝 *Post Review*\n\n{post_text}",
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "✅ Approve", "callback_data": "approve"},
                    {"text": "❌ Reject", "callback_data": "reject"},
                ]
            ]
        },
    }

    res = requests.post(f"{BASE_URL}/sendMessage", json=payload)
    res.raise_for_status()
    return res.json()["result"]["message_id"]


def get_updates(offset=None):
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    return requests.get(f"{BASE_URL}/getUpdates", params=params).json()


def wait_for_decision():
    """Block until user approves or rejects."""
    last_update_id = None

    while True:
        updates = get_updates(last_update_id)

        for update in updates.get("result", []):
            last_update_id = update["update_id"] + 1

            # Button click
            if "callback_query" in update:
                callback = update["callback_query"]
                action = callback["data"]

                # Acknowledge button click
                requests.post(
                    f"{BASE_URL}/answerCallbackQuery",
                    json={"callback_query_id": callback["id"]},
                )

                if action == "approve":
                    return {"decision": "approve"}

                if action == "reject":
                    reason = ask_rejection_reason()
                    return {
                        "decision": "reject",
                        "reason": reason,
                    }

        time.sleep(1)


def ask_rejection_reason() -> str:
    """Ask user for rejection reason."""
    requests.post(
        f"{BASE_URL}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": "❌ Please reply with a short reason for rejection.",
        },
    )

    last_update_id = None

    while True:
        updates = get_updates(last_update_id)

        for update in updates.get("result", []):
            last_update_id = update["update_id"] + 1

            if "message" in update:
                msg = update["message"]
                if msg.get("text"):
                    return msg["text"]

        time.sleep(1)
