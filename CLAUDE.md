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
- Outputs full campaign: brief + 3 copy variations + 3 images
- Branch: `claude/build-repo-agent-526iM`
