# icyflamze-creative-os-clean

## Project Overview
A free AI creative studio for generating ad campaigns — copy + images — using Claude + Pollinations.ai.
No paid image API needed. No Arcads account needed.

## Files
```
creative_os.py          # Main Creative OS agent (ad copy + images)
repo_agent.py           # Repo reader/installer agent
tools/
  image_generator.py    # Pollinations.ai image generation (free)
  campaign_manager.py   # Output folder + file management
requirements.txt        # claude-agent-sdk, anthropic, anyio
output/                 # Generated campaigns land here (gitignored)
```

## Creative OS — Usage
```bash
pip install -r requirements.txt

# Quick brief as one string
python creative_os.py "Product: Nike Air Max. Audience: sneakerheads 18-30. Vibe: premium street."

# Flags
python creative_os.py --product "ArcAds Cola" --audience "Gen Z" --vibe "bold and fun"

# Interactive mode
python creative_os.py --interactive
```

Each campaign creates a folder under `output/`:
```
output/{product-slug}-{timestamp}/
  brief.md              # Campaign brief + creative angles
  copy/
    variation-1.md      # Hook + body + CTA + platform note
    variation-2.md
    variation-3.md
  images/
    hero.jpg            # Clean product shot
    ugc.jpg             # UGC/lifestyle feel
    lifestyle.jpg       # Product in use
  campaign.json         # Machine-readable summary
```

## Repo Agent — Usage
```bash
python repo_agent.py https://github.com/owner/repo
python repo_agent.py /path/to/local/repo
```

## Known Constraints
- `bypassPermissions` blocked when running as root — uses `acceptEdits` instead
- Pollinations.ai blocked in some server environments but works fine locally
- If image gen fails, the agent saves the prompt to a `.txt` file with a manual generation link

## Image Generation
Uses Pollinations.ai — free, no API key, no signup:
`https://image.pollinations.ai/prompt/{prompt}?width=768&height=768&model=flux`
If blocked, fallback links saved to `images/{name}-prompt.txt`.

## Prompt Engineering — Key Learnings from Arcads Skill

These apply to all image generation in Creative OS:

### UGC Realism (critical)
- Always include the **imperfection block**: motion blur, overexposure, grain, lens distortion,
  off-center framing, soft focus, uneven lighting — without this, output looks too polished
- Always include **skin realism** inline with character: "visible pores, slight unevenness in
  skin tone, minor undereye shadows, hint of shine from natural oils"
- NEVER use: acne, pimples, breakouts, blemishes — goal is "real person, not retouched"
- End with negative cues: "No retouching, no beauty filter, no studio lighting, no airbrushed skin"

### Image Prompt Formula
- **Hero**: `{product} + {style} + {composition} + {lighting} + {background} + Avoid: {}`
- **UGC**: `{camera: raw iPhone front-camera} + {character + skin realism} + {action} + {imperfection block} + {negative cues}`
- **Lifestyle**: `{product in real-world use} + {specific lived-in setting} + {natural lighting} + {mood}`

### Vibe Translation (from vague to visual)
- "premium" → dark backgrounds, minimal props, slow motion, muted palette
- "fun" → bright colors, fast cuts, candid expressions, chaotic energy
- "warm" → golden hour light, hands around product, lived-in spaces
- "bold" → high contrast, direct eye contact, punchy colors, strong shadows

## Session History
### Session 1 (2026-05-03)
- Built `repo_agent.py` using Claude Agent SDK
- Tested against `krusemediallc/arcads-claude-code` — Claude Code skill pack
  - Manually ran setup: `.env`, `MASTER_CONTEXT.md`, synced skills
  - `sync-skill.sh` is at `shared/scripts/sync-skill.sh` (setup.sh has wrong path)
- `bypassPermissions` fails as root — switched to `acceptEdits`

### Session 2 (2026-05-03)
- Built Creative OS (`creative_os.py`) as free Arcads alternative
- Uses Claude Agent SDK + custom MCP tools (save_file, generate_image)
- Pollinations.ai for images (free, no key)
- Read Arcads skill prompting guide + UGC selfie + Nano Banana + SKILL.md
- Upgraded system prompt with Arcads prompt formulas:
  - UGC imperfection block, skin realism block, negative cues
  - Vibe → visual translation system
  - Per-image-type prompt formulas (hero / ugc / lifestyle)
  - Copy structure: hook / body / CTA / platform / dialogue
- Branch: `claude/build-repo-agent-526iM`
