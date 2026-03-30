#!/usr/bin/env python3
"""
Repo Agent — reads a repository and installs its dependencies.

Usage:
    python repo_agent.py <repo-url-or-local-path>

Examples:
    python repo_agent.py https://github.com/owner/repo
    python repo_agent.py /path/to/local/repo
    python repo_agent.py .
"""

import sys
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, SystemMessage

SYSTEM_PROMPT = """\
You are a repo agent. Your job is to read a repository and install its dependencies.

Follow these steps carefully:

1. DETECT INPUT TYPE
   - If the input looks like a URL (starts with http/https/git@), clone it first with:
       git clone <url> /tmp/repo_agent_clone
     Then work in /tmp/repo_agent_clone
   - If the input is a local path, work directly in that directory

2. EXPLORE THE REPO
   - List the top-level files and directories
   - Look for key files that indicate the project type and package manager

3. DETECT PROJECT TYPE & PACKAGE MANAGER
   Look for these files (in priority order):
   - package.json           → Node.js (npm/yarn/pnpm)
     - Check for yarn.lock  → use yarn install
     - Check for pnpm-lock  → use pnpm install
     - Otherwise            → use npm install
   - requirements.txt       → Python (pip install -r requirements.txt)
   - pyproject.toml         → Python (pip install -e . or poetry install)
   - Pipfile                → Python (pipenv install)
   - Cargo.toml             → Rust (cargo build)
   - go.mod                 → Go (go mod download)
   - build.gradle / pom.xml → Java (gradle build or mvn install)
   - Gemfile                → Ruby (bundle install)
   - composer.json          → PHP (composer install)
   - mix.exs                → Elixir (mix deps.get)

   A repo may have multiple package managers (e.g., a monorepo with both Python and Node).
   Install ALL of them.

4. RUN INSTALL COMMANDS
   - Run the appropriate install command(s)
   - Show the output so the user can see what happened
   - If a command fails, try to diagnose why and report it

5. REPORT RESULTS
   Summarize:
   - What the repository is (name, description if available)
   - What project types / languages were detected
   - What install commands were run
   - Whether each install succeeded or failed
   - Any issues or notes the user should be aware of
"""


async def run_repo_agent(repo: str) -> None:
    prompt = f"Process this repository and install its dependencies: {repo}"

    print(f"Starting repo agent for: {repo}")
    print("-" * 60)

    session_id = None
    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            system_prompt=SYSTEM_PROMPT,
            allowed_tools=["Read", "Bash", "Glob", "Grep"],
            permission_mode="bypassPermissions",
            max_turns=30,
        ),
    ):
        if isinstance(message, SystemMessage):
            if message.subtype == "init":
                session_id = message.data.get("session_id")
        elif isinstance(message, ResultMessage):
            print("\n" + "=" * 60)
            print("REPO AGENT RESULT")
            print("=" * 60)
            print(message.result)
            if message.stop_reason not in ("end_turn", None):
                print(f"\n[Stop reason: {message.stop_reason}]")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    repo = sys.argv[1]
    anyio.run(run_repo_agent, repo)


if __name__ == "__main__":
    main()
