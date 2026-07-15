#!/usr/bin/env python3
"""
One-click setup for Verifi AI.

What this does, in order:
  1. Checks your Python version
  2. Creates a virtual environment inside server/
  3. Installs the exact dependencies app.py needs
  4. Verifies the model + data files are present (fails loudly if not,
     instead of crashing later with a cryptic error)
  5. Starts the Flask backend on http://127.0.0.1:5050
  6. Opens chrome://extensions and prints the 4 clicks needed to load
     the extension

Usage:
    python3 setup.py        (Mac/Linux)
    python setup.py         (Windows)

Or just double-click setup.sh (Mac/Linux) or setup.bat (Windows).
"""

import os
import sys
import subprocess
import time
import venv
import webbrowser
import socket
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SERVER_DIR = ROOT / "server"
EXTENSION_DIR = ROOT / "extension"
VENV_DIR = SERVER_DIR / "venv"

REQUIRED_FILES = [
    SERVER_DIR / "app.py",
    SERVER_DIR / "requirements.txt",
    SERVER_DIR / "health_model.pkl",
    SERVER_DIR / "finance_model.pkl",
    SERVER_DIR / "data" / "local_news.json",
]

REQUIRED_EXTENSION_FILES = [
    EXTENSION_DIR / "manifest.json",
    EXTENSION_DIR / "background.js",
    EXTENSION_DIR / "content.js",
]


def banner(msg):
    print("\n" + "=" * 60)
    print(msg)
    print("=" * 60)


def check_python_version():
    if sys.version_info < (3, 8):
        sys.exit("Python 3.8+ is required. Please install a newer Python and re-run.")


def check_required_files():
    missing = [str(f.relative_to(ROOT)) for f in REQUIRED_FILES + REQUIRED_EXTENSION_FILES if not f.exists()]
    if missing:
        banner("Missing required files — fix these and re-run setup.py")
        for m in missing:
            print(f"  - {m}")
        print(f"\nExpected layout:\n"
              f"  {ROOT}/\n"
              f"    server/       <- app.py, requirements.txt, *.pkl, data/local_news.json\n"
              f"    extension/    <- manifest.json, background.js, content.js\n")
        sys.exit(1)


def venv_paths():
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe", VENV_DIR / "Scripts" / "pip.exe"
    return VENV_DIR / "bin" / "python", VENV_DIR / "bin" / "pip"


def create_venv():
    if VENV_DIR.exists():
        print("Virtual environment already exists, skipping creation.")
        return
    banner("Creating virtual environment (server/venv)")
    venv.EnvBuilder(with_pip=True).create(VENV_DIR)


def install_requirements():
    banner("Installing dependencies (first run can take ~1 minute)")
    _, pip_path = venv_paths()
    subprocess.run(
        [str(pip_path), "install", "-q", "-r", str(SERVER_DIR / "requirements.txt")],
        check=True,
    )


def port_is_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex((host, port)) == 0


def start_server():
    if port_is_open("127.0.0.1", 5050):
        banner("Backend already running on port 5050 — reusing it")
        return None

    banner("Starting Flask backend on http://127.0.0.1:5050")
    python_path, _ = venv_paths()
    proc = subprocess.Popen([str(python_path), "app.py"], cwd=str(SERVER_DIR))

    for _ in range(20):
        if port_is_open("127.0.0.1", 5050):
            print("Backend is up.")
            return proc
        time.sleep(0.5)

    print("Warning: backend did not respond within 10s. Scroll up for the server's own error output.")
    return proc


def open_extensions_page():
    banner("Opening chrome://extensions")
    try:
        webbrowser.get("chrome").open("chrome://extensions/")
    except webbrowser.Error:
        try:
            webbrowser.open("chrome://extensions/")
        except Exception:
            print("Could not auto-open Chrome. Open it yourself and go to chrome://extensions")


def print_extension_instructions():
    banner("Load the Chrome extension (one-time, ~15 seconds)")
    print(f"""
1. In the tab that just opened, turn ON "Developer mode" (top-right toggle).
2. Click "Load unpacked".
3. Select this exact folder:

   {EXTENSION_DIR}

4. Done. Highlight any text on any webpage, right-click, and choose
   "Verify Text with Verifi AI".
""")


def main():
    check_python_version()
    check_required_files()
    create_venv()
    install_requirements()
    server_proc = start_server()
    open_extensions_page()
    print_extension_instructions()

    if server_proc is None:
        banner("Setup complete")
        return

    banner("Backend is running — leave this window open while you demo")
    print("Press Ctrl+C to stop the server.\n")
    try:
        server_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server_proc.terminate()


if __name__ == "__main__":
    main()