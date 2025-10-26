#!/usr/bin/env python3
"""
Sandbox runner with container isolation
Codex Continuum v100 - Continuum Σ (Sigma)
"""
import subprocess
import sys
import json
import tempfile
import os

def run(cmd: list, image: str = "python:3.11-slim", network: str = "none", audit_log: str = None) -> int:
    """
    Run a command in a sandboxed container
    
    Args:
        cmd: Command and arguments as list
        image: Docker image to use
        network: Network mode (none, bridge, host)
        audit_log: Optional path to audit log file
    
    Returns:
        Exit code of the command
    """
    # Audit the command
    if audit_log:
        try:
            with open(audit_log, 'a') as f:
                entry = {
                    "runner": "sandbox",
                    "cmd": cmd,
                    "image": image,
                    "network": network,
                    "timestamp": subprocess.check_output(["date", "+%Y-%m-%dT%H:%M:%S"]).decode().strip()
                }
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"⚠️  Audit logging failed: {e}", file=sys.stderr)
    
    # Check if Docker/Podman is available
    container_runtime = None
    for runtime in ["docker", "podman"]:
        try:
            subprocess.check_output([runtime, "--version"], stderr=subprocess.DEVNULL)
            container_runtime = runtime
            break
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    
    if not container_runtime:
        print("⛔ No container runtime (docker/podman) found. Running in fallback mode.", file=sys.stderr)
        print("🔄 Executing command directly (not sandboxed):", cmd)
        return subprocess.call(cmd)
    
    # Build container command
    container_cmd = [
        container_runtime, "run",
        "--rm",
        "--network", network,
        "--security-opt", "no-new-privileges",
        "--cap-drop", "ALL",
        image
    ] + cmd
    
    print(f"🔒 Running in sandbox: {' '.join(cmd)}")
    try:
        result = subprocess.call(container_cmd)
        return result
    except Exception as e:
        print(f"⛔ Sandbox execution failed: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sandbox.py <command> [args...]")
        sys.exit(1)
    
    exit_code = run(sys.argv[1:], audit_log="audit.jsonl")
    sys.exit(exit_code)
