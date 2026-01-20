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


if __name__ == "__main__":
    content, examples = fetch_first_row()
    print("Content:", content)
    print("Example Posts:", examples)
