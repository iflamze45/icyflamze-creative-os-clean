"""
Image generation via Pollinations.ai — completely free, no API key needed.
Falls back gracefully if the service is unavailable.
"""

import urllib.request
import urllib.parse
import urllib.error
import os
import time


POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"


def generate_image(prompt: str, output_path: str, width: int = 768, height: int = 768, model: str = "flux") -> dict:
    """
    Generate an image from a text prompt using Pollinations.ai.
    Returns {"success": bool, "path": str, "error": str | None}
    """
    encoded = urllib.parse.quote(prompt)
    seed = int(time.time()) % 99999
    url = f"{POLLINATIONS_BASE}/{encoded}?width={width}&height={height}&model={model}&nologo=true&seed={seed}"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
        "Referer": "https://pollinations.ai/",
    })

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            if response.status != 200:
                return {"success": False, "path": None, "error": f"HTTP {response.status}"}
            content_type = response.headers.get("Content-Type", "")
            if "image" not in content_type:
                return {"success": False, "path": None, "error": f"Not an image response: {content_type}"}
            with open(output_path, "wb") as f:
                f.write(response.read())
        return {"success": True, "path": output_path, "error": None}
    except urllib.error.HTTPError as e:
        return {"success": False, "path": None, "error": f"HTTP error {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {"success": False, "path": None, "error": f"Network error: {e.reason}"}
    except Exception as e:
        return {"success": False, "path": None, "error": str(e)}
