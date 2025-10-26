#!/usr/bin/env python3
import subprocess, sys
def run(cmd: list) -> int:
    return subprocess.call(cmd)
