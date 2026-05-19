#!/usr/bin/env python3
"""
Test suite for destructive bash command blocker hook.
"""

import json
import subprocess
import sys
from pathlib import Path

HOOK_PATH = Path(__file__).parent / "pre-tool-use"

def test_hook(command: str, tool_name: str = "bash", should_block: bool = True) -> bool:
    """Test hook with a command and return True if result matches expectation."""
    payload = json.dumps({
        "tool": {
            "name": tool_name,
            "input": {"command": command}
        },
        "project_path": "/test/project"
    })
    
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=5
    )
    
    blocked = result.returncode != 0
    
    if blocked != should_block:
        print(f"❌ FAIL: {command[:60]}")
        print(f"   Expected: {'block' if should_block else 'allow'}, Got: {'block' if blocked else 'allow'}")
        if blocked:
            print(f"   Output: {result.stdout[:200]}")
        return False
    
    print(f"✅ PASS: {command[:60]}")
    return True


def main():
    print("Testing destructive bash command blocker...\n")
    
    tests = [
        # Should block
        ("rm -rf /tmp/data", "bash", True),
        ("rm -rf .", "bash", True),
        ("rm -fr /home/user", "bash", True),
        ("sudo rm -rf /var/log", "bash", True),
        ("DROP TABLE users", "bash", True),
        ("DROP TABLE users;", "bash", True),
        ("git push --force origin main", "bash", True),
        ("git push origin main --force", "bash", True),
        ("TRUNCATE TABLE logs", "bash", True),
        ("DELETE FROM users", "bash", True),
        ("DELETE FROM users;", "bash", True),
        ("echo test && rm -rf /tmp && echo done", "bash", True),
        
        # Should allow
        ("rm file.txt", "bash", False),
        ("rm -f file.txt", "bash", False),
        ("rm -r directory", "bash", False),
        ("git push origin main", "bash", False),
        ("git push --force-with-lease origin main", "bash", False),
        ("DELETE FROM users WHERE id = 1", "bash", False),
        ("SELECT * FROM users", "bash", False),
        ("ls -la", "bash", False),
        ("echo 'DROP TABLE' > file.txt", "bash", False),
        
        # Non-bash tools should always allow
        ("rm -rf /", "file_editor", False),
        ("DROP TABLE users", "python", False),
    ]
    
    passed = 0
    failed = 0
    
    for command, tool, should_block in tests:
        if test_hook(command, tool, should_block):
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        sys.exit(1)
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()
