# Git Pusher by Onixia

**A single-file Python CLI tool** that pushes any local folder into a Git repository — with a clean, animated terminal UI.

---

## Features

- Checks if Git is installed and offers to auto-install it if missing
- Supports any Git repository (GitHub, GitLab, Bitbucket, self-hosted, etc.)
- Automatically detects repository owner from the URL
- Two operation modes:
  - **Replace** — completely wipes the remote repo and uploads your folder as-is
  - **Merge** — safely adds only files that don't already exist
- Uses a Personal Access Token (never saved, used only for this run)
- Cleans up stale Git credentials before pushing
- Beautiful animated terminal interface
- Single file — no dependencies other than Python and Git

## Requirements

- **Python 3** (uses only the standard library)
- **Git** (automatically installed if missing on Windows/macOS/Linux)

## Usage

```bash
python3 git_pusher.py
