#!/usr/bin/env python3
"""
Local shell runner with zero-trust mode
Codex Continuum v100 - Continuum Σ (Sigma)
"""
import subprocess
import sys
import os
import json
import re

# Zero-trust configuration
ALLOWED_COMMANDS = ["echo", "ls", "cat", "grep", "find", "python3", "pip", "git"]
DENIED_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"sudo",
    r"chmod\s+777",
    r"curl.*\|\s*sh",
    r"wget.*\|\s*sh"
]

def check_command_allowed(cmd: list, zero_trust: bool = True) -> bool:
    """Check if command is allowed in zero-trust mode"""
    if not zero_trust:
        return True
    
    if not cmd:
        return False
    
    # Check if base command is in allowed list
    base_cmd = os.path.basename(cmd[0])
    if base_cmd not in ALLOWED_COMMANDS:
        print(f"⛔ Command '{base_cmd}' not in allowed list", file=sys.stderr)
        return False
    
    # Check for denied patterns
    cmd_str = " ".join(cmd)
    for pattern in DENIED_PATTERNS:
        if re.search(pattern, cmd_str, re.IGNORECASE):
            print(f"⛔ Command matches denied pattern: {pattern}", file=sys.stderr)
            return False
    
    return True

def run(cmd: list, zero_trust: bool = True, audit_log: str = None) -> int:
    """
    Run a shell command with optional zero-trust enforcement
    
    Args:
        cmd: Command and arguments as list
        zero_trust: Enable zero-trust mode (default: True)
        audit_log: Optional path to audit log file
    
    Returns:
        Exit code of the command
    """
    # Audit the command
    if audit_log:
        try:
            with open(audit_log, 'a') as f:
                entry = {
                    "runner": "local_shell",
                    "cmd": cmd,
                    "zero_trust": zero_trust,
                    "timestamp": subprocess.check_output(["date", "+%Y-%m-%dT%H:%M:%S"]).decode().strip()
                }
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"⚠️  Audit logging failed: {e}", file=sys.stderr)
    
    # Check if command is allowed
    if not check_command_allowed(cmd, zero_trust):
        return 126  # Command not executable
    
    try:
        result = subprocess.call(cmd)
        return result
    except FileNotFoundError:
        print(f"⛔ Command not found: {cmd[0]}", file=sys.stderr)
        return 127
    except Exception as e:
        print(f"⛔ Error executing command: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: local_shell.py <command> [args...]")
        sys.exit(1)
    
    exit_code = run(sys.argv[1:], zero_trust=True, audit_log="audit.jsonl")
    sys.exit(exit_code)
