Git Pusher by Onixia
A single-file Python CLI tool that pushes a local folder into any Git repository — with a clean, animated terminal UI.

What it does
Checks if Git is installed; offers to auto-install it if missing.
Asks for the repository URL (the account/owner is auto-detected from it).
Asks for the local folder or file path to push.
Asks for a Personal Access Token (used only for this run, never saved).
Lets you choose:
Replace — wipe the repo and upload the local folder as-is.
Merge — only add files that don't already exist in the repo.
Clones, copies your data in, commits, and pushes to the chosen branch.
Cleans up any stale cached Git credentials on your machine before pushing, so an old token can never silently override the one you just entered.
Requirements
Python 3 (standard library only, no extra packages needed)
Git (auto-installed if missing, on Windows/macOS/Linux)
Usage
bash
python3 git_pusher.py
Follow the on-screen prompts.


