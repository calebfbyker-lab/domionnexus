"""Orchestrator for the 3-part builder
Usage: python run_builder.py --root ./build_output --until part2
"""
import argparse
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent

def run_until(root, until):
    root = str(root)
    parts = [
        (HERE / 'part1.py'),
        (HERE / 'part2.py'),
        (HERE / 'part3.py'),
    ]
    names = ['part1','part2','part3']
    idx = names.index(until) if until in names else len(names)-1
    for i in range(0, idx+1):
        p = parts[i]
        print(f"running {p.name} -> writing into {root}")
        rc = __import__('runpy').run_path(str(p), init_globals={'__name__': '__main__'}, run_name='__main__')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='./build_output')
    ap.add_argument('--until', choices=['part1','part2','part3'], default='part3')
    a = ap.parse_args()
    # ensure build_output exists
    Path(a.root).mkdir(parents=True, exist_ok=True)
    # run parts sequentially
    # We call them as modules by executing their files; they accept --root but we provide via run
    import subprocess
    for part in ['part1','part2','part3']:
        cmd = [sys.executable, str(HERE / f"{part}.py"), '--root', a.root]
        print('->', ' '.join(cmd))
        res = subprocess.run(cmd)
        if res.returncode != 0:
            print('part failed:', part)
            sys.exit(res.returncode)
        if part == a.until:
            print('stopped at', part)
            break
    print('done')
