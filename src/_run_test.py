import os
import types

# Set required env vars to dummy values
os.environ.setdefault("NOTION_API_KEY", "test-notion-key")
os.environ.setdefault("NOTION_DATABASE_ID", "test-db-id")
os.environ.setdefault("OPENROUTER_API_KEY", "test-openrouter-key")
os.environ.setdefault("MASTODON_BASE_URL", "https://example.test")
os.environ.setdefault("MASTODON_ACCESS_TOKEN", "test-mastodon-token")

# Mock requests.post to return deterministic responses for Notion and OpenRouter
import requests

class MockResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        return None

    def json(self):
        return self._data


def fake_post(url, json=None, headers=None):
    if "api.notion.com" in url:
        # Return a Notion-like database query response with one row
        data = {
            "results": [
                {
                    "properties": {
                        "Content": {"rich_text": [{"plain_text": "Mock Content from Notion"}]},
                        "Example Posts": {"rich_text": [{"plain_text": "Mock example post"}]},
                    }
                }
            ]
        }
        return MockResponse(data)
    elif "openrouter.ai" in url:
        # Return a fake OpenRouter chat completion
        data = {"choices": [{"message": {"content": "This is a generated Mastodon post (mock)."}}]}
        return MockResponse(data)
    else:
        return MockResponse({})

# Apply the monkeypatch
requests.post = fake_post

# Replace mastodon_client.mastodon with a mock that records the posted text
import mastodon_client

class MockMastodon:
    def __init__(self):
        self.posts = []

    def status_post(self, text):
        print("[mock] Mastodon.status_post called with:\n", text)
        self.posts.append(text)

mastodon_client.mastodon = MockMastodon()

# Run the main flow
import main

if __name__ == "__main__":
    main.main()
    print("\nTest run complete. Mock Mastodon posts:\n", mastodon_client.mastodon.posts)
