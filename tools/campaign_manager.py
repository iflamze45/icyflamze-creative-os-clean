"""
Manages campaign output folders and file saving.
"""

import os
import re
import json
from datetime import datetime


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:40]


def create_campaign_dir(product_name: str, base_dir: str = "output") -> str:
    slug = slugify(product_name)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    campaign_dir = os.path.join(base_dir, f"{slug}-{timestamp}")
    os.makedirs(os.path.join(campaign_dir, "copy"), exist_ok=True)
    os.makedirs(os.path.join(campaign_dir, "images"), exist_ok=True)
    return campaign_dir


def save_text_file(path: str, content: str) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def save_campaign_json(campaign_dir: str, data: dict) -> str:
    path = os.path.join(campaign_dir, "campaign.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path


def image_path(campaign_dir: str, name: str) -> str:
    return os.path.join(campaign_dir, "images", f"{name}.jpg")


def copy_path(campaign_dir: str, name: str) -> str:
    return os.path.join(campaign_dir, "copy", f"{name}.md")
