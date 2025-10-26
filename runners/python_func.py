#!/usr/bin/env python3
def run(cmd: list) -> int:
    # expects ["python","-c","<code>"] style or simple print substitute
    try:
        if cmd and len(cmd) >= 2 and cmd[0] == "python" and cmd[1] == "-c":
            code = " ".join(cmd[2:])
            exec(code, {})
            return 0
        print("python_func runner saw:", cmd)
        return 0
    except Exception as e:
        print("python_func runner error:", e)
        return 1
