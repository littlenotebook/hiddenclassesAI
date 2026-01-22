from mastodon import Mastodon
from dotenv import load_dotenv
import os

mastodon = Mastodon(
    access_token=os.getenv("MASTODON_ACCESS_TOKEN"),
    api_base_url=os.getenv("MASTODON_BASE_URL")
)

def publish_post(text: str, image_path: str = None) -> dict:
    """
    Publish a post to Mastodon.
    
    Args:
        text: The post content.
        image_path: Optional path to an image file to attach.

    Returns:
        The Mastodon status response.
    """
    media_ids = None
    if image_path:
        # Upload image first
        media = mastodon.media_post(image_path)
        media_ids = [media]

    # Post text with optional image
    return mastodon.status_post(text, media_ids=media_ids)
