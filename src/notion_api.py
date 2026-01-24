import os
import requests
from dotenv import load_dotenv
load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def fetch_first_row():
    """Query the Notion database using the HTTP API (avoids SDK incompatibilities).

    Returns (content, examples) strings from the first row.
    """
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    res = requests.post(url, headers=HEADERS)
    res.raise_for_status()

    response = res.json()
    results = response.get("results", [])
    if not results:
        raise ValueError("No rows found in Notion database!")

    row = results[0]

    # Access the properties safely
    content_prop = row.get("properties", {}).get("Content", {}).get("rich_text", [])
    examples_prop = row.get("properties", {}).get("Example Posts", {}).get("rich_text", [])

    content = content_prop[0].get("plain_text", "") if content_prop else ""
    examples = examples_prop[0].get("plain_text", "") if examples_prop else ""

    return content, examples


def fetch_all_pages():
    """
    Fetch all rows from the Notion database.
    Returns a list of dicts with {id, title, content}.
    """

    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    pages = []
    payload = {}

    while True:
        res = requests.post(url, headers=HEADERS, json=payload)
        res.raise_for_status()
        data = res.json()

        for row in data.get("results", []):
            props = row.get("properties", {})

            # Adjust property names if yours differ
            content_prop = props.get("Content", {}).get("rich_text", [])
            examples_prop = props.get("Example Posts", {}).get("rich_text", [])
            title_prop = props.get("Name", {}).get("title", [])

            content = " ".join(t["plain_text"] for t in content_prop)
            examples = " ".join(t["plain_text"] for t in examples_prop)
            title = " ".join(t["plain_text"] for t in title_prop)

            full_text = "\n".join(
                part for part in [title, content, examples] if part
            )

            if full_text.strip():
                pages.append({
                    "id": row["id"],
                    "title": title or "Untitled",
                    "content": full_text
                })

        # Pagination
        if data.get("has_more"):
            payload["start_cursor"] = data["next_cursor"]
        else:
            break

    return pages



if __name__ == "__main__":
    content, examples = fetch_first_row()
    print("Content:", content)
    print("Example Posts:", examples)
