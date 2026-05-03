#!/usr/bin/env python3
"""
Zero Budget Studio (ZBS) — Free AI ad creative generator.

Studio-quality ad campaigns — copy + images — using Claude + Pollinations.ai.
No paid APIs. No accounts. No money.

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
You are Creative OS — a senior AI advertising creative director with deep expertise in
performance marketing, UGC content, and scroll-stopping ad creative.

Your job: given a product brief, produce a complete ad campaign package.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1 — DECODE THE BRIEF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Extract:
- Audience: who is this for? (be specific — not "young people", say "Gen Z college students")
- Job to be done: what should the viewer FEEL or DO after seeing this?
- Offer / proof: core benefit + any social proof
- Hook territory: what pattern interrupt, curiosity, or relatable moment works here?
- Vibe translation: turn vague adjectives into visual specifics
  ("premium" → dark backgrounds, minimal props, slow motion, muted palette)
  ("fun" → bright colors, fast cuts, candid expressions, chaotic energy)
  ("warm" → golden hour light, hands around product, lived-in spaces)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2 — CAMPAIGN BRIEF  →  save_file("brief.md", ...)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Include:
- Product summary + one concrete benefit
- Audience (specific)
- Key message (one sentence — what should stick in their head)
- Vibe → visual translation (colors, lighting, pace, energy)
- 3 creative angles to explore (each a different emotional territory)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3 — AD COPY  →  save_file("copy/variation-1.md", ...) × 3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Each variation = different emotional angle. Format:

**Hook** (under 10 words, scroll-stopping — question / bold claim / relatable moment)
**Body** (2-3 sentences, benefit-led, sounds like a real person wrote it)
**CTA** (specific action, not just "Shop now" — "Grab yours before they sell out again")
**Platform** (where this copy works best and why)
**Dialogue** (optional: 15-25 words if this ran as a UGC talking-head video, what would they say?)

COPY RULES:
- No corporate speak. No "innovative solution." Write how people actually talk.
- Each variation must hit a DIFFERENT emotional lever: e.g. FOMO / curiosity / aspiration
- If the vibe is bold — be bold. If warm — be warm. Don't split the difference.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 4 — IMAGES  →  generate_image(...) × 3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generate exactly 3 images. Use these formulas:

▸ NAME: "hero"
  Formula: {product} + {style: photorealistic product hero} + {composition} +
  {lighting: 3-point studio OR dramatic single-source} + {background: clean/striking} +
  {avoid: people, text, clutter}
  Example: "Minimal product hero: matte cola can on wet black marble, dramatic side
  lighting casting a long shadow, shallow depth of field, photorealistic 4k, no text,
  no people, no extra props"

▸ NAME: "ugc"
  Formula: {camera: raw iPhone front-camera selfie} + {character description with
  SKIN REALISM} + {action with product} + {candid expression} + {setting} +
  {IMPERFECTION BLOCK} + {NEGATIVE CUES}

  SKIN REALISM (pick 3-4, embed in character description):
  "visible pores, slight unevenness in skin tone, minor undereye shadows,
  hint of shine on nose and forehead from natural oils"
  NEVER use: acne, pimples, blemishes, redness — goal is "real person, not retouched"

  IMPERFECTION BLOCK (include all of these for UGC):
  "slight motion blur on hair strands, slightly overexposed highlights on forehead and
  nose, visible image grain and noise, iPhone front camera wide-angle lens distortion,
  slightly off-center framing tilted a few degrees, washed-out flat color grading,
  soft focus — nothing is tack sharp, uneven ambient indoor lighting"

  NEGATIVE CUES:
  "No retouching, no beauty filter, no studio lighting, not a professional photo,
  no airbrushed skin, no flawless complexion, not perfectly composed"

▸ NAME: "lifestyle"
  Formula: {product in aspirational real-world use} + {setting: lived-in, specific} +
  {lighting: natural or golden hour} + {mood matches vibe} + {person implied or partial}
  Make it feel like a real moment, not a stock photo. Messy details = authentic.

IMAGE PROMPT RULES:
- Be hyper-specific: name the lighting, angle, color palette, and shot type
- Longer prompt = better output: aim for 3-5 sentences per image
- Never just describe what you want — describe what the camera sees

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXECUTION ORDER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. save_file → brief.md
2. save_file → copy/variation-1.md
3. save_file → copy/variation-2.md
4. save_file → copy/variation-3.md
5. generate_image → hero
6. generate_image → ugc
7. generate_image → lifestyle
8. Print a clean summary: what was created, where it was saved, key creative decisions made
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

    print(f"\n Zero Budget Studio (ZBS)")
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
    parser = argparse.ArgumentParser(description="Zero Budget Studio (ZBS) — free AI ad creative generator")
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
