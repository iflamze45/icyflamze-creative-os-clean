#!/usr/bin/env python3
"""
Creative OS — Free AI ad creative generator.

Generates ad copy + images using Claude + Pollinations.ai (both free).

Usage:
    python creative_os.py "Product: ArcAds Cola Can. Audience: Gen Z. Vibe: bold and energetic."
    python creative_os.py --product "Nike Air Max" --audience "sneakerheads 18-30" --vibe "premium street"
    python creative_os.py --interactive
"""

import sys
import os
import json
import argparse
import anyio
from claude_agent_sdk import (
    tool,
    create_sdk_mcp_server,
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
)
from tools.image_generator import generate_image
from tools.campaign_manager import (
    create_campaign_dir,
    save_text_file,
    save_campaign_json,
    image_path,
    copy_path,
)

# ── Global campaign context (set per run) ─────────────────────────────────────
_campaign_dir: str = ""
_campaign_meta: dict = {}


SYSTEM_PROMPT = """\
You are Creative OS — an expert AI advertising creative director.

Your job: given a product brief, produce a complete ad campaign package with:

1. CAMPAIGN BRIEF (brief.md)
   - Product summary, target audience, key message, tone/vibe
   - 3 creative angles to explore

2. AD COPY VARIATIONS (copy/variation-1.md through copy/variation-3.md)
   Each variation must include:
   - Hook / Headline (punchy, scroll-stopping — under 10 words)
   - Body copy (2-3 sentences, benefit-driven, matches the vibe)
   - CTA (Call to Action — direct and specific)
   - Platform note (where this copy works best: TikTok, Instagram, Meta Feed, etc.)

3. IMAGE PROMPTS + GENERATION
   Generate 3 images using the generate_image tool:
   - hero: clean product shot on a striking background
   - ugc: lifestyle/UGC-style, feels authentic, person implied or present
   - lifestyle: product in use, aspirational setting

   For image prompts, be very specific: lighting, angle, mood, color palette, shot type.
   Good prompt example: "product photo of a cola can on a neon-lit bar counter, moody blue-purple
   lighting, shallow depth of field, photorealistic, 4k, no text"

4. CAMPAIGN SUMMARY (campaign.json — auto-saved)

RULES:
- Always use the save_file tool to write copy files
- Always use generate_image for all 3 images
- Be opinionated — don't hedge, make strong creative choices
- Copy should feel human, not like AI wrote it
- Adapt tone completely to the vibe: bold copy for bold brands, warm for lifestyle, etc.
- After finishing, print a clear summary of everything that was created
"""


def make_tools(campaign_dir: str, campaign_meta: dict):

    @tool(
        "save_file",
        "Save a text file to the campaign output folder. Use for brief.md and copy/variation-*.md",
        {"filename": str, "content": str},
    )
    async def save_file(args):
        filename = args["filename"]
        content = args["content"]
        path = os.path.join(campaign_dir, filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        save_text_file(path, content)
        return {"content": [{"type": "text", "text": f"Saved: {path}"}]}

    @tool(
        "generate_image",
        "Generate an AI image from a prompt and save it. Use for hero, ugc, and lifestyle images.",
        {"prompt": str, "name": str, "width": int, "height": int},
    )
    async def gen_image(args):
        prompt = args["prompt"]
        name = args["name"]
        width = args.get("width", 768)
        height = args.get("height", 768)
        path = image_path(campaign_dir, name)
        result = generate_image(prompt, path, width=width, height=height)
        if result["success"]:
            campaign_meta.setdefault("images", {})[name] = path
            return {"content": [{"type": "text", "text": f"Image saved: {path}"}]}
        else:
            # Save the prompt as a text file so the user can generate it manually
            fallback_path = image_path(campaign_dir, name).replace(".jpg", "-prompt.txt")
            save_text_file(fallback_path, f"IMAGE PROMPT ({name}):\n\n{prompt}\n\nGenerate at: https://pollinations.ai/create/{prompt.replace(' ', '+')}\nOr: https://www.bing.com/images/create")
            return {"content": [{"type": "text", "text": f"Image generation failed ({result['error']}). Prompt saved to {fallback_path}. You can generate it manually at pollinations.ai or bing.com/images/create"}]}

    return [save_file, gen_image]


async def run_creative_os(brief: str, product_name: str) -> None:
    campaign_dir = create_campaign_dir(product_name)
    campaign_meta = {"product": product_name, "brief": brief, "campaign_dir": campaign_dir}

    print(f"\n Creative OS")
    print(f" Campaign: {campaign_dir}")
    print("-" * 60)

    tools_list = make_tools(campaign_dir, campaign_meta)
    server = create_sdk_mcp_server("creative-tools", tools=tools_list)

    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={"creative": server},
        permission_mode="acceptEdits",
        max_turns=40,
    )

    prompt = f"""Create a full ad campaign for this product brief:

{brief}

Campaign output folder: {campaign_dir}

Generate all copy files and all 3 images. Then print a summary of what was created."""

    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock) and block.text.strip():
                        print(block.text)
            elif isinstance(message, ResultMessage):
                save_campaign_json(campaign_dir, campaign_meta)
                print(f"\n Campaign saved to: {campaign_dir}/")


def build_brief(args) -> tuple[str, str]:
    if args.brief:
        product = args.brief.split(".")[0].replace("Product:", "").strip()
        return args.brief, product

    product = args.product or input("Product name: ").strip()
    audience = args.audience or input("Target audience: ").strip()
    vibe = args.vibe or input("Vibe / tone (e.g. bold, warm, luxury, playful): ").strip()
    extra = args.notes or ""

    brief = f"Product: {product}. Target audience: {audience}. Vibe: {vibe}."
    if extra:
        brief += f" Additional notes: {extra}"

    return brief, product


def main():
    parser = argparse.ArgumentParser(description="Creative OS — free AI ad creative generator")
    parser.add_argument("brief", nargs="?", help="Full brief as a single string")
    parser.add_argument("--product", help="Product name")
    parser.add_argument("--audience", help="Target audience")
    parser.add_argument("--vibe", help="Tone / vibe")
    parser.add_argument("--notes", help="Additional creative notes")
    parser.add_argument("--interactive", action="store_true", help="Interactive prompt mode")
    args = parser.parse_args()

    if not args.brief and not args.product and not args.interactive:
        parser.print_help()
        print("\nExamples:")
        print('  python creative_os.py "Product: Nike Air Max. Audience: sneakerheads 18-30. Vibe: premium street."')
        print("  python creative_os.py --product 'ArcAds Cola' --audience 'Gen Z' --vibe 'bold and fun'")
        print("  python creative_os.py --interactive")
        sys.exit(0)

    brief, product_name = build_brief(args)
    anyio.run(run_creative_os, brief, product_name)


if __name__ == "__main__":
    main()
