#!/usr/bin/env python3
"""
CLI Environment Verification
Tests that your AI CLIs are properly configured and accessible

Run: python verify_env.py
"""

import subprocess
import sys
import shutil
from pathlib import Path


def check_command(cmd: str, test_args: list = None) -> dict:
    """Check if a command exists and optionally test it"""
    result = {
        "command": cmd,
        "exists": False,
        "path": None,
        "test_passed": None,
        "error": None
    }
    
    # Check if command exists
    path = shutil.which(cmd)
    if path:
        result["exists"] = True
        result["path"] = path
        
        # Run test if args provided
        if test_args:
            try:
                proc = subprocess.run(
                    [cmd] + test_args,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                result["test_passed"] = proc.returncode == 0
                if proc.returncode != 0:
                    result["error"] = proc.stderr[:200]
            except subprocess.TimeoutExpired:
                result["test_passed"] = False
                result["error"] = "Command timed out"
            except Exception as e:
                result["test_passed"] = False
                result["error"] = str(e)
    
    return result


def main():
    print("\n" + "=" * 60)
    print("🔍 Multi-AI Orchestrator - Environment Verification")
    print("=" * 60 + "\n")
    
    checks = []
    
    # Check Claude CLI
    print("Checking Claude CLI...")
    claude = check_command("claude", ["--version"])
    checks.append(claude)
    if claude["exists"]:
        print(f"  ✅ Found: {claude['path']}")
        if claude["test_passed"]:
            print("  ✅ Version check passed")
        else:
            print(f"  ⚠️  Version check failed: {claude.get('error', 'unknown')}")
    else:
        print("  ❌ Not found")
        print("     Install: npm install -g @anthropic-ai/claude-code")
        print("     Then run: claude auth")
    
    print()
    
    # Check Gemini CLI
    print("Checking Gemini CLI...")
    gemini = check_command("gemini", ["--version"])
    checks.append(gemini)
    if gemini["exists"]:
        print(f"  ✅ Found: {gemini['path']}")
        if gemini["test_passed"]:
            print("  ✅ Version check passed")
        else:
            print(f"  ⚠️  Version check failed: {gemini.get('error', 'unknown')}")
    else:
        print("  ❌ Not found")
        print("     Install: npm install -g @anthropic-ai/gemini-cli")
        print("     Then set: export GEMINI_API_KEY='your-key'")
    
    print()
    
    # Check Fara-7B
    print("Checking Fara-7B...")
    fara_dir = Path.home() / "fara"
    fara_venv = fara_dir / ".venv" / "bin" / "python"
    
    if fara_dir.exists():
        print(f"  ✅ Fara directory found: {fara_dir}")
        if fara_venv.exists():
            print(f"  ✅ Virtual environment found")
            # Test import
            try:
                result = subprocess.run(
                    [str(fara_venv), "-c", "import fara; print('ok')"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(fara_dir)
                )
                if result.returncode == 0:
                    print("  ✅ Fara module importable")
                else:
                    print(f"  ⚠️  Fara import failed: {result.stderr[:100]}")
            except Exception as e:
                print(f"  ⚠️  Could not test Fara: {e}")
        else:
            print("  ⚠️  Virtual environment not found at .venv/bin/python")
            print("     Run: cd ~/fara && python3 -m venv .venv && source .venv/bin/activate && pip install -e .")
    else:
        print("  ❌ Not found")
        print("     Install:")
        print("       git clone https://github.com/microsoft/fara.git ~/fara")
        print("       cd ~/fara")
        print("       python3 -m venv .venv")
        print("       source .venv/bin/activate")
        print("       pip install -e .")
        print("       playwright install")
    
    print()
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    available = sum(1 for c in checks if c["exists"])
    print(f"\nAvailable CLIs: {available}/2 (+ Fara optional)")
    
    if available >= 1:
        print("\n✅ You can use the orchestrator with available providers.")
        print("\nQuick test:")
        print("  ./mai status")
        print("  ./mai run 'Hello, test message'")
    else:
        print("\n❌ No AI CLIs found. Install at least one to use the orchestrator.")
    
    print()
    
    # Show CLI syntax reference
    print("=" * 60)
    print("CLI Syntax Reference (for customization)")
    print("=" * 60)
    print("""
Claude CLI (claude):
  Non-interactive:  claude -p "prompt"
  With tools:       claude -p "prompt" --allowedTools Bash,Read,Write
  System prompt:    claude -p "prompt" --system-prompt "instructions"
  JSON output:      claude -p "prompt" --output-format json

Gemini CLI (gemini):
  Non-interactive:  gemini -p "prompt"
  With files:       gemini -p "prompt about @./file.txt"
  JSON output:      gemini -p "prompt" --output-format json
  YOLO mode:        gemini -p "prompt" --yolo

Fara-7B (python -m fara.cli):
  Basic task:       python -m fara.cli --task "description" --url "https://..."
  With screenshots: python -m fara.cli --task "..." --screenshot-dir ./screenshots
  Sandbox mode:     python -m fara.cli --task "..." --sandbox
""")


if __name__ == "__main__":
    main()
