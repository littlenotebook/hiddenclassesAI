# src/image_generator.py
from pathlib import Path
import replicate

OUTPUT_DIR = Path(__file__).parent.parent / "generated_images"
OUTPUT_DIR.mkdir(exist_ok=True)

MODEL_ID = (
    "sundai-club/flux-orangecat:"
    "8a1f20975a367c8c0f0538062bc99456f6cfd5b6b7a433a30ec45433aa494552"
)


def make_image_prompt(post_text: str) -> str:
    """Generate a HiddenClasses-themed prompt with 'orangecat' as the main subject."""
    return f"""
orangecat as the main subject, minimal illustration, soft pastel palette.
Theme: exploratory careers, hidden skills, side quests.
Visual metaphors: maps, paths, icons, modular systems.
No text, no logos, calm, modern.
Inspired by: {post_text}
"""


def generate_image(post_text: str) -> Path:
    """Generate an image for HiddenClasses using the 'schnell' model."""
    prompt = make_image_prompt(post_text)

    output = replicate.run(
        MODEL_ID,
        input={
            "model": "schnell",
            "prompt": prompt,
            "go_fast": True,
            "lora_scale": 1.5,
            "megapixels": "1",
            "num_outputs": 1,
            "aspect_ratio": "1:1",
            "output_format": "png",
            "guidance_scale": 3,
            "output_quality": 80,
            "prompt_strength": 0.8,
            "extra_lora_scale": 1.5,
            "num_inference_steps": 4,
        },
    )

    # Output is already a PNG, Mastodon-compatible
    image_path = OUTPUT_DIR / "hiddenclass.png"

    with open(image_path, "wb") as f:
        f.write(output[0].read())

    return image_path
