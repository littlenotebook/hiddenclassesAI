from mastodon import Mastodon
import os

mastodon = Mastodon(
    access_token=os.getenv("MASTODON_ACCESS_TOKEN"),
    api_base_url=os.getenv("MASTODON_BASE_URL")
)

def publish_post(text):
    mastodon.status_post(text)
