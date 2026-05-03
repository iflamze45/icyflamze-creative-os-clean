# icyflamze-creative-os-clean

## Project Overview
A repo agent that reads and installs repositories using the Claude Agent SDK.

## Key Files
- `repo_agent.py` — main agent script
- `requirements.txt` — Python dependencies (`claude-agent-sdk`, `anyio`)

## How to Use
```bash
pip install -r requirements.txt
python repo_agent.py <repo-url-or-local-path>

# Examples:
python repo_agent.py https://github.com/owner/repo
python repo_agent.py /path/to/local/repo
python repo_agent.py .
```

## How the Agent Works
1. Detects if input is a URL (clones to `/tmp/repo_agent_clone`) or a local path
2. Explores repo structure with Read/Glob/Grep tools
3. Detects package managers: npm/yarn/pnpm, pip, cargo, go mod, bundle, composer, etc.
4. Runs the appropriate install command(s) — handles monorepos with multiple package managers
5. Reports what was found and installed

## Known Constraints
- **Permission mode:** Uses `acceptEdits` — `bypassPermissions` is blocked when running as root
- **Tools used:** Read, Bash, Glob, Grep
- **Max turns:** 30

## Session History
### Session 1 (2026-05-03)
- Built `repo_agent.py` using Claude Agent SDK (`claude-agent-sdk`)
- Added `requirements.txt`
- Tested against `krusemediallc/arcads-claude-code` — a Claude Code skill pack (no traditional deps)
  - Manually ran setup: created `.env`, `MASTER_CONTEXT.md`, synced skills to `.claude/` and `.cursor/`
  - `sync-skill.sh` lives at `shared/scripts/sync-skill.sh` (not `scripts/` as setup.sh expects — known bug in that repo)
- Discovered `bypassPermissions` fails as root; switched to `acceptEdits`
- Branch: `claude/build-repo-agent-526iM`
