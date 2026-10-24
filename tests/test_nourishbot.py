import json

import pytest
from PIL import Image

from nourishbot import build_prompt, image_data_url, parse_json_response, prepare_image


def test_build_prompt_carries_diet_and_mode():
    prompt = build_prompt("recipe", "vegan")
    assert "vegan" in prompt
    assert '"mode": "recipe"' in prompt


def test_analysis_prompt_has_nutrition_fields():
    prompt = build_prompt("analysis")
    assert '"protein_g"' in prompt
    assert '"calories_kcal"' in prompt


def test_parse_json_response_accepts_fenced_json():
    payload = {"mode": "analysis", "dish_name": "Soup"}
    assert parse_json_response(f"```json\n{json.dumps(payload)}\n```") == payload


def test_prepare_image_resizes_and_encodes(tmp_path):
    path = tmp_path / "large.png"
    Image.new("RGB", (2200, 1800), "orange").save(path)
    encoded, mime = prepare_image(path.read_bytes())
    assert mime == "image/jpeg"
    assert image_data_url(encoded).startswith("data:image/jpeg;base64,")


def test_build_prompt_rejects_unknown_mode():
    with pytest.raises(ValueError):
        build_prompt("unknown")

