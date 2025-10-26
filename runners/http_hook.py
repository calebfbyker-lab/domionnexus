#!/usr/bin/env python3
import requests, json
def run(cmd: list) -> int:
    # expects ["http","POST","https://...","{json}"]
    try:
        if len(cmd) >= 4 and cmd[0] == "http":
            method = cmd[1].upper(); url = cmd[2]
            body = json.loads(" ".join(cmd[3:]))
            r = requests.request(method, url, json=body, timeout=10)
            print("http_hook status:", r.status_code)
            return 0 if r.ok else 2
        print("http_hook runner saw:", cmd); return 0
    except Exception as e:
        print("http_hook runner error:", e); return 1
