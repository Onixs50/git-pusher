#!/usr/bin/env python3
"""
Git Pusher by Onixia
---------------------
A polished, animated terminal tool to push local data into any Git repository.
Pure Python standard library - no external dependencies required.

Features:
  - Auto-detects and offers to install Git if it's missing
  - Auto-extracts the Git username/owner directly from the repository URL
  - Animated intro, gradient banners, digital-rain effects, spinners, progress bars, confetti
  - Replace-all (always force-pushes, no matter if content looks unchanged)
    or merge-only (adds only files that don't already exist) push modes
  - Secure token input (never shown on screen, never stored)
"""

import os
import re
import sys
import time
import random
import shutil
import platform
import subprocess
import threading
from urllib.parse import urlparse, urlunparse


# ---------------------------------------------------------------------------
# Windows ANSI support (so colors/animations work in cmd.exe too)
# ---------------------------------------------------------------------------
def _enable_windows_ansi():
    if platform.system() != "Windows":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        pass


_enable_windows_ansi()


# ---------------------------------------------------------------------------
# Colors / styling
# ---------------------------------------------------------------------------
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    WHITE = "\033[97m"


GRADIENT = [
    "\033[38;5;51m", "\033[38;5;45m", "\033[38;5;39m", "\033[38;5;33m",
    "\033[38;5;69m", "\033[38;5;105m", "\033[38;5;141m", "\033[38;5;177m",
    "\033[38;5;213m", "\033[38;5;177m", "\033[38;5;141m", "\033[38;5;105m",
]

CONFETTI_COLORS = [C.CYAN, C.MAGENTA, C.GREEN, C.YELLOW, C.BLUE]


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def term_width(default=76):
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return default


BANNER_LINES = [
    r"   ██████╗ ██╗████████╗    ██████╗ ██╗   ██╗███████╗██╗  ██╗███████╗██████╗ ",
    r"  ██╔════╝ ██║╚══██╔══╝    ██╔══██╗██║   ██║██╔════╝██║  ██║██╔════╝██╔══██╗",
    r"  ██║  ███╗██║   ██║       ██████╔╝██║   ██║███████╗███████║█████╗  ██████╔╝",
    r"  ██║   ██║██║   ██║       ██╔═══╝ ██║   ██║╚════██║██╔══██║██╔══╝  ██╔══██╗",
    r"  ╚██████╔╝██║   ██║       ██║     ╚██████╔╝███████║██║  ██║███████╗██║  ██║",
    r"   ╚═════╝ ╚═╝   ╚═╝       ╚═╝      ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝",
]


# ---------------------------------------------------------------------------
# Animation primitives
# ---------------------------------------------------------------------------
def digital_rain(duration=0.7, width=None):
    """Brief Matrix-style character rain before the banner reveals itself."""
    width = width or min(term_width(), 78)
    chars = "01<>{}[]/\\|+=*#$%git"
    hide_cursor()
    end = time.time() + duration
    while time.time() < end:
        line = "".join(random.choice(chars) for _ in range(width))
        color = random.choice(GRADIENT)
        sys.stdout.write(f"\r{color}{line}{C.RESET}")
        sys.stdout.flush()
        time.sleep(0.03)
    sys.stdout.write("\r" + " " * width + "\r")
    show_cursor()


def print_gradient_banner(delay=0.05):
    for i, line in enumerate(BANNER_LINES):
        color = GRADIENT[i % len(GRADIENT)]
        print(f"{color}{C.BOLD}{line}{C.RESET}")
        time.sleep(delay)
    subtitle = ">> Git Pusher by Onixia <<"
    pad = " " * 25
    print(f"{pad}{C.MAGENTA}{C.BOLD}{subtitle}{C.RESET}")
    tagline = "Push your local data anywhere, beautifully."
    pad2 = " " * 19
    print(f"{pad2}{C.DIM}{tagline}{C.RESET}")


def boot_sequence():
    steps = [
        "Waking up engines",
        "Warming up the terminal",
        "Polishing pixels",
        "Calibrating sparkles",
        "Preparing Git Pusher",
    ]
    hide_cursor()
    for step in steps:
        for dots in range(4):
            sys.stdout.write(f"\r{C.CYAN}{step}{'.' * dots}{' ' * (3 - dots)}{C.RESET}")
            sys.stdout.flush()
            time.sleep(0.07)
    sys.stdout.write("\r" + " " * 50 + "\r")
    show_cursor()


def type_effect(text, delay=0.012, color=C.WHITE):
    for ch in text:
        sys.stdout.write(color + ch + C.RESET)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def rainbow_text(text):
    out = ""
    for i, ch in enumerate(text):
        out += f"{GRADIENT[i % len(GRADIENT)]}{ch}"
    return out + C.RESET


def divider(char="─", color=C.DIM, width=None):
    width = width or min(term_width(), 76)
    print(f"{color}{char * width}{C.RESET}")


def sparkle_line(width=None, duration=0.25):
    """A quick shimmering line used as a transition between sections."""
    width = width or min(term_width(), 76)
    hide_cursor()
    frames = ["✦", "·", "✧", "˙", "∙"]
    end = time.time() + duration
    while time.time() < end:
        line = "".join(random.choice(frames) if random.random() < 0.35 else " " for _ in range(width))
        color = random.choice(GRADIENT)
        sys.stdout.write(f"\r{color}{line}{C.RESET}")
        sys.stdout.flush()
        time.sleep(0.03)
    sys.stdout.write("\r" + " " * width + "\r")
    show_cursor()


def section(title):
    print()
    bar_len = max(1, min(term_width(), 76) - len(title) - 4)
    print(f"{C.BLUE}{C.BOLD}── {rainbow_text(title)}{C.BLUE}{C.BOLD} {'─' * bar_len}{C.RESET}")


def box(title, lines, color=C.CYAN, animate=True):
    width = max([len(title) + 4] + [len(l) + 4 for l in lines] + [40])
    top = f"{color}╭{'─' * (width - 2)}╮{C.RESET}"
    header = f"{color}│{C.RESET} {C.BOLD}{title.ljust(width - 4)}{C.RESET} {color}│{C.RESET}"
    sep = f"{color}├{'─' * (width - 2)}┤{C.RESET}"
    bottom = f"{color}╰{'─' * (width - 2)}╯{C.RESET}"
    rows = [top, header, sep] + [f"{color}│{C.RESET} {l.ljust(width - 4)} {color}│{C.RESET}" for l in lines] + [bottom]
    for r in rows:
        print(r)
        if animate:
            time.sleep(0.03)


# ---------------------------------------------------------------------------
# Spinner
# ---------------------------------------------------------------------------
class Spinner:
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, message="Working"):
        self.message = message
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        hide_cursor()
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()

    def _spin(self):
        i = 0
        while self.running:
            frame = self.frames[i % len(self.frames)]
            color = GRADIENT[i % len(GRADIENT)]
            sys.stdout.write(f"\r{color}{frame}{C.RESET} {self.message}...")
            sys.stdout.flush()
            time.sleep(0.06)
            i += 1
        sys.stdout.write("\r" + " " * (len(self.message) + 20) + "\r")
        sys.stdout.flush()

    def stop(self, success=True, done_message=None):
        self.running = False
        if self.thread:
            self.thread.join()
        show_cursor()
        icon = f"{C.GREEN}✔{C.RESET}" if success else f"{C.RED}✘{C.RESET}"
        msg = done_message or self.message
        print(f"{icon} {msg}")


def progress_bar(label, duration=0.9, width=32):
    hide_cursor()
    steps = 30
    for i in range(steps + 1):
        filled = int(width * i / steps)
        bar = "█" * filled + "░" * (width - filled)
        color = GRADIENT[i % len(GRADIENT)]
        pct = int(100 * i / steps)
        sys.stdout.write(f"\r{color}{label}{C.RESET} [{C.CYAN}{bar}{C.RESET}] {pct:3d}%")
        sys.stdout.flush()
        time.sleep(duration / steps)
    print()
    show_cursor()


def success_flourish():
    frames = ["✦", "✧", "★", "✩", "✪", "✫", "✬", "✭"]
    hide_cursor()
    line = ""
    for i in range(28):
        color = GRADIENT[i % len(GRADIENT)]
        line += f"{color}{frames[i % len(frames)]}{C.RESET}"
        sys.stdout.write(f"\r{line}")
        sys.stdout.flush()
        time.sleep(0.02)
    print()
    show_cursor()


def confetti_rain(rows=4, width=None):
    width = width or min(term_width(), 76)
    chars = "✦✧★✩*.+."
    hide_cursor()
    for _ in range(rows):
        line = "".join(
            f"{random.choice(CONFETTI_COLORS)}{random.choice(chars)}{C.RESET}" if random.random() < 0.25 else " "
            for _ in range(width)
        )
        print(line)
        time.sleep(0.06)
    show_cursor()


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------
def ask(prompt, default=None):
    suffix = f" [{C.DIM}{default}{C.RESET}]" if default else ""
    val = input(f"{C.YELLOW}?{C.RESET} {prompt}{suffix}: ").strip()
    return val if val else (default or "")


def ask_secret(prompt):
    """Token input, shown in plain text on screen (not hidden) per user preference.
    Still never written to disk and wiped from memory/config at the end of the run."""
    return input(f"{C.YELLOW}?{C.RESET} {prompt}: ").strip()


def ask_choice(prompt, choices):
    print(f"{C.YELLOW}?{C.RESET} {prompt}")
    for i, c in enumerate(choices, 1):
        print(f"   {C.CYAN}{i}{C.RESET}) {c}")
    while True:
        raw = input(f"{C.YELLOW}>{C.RESET} Choose [1-{len(choices)}]: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(choices):
            return int(raw) - 1
        print(f"{C.RED}Invalid choice, try again.{C.RESET}")


# ---------------------------------------------------------------------------
# Shell helpers
# ---------------------------------------------------------------------------
def run(cmd, cwd=None):
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    result = subprocess.run(
        cmd, cwd=cwd, shell=False, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    return result.returncode, result.stdout, result.stderr


# Flags injected into every git command that talks to a remote, so it relies
# ONLY on the token embedded in the URL and never a cached/stored credential
# (Windows Credential Manager, ~/.git-credentials, url.insteadOf rewrites, etc.)
NO_STORED_CREDS = ["-c", "credential.helper=", "-c", "credential.useHttpPath=true"]


def run_visible(cmd):
    """Run a command with output/stdin attached to the terminal (for installers needing sudo/passwords)."""
    try:
        result = subprocess.run(cmd, shell=False)
        return result.returncode
    except FileNotFoundError:
        return 127


def check_git_installed():
    code, _, _ = run(["git", "--version"])
    return code == 0


TOKEN_PATTERN = re.compile(r"(ghp_[A-Za-z0-9]+|github_pat_[A-Za-z0-9_]+|gho_[A-Za-z0-9]+)")


def cleanup_stale_git_credentials():
    """
    Find and remove any old cached GitHub token so it can never silently
    override the fresh one this run is about to use. Covers the two places
    that commonly cause this: a stored ~/.git-credentials line, and a
    global `url.<...>.insteadOf` rewrite rule in ~/.gitconfig.
    """
    section("Credential Cleanup")
    spinner = Spinner("Scanning for cached Git credentials")
    spinner.start()
    findings = []

    # 1) ~/.git-credentials plaintext store
    cred_file = os.path.expanduser("~/.git-credentials")
    if os.path.exists(cred_file):
        try:
            with open(cred_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            keep = [l for l in lines if "github.com" not in l]
            if len(keep) != len(lines):
                with open(cred_file, "w", encoding="utf-8") as f:
                    f.writelines(keep)
                findings.append(f"Removed {len(lines) - len(keep)} stale line(s) from ~/.git-credentials")
        except Exception:
            pass

    # 2) Global git config: any url.*.insteadOf or credential.* entry that
    #    embeds a token or points at github.com gets stripped out.
    code, out, _ = run(["git", "config", "--global", "--list"])
    if code == 0:
        for line in out.splitlines():
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            looks_stale = TOKEN_PATTERN.search(value) or (
                "insteadof" in key.lower() and "github.com" in value.lower()
            )
            if looks_stale:
                run(["git", "config", "--global", "--unset-all", key])
                findings.append(f"Removed global git config entry: {key}")

    # 3) Kill any running git credential-cache daemon holding old entries
    run(["git", "credential-cache", "exit"])

    spinner.stop(success=True, done_message="Credential scan complete")
    if findings:
        for item in findings:
            print(f"{C.YELLOW}⚠ {item}{C.RESET}")
    else:
        print(f"{C.DIM}No stale cached credentials found.{C.RESET}")


# ---------------------------------------------------------------------------
# Auto-install Git
# ---------------------------------------------------------------------------
def ensure_git_installed():
    if check_git_installed():
        return True

    section("Git Setup")
    print(f"{C.YELLOW}Git was not found on this system.{C.RESET}")
    choice = ask("Attempt to install Git automatically now? (y/n)", default="y")
    if choice.lower() not in ("y", "yes"):
        print(f"{C.RED}Git is required to continue. Please install it manually: https://git-scm.com/downloads{C.RESET}")
        sys.exit(1)

    system = platform.system()
    installed = False

    if system == "Windows":
        if shutil.which("winget"):
            print(f"{C.CYAN}Installing Git via winget...{C.RESET}")
            installed = run_visible(
                ["winget", "install", "--id", "Git.Git", "-e", "--silent",
                 "--accept-package-agreements", "--accept-source-agreements"]
            ) == 0
        elif shutil.which("choco"):
            print(f"{C.CYAN}Installing Git via Chocolatey...{C.RESET}")
            installed = run_visible(["choco", "install", "git", "-y"]) == 0
        else:
            print(f"{C.RED}No supported package manager found (winget/choco).{C.RESET}")

    elif system == "Darwin":
        if shutil.which("brew"):
            print(f"{C.CYAN}Installing Git via Homebrew...{C.RESET}")
            installed = run_visible(["brew", "install", "git"]) == 0
        else:
            print(f"{C.RED}Homebrew not found. Install it from https://brew.sh, or install Git via Xcode Command Line Tools:{C.RESET}")
            print(f"{C.DIM}  xcode-select --install{C.RESET}")

    elif system == "Linux":
        if shutil.which("apt-get"):
            print(f"{C.CYAN}Installing Git via apt-get (you may be asked for your password)...{C.RESET}")
            run_visible(["sudo", "apt-get", "update"])
            installed = run_visible(["sudo", "apt-get", "install", "-y", "git"]) == 0
        elif shutil.which("dnf"):
            print(f"{C.CYAN}Installing Git via dnf...{C.RESET}")
            installed = run_visible(["sudo", "dnf", "install", "-y", "git"]) == 0
        elif shutil.which("yum"):
            print(f"{C.CYAN}Installing Git via yum...{C.RESET}")
            installed = run_visible(["sudo", "yum", "install", "-y", "git"]) == 0
        elif shutil.which("pacman"):
            print(f"{C.CYAN}Installing Git via pacman...{C.RESET}")
            installed = run_visible(["sudo", "pacman", "-Sy", "--noconfirm", "git"]) == 0
        elif shutil.which("zypper"):
            print(f"{C.CYAN}Installing Git via zypper...{C.RESET}")
            installed = run_visible(["sudo", "zypper", "install", "-y", "git"]) == 0
        elif shutil.which("apk"):
            print(f"{C.CYAN}Installing Git via apk...{C.RESET}")
            installed = run_visible(["sudo", "apk", "add", "git"]) == 0
        else:
            print(f"{C.RED}No supported package manager found (apt-get/dnf/yum/pacman/zypper/apk).{C.RESET}")

    if not installed or not check_git_installed():
        print(f"{C.RED}Automatic installation failed or could not be verified.{C.RESET}")
        print(f"{C.DIM}Please install Git manually: https://git-scm.com/downloads{C.RESET}")
        sys.exit(1)

    print(f"{C.GREEN}✔ Git installed successfully.{C.RESET}")
    return True


# ---------------------------------------------------------------------------
# Repo URL helpers
# ---------------------------------------------------------------------------
def normalize_repo_url(raw_url):
    """Ensure the URL has a scheme, defaulting to https://, and no stray whitespace/slashes."""
    raw_url = raw_url.strip().rstrip("/")
    if not re.match(r"^[a-zA-Z]+://", raw_url):
        raw_url = "https://" + raw_url
    return raw_url


def is_valid_repo_url(repo_url):
    """A usable repo URL must have both a scheme and an actual host."""
    parsed = urlparse(repo_url)
    return bool(parsed.scheme) and bool(parsed.netloc)


def extract_owner(repo_url):
    """Pull the account/organization name straight out of the repo URL's path."""
    parsed = urlparse(repo_url)
    parts = [p for p in parsed.path.split("/") if p]
    return parts[0] if parts else ""


def build_auth_url(repo_url, token):
    """Embed the token into an https:// git URL for authentication.

    Uses urlparse/urlunparse instead of manual string slicing so this can't
    accidentally drop the host if the URL has a trailing slash, stray
    whitespace, or any other quirk - it always rebuilds from real URL parts.
    """
    token = token.strip()
    parsed = urlparse(repo_url)
    if parsed.scheme != "https" or not parsed.netloc:
        return repo_url
    netloc_with_token = f"{token}@{parsed.netloc}"
    return urlunparse((parsed.scheme, netloc_with_token, parsed.path, parsed.params, parsed.query, parsed.fragment))


def copy_merge(src_dir, dst_dir):
    """Copy files from src_dir into dst_dir, skipping anything that already exists."""
    for root, dirs, files in os.walk(src_dir):
        rel = os.path.relpath(root, src_dir)
        target_root = dst_dir if rel == "." else os.path.join(dst_dir, rel)
        os.makedirs(target_root, exist_ok=True)
        for f in files:
            src_file = os.path.join(root, f)
            dst_file = os.path.join(target_root, f)
            if not os.path.exists(dst_file):
                shutil.copy2(src_file, dst_file)


# ---------------------------------------------------------------------------
# Main flow
# ---------------------------------------------------------------------------
def main():
    clear()
    digital_rain(0.6)
    boot_sequence()
    print_gradient_banner()
    print()
    type_effect("Push local data into any Git repository. Fast, clean, simple.", 0.01, C.DIM)
    divider()

    ensure_git_installed()
    cleanup_stale_git_credentials()

    # Step 1: Repository URL (username/owner is auto-extracted from it)
    section("Repository")
    raw_repo_url = ask("Repository URL (https://github.com/user/repo.git)")
    while not raw_repo_url:
        print(f"{C.RED}Repository URL is required.{C.RESET}")
        raw_repo_url = ask("Repository URL")
    repo_url = normalize_repo_url(raw_repo_url)
    while not is_valid_repo_url(repo_url):
        print(f"{C.RED}That doesn't look like a valid URL (missing host). Try again.{C.RESET}")
        raw_repo_url = ask("Repository URL")
        repo_url = normalize_repo_url(raw_repo_url)
    git_username = extract_owner(repo_url)
    if git_username:
        print(f"{C.DIM}Detected account:{C.RESET} {C.CYAN}{git_username}{C.RESET}")

    sparkle_line(duration=0.2)

    # Step 2: Local data path
    section("Local Data")
    data_path = ask("Local folder or file path to push")
    while not data_path or not os.path.exists(data_path):
        print(f"{C.RED}Path does not exist. Try again.{C.RESET}")
        data_path = ask("Local folder or file path to push")
    data_path = os.path.abspath(data_path)

    sparkle_line(duration=0.2)

    # Step 3: Token
    section("Authentication")
    token = ask_secret("Personal Access Token (with repo write access)")
    while not token:
        print(f"{C.RED}Token is required.{C.RESET}")
        token = ask_secret("Personal Access Token")

    sparkle_line(duration=0.2)

    # Step 4: Push mode
    section("Push Mode")
    mode_index = ask_choice(
        "The repository may already contain this data with some changes. What do you want to do?",
        [
            "Replace everything - wipe the repo and upload the current folder as-is (always pushed, even if it looks unchanged)",
            "Merge - only add files that don't already exist in the repo, leave the rest untouched",
        ],
    )
    mode = "replace" if mode_index == 0 else "merge"

    # Step 5: Branch
    branch = ask("Branch name", default="main")

    # Confirmation
    section("Summary")
    box("Ready to push", [
        f"Repo:     {repo_url}",
        f"Account:  {git_username or '(unknown)'}",
        f"Data:     {data_path}",
        f"Token:    {token}",
        f"Mode:     {'Replace all' if mode == 'replace' else 'Merge (add new only)'}",
        f"Branch:   {branch}",
    ])
    print()
    confirm = ask("Proceed? (y/n)", default="y")
    if confirm.lower() not in ("y", "yes"):
        print(f"{C.YELLOW}Cancelled.{C.RESET}")
        sys.exit(0)

    work_dir = os.path.join(os.getcwd(), ".git_pusher_temp")
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)

    auth_url = build_auth_url(repo_url, token)

    section("Working")

    # Clone the repo
    spinner = Spinner("Cloning repository")
    spinner.start()
    code, _, err = run(["git", *NO_STORED_CREDS, "clone", "--branch", branch, auth_url, work_dir])
    if code != 0:
        spinner.stop(success=False, done_message="Branch not found, trying default branch")
        spinner = Spinner("Cloning default branch")
        spinner.start()
        code2, _, err2 = run(["git", *NO_STORED_CREDS, "clone", auth_url, work_dir])
        spinner.stop(success=(code2 == 0), done_message="Repository cloned" if code2 == 0 else "Clone failed")
        if code2 != 0:
            print(f"{C.RED}{err2.strip()}{C.RESET}")
            sys.exit(1)
        run(["git", "checkout", "-b", branch], cwd=work_dir)
    else:
        spinner.stop(success=True, done_message="Repository cloned")

    # Local commit identity
    run(["git", "config", "user.name", git_username or "git-pusher"], cwd=work_dir)
    run(["git", "config", "user.email", f"{git_username or 'git-pusher'}@users.noreply.github.com"], cwd=work_dir)

    # Replace mode: clear everything except .git
    if mode == "replace":
        spinner = Spinner("Clearing existing repository content")
        spinner.start()
        for item in os.listdir(work_dir):
            if item == ".git":
                continue
            full = os.path.join(work_dir, item)
            if os.path.isdir(full):
                shutil.rmtree(full)
            else:
                os.remove(full)
        spinner.stop(success=True, done_message="Existing content cleared")

    # Copy local data in
    progress_bar("Copying local data", duration=1.0)
    if os.path.isdir(data_path):
        if mode == "replace":
            for item in os.listdir(data_path):
                src = os.path.join(data_path, item)
                dst = os.path.join(work_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
        else:
            copy_merge(data_path, work_dir)
    else:
        dst = os.path.join(work_dir, os.path.basename(data_path))
        if mode == "replace" or not os.path.exists(dst):
            shutil.copy2(data_path, dst)
    print(f"{C.GREEN}✔{C.RESET} Data copied")

    # Stage
    spinner = Spinner("Staging changes")
    spinner.start()
    run(["git", "add", "-A"], cwd=work_dir)
    spinner.stop(success=True, done_message="Changes staged")

    _, status_out, _ = run(["git", "status", "--porcelain"], cwd=work_dir)
    has_changes = bool(status_out.strip())

    if not has_changes and mode == "merge":
        print(f"{C.YELLOW}Nothing new to add, repository already up to date.{C.RESET}")
        shutil.rmtree(work_dir, ignore_errors=True)
        sys.exit(0)

    # Commit (replace mode always commits, even if content looks identical)
    spinner = Spinner("Committing changes")
    spinner.start()
    commit_msg = f"Git Pusher by Onixia: {'replace' if mode == 'replace' else 'merge'} update"
    commit_cmd = ["git", "commit", "-m", commit_msg]
    if not has_changes:
        commit_cmd.insert(2, "--allow-empty")
    code, _, err = run(commit_cmd, cwd=work_dir)
    spinner.stop(success=(code == 0), done_message="Changes committed" if code == 0 else "Commit failed")
    if code != 0:
        print(f"{C.RED}{err.strip()}{C.RESET}")
        shutil.rmtree(work_dir, ignore_errors=True)
        sys.exit(1)

    # Push (replace mode force-pushes to guarantee the folder always lands exactly as given)
    # Re-assert the remote URL right before pushing, in case anything on this
    # machine (insteadOf rewrite, credential helper, etc.) altered it since clone.
    run(["git", *NO_STORED_CREDS, "remote", "set-url", "origin", auth_url], cwd=work_dir)

    spinner = Spinner(f"Pushing to {branch}")
    spinner.start()
    push_cmd = ["git", *NO_STORED_CREDS, "push", "-u", "origin", branch]
    if mode == "replace":
        push_cmd.insert(len(NO_STORED_CREDS) + 2, "--force")
    code, _, err = run(push_cmd, cwd=work_dir)
    spinner.stop(success=(code == 0), done_message="Push complete" if code == 0 else "Push failed")
    if code != 0:
        print(f"{C.RED}{err.strip()}{C.RESET}")
        shutil.rmtree(work_dir, ignore_errors=True)
        sys.exit(1)

    shutil.rmtree(work_dir, ignore_errors=True)

    # The token only ever lived in memory and in the temp folder's .git/config,
    # which is now deleted above. Clear the in-memory reference too.
    token = None
    auth_url = None

    print()
    success_flourish()
    confetti_rain(rows=3)
    box("Success", [
        f"Pushed to: {repo_url}",
        f"Branch:    {branch}",
        f"Mode:      {'Replace all' if mode == 'replace' else 'Merge'}",
    ], color=C.GREEN)
    print(f"{C.DIM}Token was not saved anywhere and has been cleared from memory.{C.RESET}")
    print(f"{C.DIM}Git Pusher by Onixia — done.{C.RESET}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        show_cursor()
        print(f"\n{C.RED}Cancelled by user.{C.RESET}")
        sys.exit(1)
