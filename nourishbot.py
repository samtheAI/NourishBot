"""Core Groq vision workflow for NourishBot."""

from __future__ import annotations

import base64
import io
import json
import os
import re
from typing import Any

from PIL import Image, ImageOps


MODEL_ID = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
MAX_IMAGE_EDGE = 1600


RECIPE_SCHEMA = """
{
  "mode": "recipe",
  "title": "short recipe name",
  "summary": "one useful sentence",
  "detected_items": ["food item"],
  "ingredients": [{"item": "ingredient", "amount": "quantity", "note": "optional note"}],
  "instructions": ["clear numbered-step text without the number"],
  "dietary_notes": ["how the recipe satisfies the requested restriction"],
  "nutrition_per_serving": {
    "calories_kcal": 0, "protein_g": 0, "carbs_g": 0,
    "fat_g": 0, "fiber_g": 0, "sugar_g": 0
  },
  "servings": 0,
  "prep_time_minutes": 0,
  "cook_time_minutes": 0,
  "confidence": "high, medium, or low",
  "warnings": ["allergen, food-safety, uncertainty, or missing-ingredient note"]
}
"""


ANALYSIS_SCHEMA = """
{
  "mode": "analysis",
  "dish_name": "best identification of the dish",
  "summary": "one useful sentence",
  "estimated_portion": "visible serving estimate",
  "nutrition": {
    "calories_kcal": 0, "protein_g": 0, "carbs_g": 0,
    "fat_g": 0, "fiber_g": 0, "sugar_g": 0, "sodium_mg": 0
  },
  "likely_ingredients": ["ingredient"],
  "nutrition_highlights": ["helpful nutritional observation"],
  "dietary_flags": ["likely allergen, dietary conflict, or none identified"],
  "confidence": "high, medium, or low",
  "disclaimer": "short statement that image-based nutrition is an estimate"
}
"""


def prepare_image(image_bytes: bytes) -> tuple[bytes, str]:
    """Normalize an uploaded image and keep payloads small enough for vision APIs."""
    if not image_bytes:
        raise ValueError("The image is empty. Please upload a different file.")

    try:
        with Image.open(io.BytesIO(image_bytes)) as raw:
            image = ImageOps.exif_transpose(raw)
            if image.mode not in ("RGB", "L"):
                background = Image.new("RGB", image.size, "white")
                if "A" in image.getbands():
                    background.paste(image, mask=image.getchannel("A"))
                    image = background
                else:
                    image = image.convert("RGB")
            elif image.mode == "L":
                image = image.convert("RGB")

            image.thumbnail((MAX_IMAGE_EDGE, MAX_IMAGE_EDGE), Image.Resampling.LANCZOS)
            output = io.BytesIO()
            image.save(output, format="JPEG", quality=88, optimize=True)
    except Exception as exc:
        raise ValueError("NourishBot could not read that image. Try a JPG, PNG, or WebP file.") from exc

    return output.getvalue(), "image/jpeg"


def image_data_url(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def build_prompt(workflow: str, dietary_restrictions: str = "") -> str:
    diet = dietary_restrictions.strip() or "No dietary restriction supplied"

    if workflow == "recipe":
        return f"""
You are NourishBot, a careful food-vision cooking assistant. Inspect the image and
identify only ingredients that are reasonably visible. Create one practical recipe
that prioritizes those items. You may add common pantry essentials, but clearly note
them. Respect this dietary request: {diet}.

Return ONLY one valid JSON object matching this exact shape:
{RECIPE_SCHEMA}

Use realistic amounts and concise steps. All nutrition numbers must be numeric
estimates per serving, not strings. Do not claim medical precision. If the image or
ingredients are uncertain, say so in warnings and lower confidence.
""".strip()

    if workflow == "analysis":
        return f"""
You are NourishBot, a careful food-vision nutrition assistant. Inspect the completed
dish, identify the likely food and visible ingredients, estimate the visible portion,
and provide an approximate nutrition breakdown. Dietary context, if any: {diet}.

Return ONLY one valid JSON object matching this exact shape:
{ANALYSIS_SCHEMA}

All nutrition values must be numeric estimates for the visible portion, not strings.
Mention meaningful allergens or uncertainty. Never present the estimate as medical,
diagnostic, or laboratory-grade information.
""".strip()

    raise ValueError(f"Unsupported workflow: {workflow}")


def parse_json_response(content: Any) -> dict[str, Any]:
    """Parse JSON even if a model wraps it in a Markdown fence."""
    if isinstance(content, dict):
        return content
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Groq returned an empty response. Please try again.")

    candidate = content.strip()
    candidate = re.sub(r"^```(?:json)?\s*", "", candidate, flags=re.IGNORECASE)
    candidate = re.sub(r"\s*```$", "", candidate)

    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        start, end = candidate.find("{"), candidate.rfind("}")
        if start == -1 or end <= start:
            raise ValueError("Groq returned an unexpected format. Please try again.")
        try:
            parsed = json.loads(candidate[start : end + 1])
        except json.JSONDecodeError as exc:
            raise ValueError("Groq returned malformed data. Please try again.") from exc

    if not isinstance(parsed, dict):
        raise ValueError("Groq returned an unexpected format. Please try again.")
    return parsed


def analyze_with_groq(
    image_bytes: bytes,
    workflow: str,
    dietary_restrictions: str,
    api_key: str,
    model: str = MODEL_ID,
) -> dict[str, Any]:
    """Send a compressed image plus the selected workflow prompt to Groq."""
    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured.")

    from groq import Groq

    normalized, mime_type = prepare_image(image_bytes)
    client = Groq(api_key=api_key, timeout=30.0, max_retries=1)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": build_prompt(workflow, dietary_restrictions)},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data_url(normalized, mime_type)},
                    },
                ],
            }
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    return parse_json_response(response.choices[0].message.content)

