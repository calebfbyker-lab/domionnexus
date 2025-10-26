"""Builder Part 3
Writes Dockerfile, CI workflows and optionally packages the built tree into a zip/tar
"""
import os, argparse, textwrap, shutil, zipfile

def w(root, rel, content):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)

def run(root, package=True, out_zip='/mnt/data/codex-builder-output.zip'):
    w(root, 'Dockerfile', textwrap.dedent('''
    FROM python:3.11-slim
    WORKDIR /app
    ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY . .
    EXPOSE 8000
    USER 65532:65532
    CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8000"]
    '''))

    # basic CI
    w(root, '.github/workflows/ci.yml', textwrap.dedent('''
    name: builder-ci
    on: [push, pull_request]
    jobs:
      build:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-python@v5
            with: { python-version: '3.11' }
          - run: |
              python -m pip install --upgrade pip
              pip install -r requirements.txt
              python scripts/hash_all.py --root . --out codex/manifest.v95x.json
              python scripts/verify_manifest.py --root . --manifest codex/manifest.v95x.json
    '''))

    print('part3: written Dockerfile and CI workflow')

    if package:
        zip_path = out_zip
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            for dp,_,files in os.walk(root):
                for n in files:
                    p = os.path.join(dp,n)
                    z.write(p, os.path.relpath(p, root))
        print('packaged builder output to', zip_path)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default='./build_output'); ap.add_argument('--out', default='/mnt/data/codex-builder-output.zip'); a=ap.parse_args(); run(a.root, out_zip=a.out)
