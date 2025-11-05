#!/usr/bin/env python3
import sys, re, html

def text_snippet(s, maxlen=800):
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) <= maxlen:
        return s
    return s[:maxlen].rsplit(" ",1)[0]+"..."

def extract(input_path, output_path):
    raw = open(input_path, 'rb').read().decode('utf-8', errors='ignore')
    title = ''
    m = re.search(r'<title>(.*?)</title>', raw, flags=re.I|re.S)
    if m:
        title = html.unescape(m.group(1)).strip()

    # Extract code blocks from <pre> or <code> tags
    codes = []
    for m in re.finditer(r'<pre[^>]*>(.*?)</pre>', raw, flags=re.S|re.I):
        inner = m.group(1)
        # remove inner <code> wrapper if present
        inner = re.sub(r'^<code[^>]*>|</code>$','', inner.strip(), flags=re.I)
        txt = re.sub(r'<[^>]+>', '', inner)
        codes.append(('text', html.unescape(txt).rstrip()))

    for m in re.finditer(r'<code[^>]*class=["\']?language-([a-zA-Z0-9_-]+)["\']?[^>]*>(.*?)</code>', raw, flags=re.S|re.I):
        lang = m.group(1)
        txt = re.sub(r'<[^>]+>', '', m.group(2))
        codes.append((lang, html.unescape(txt).rstrip()))

    # Fallback: triple-backtick style in the page
    for m in re.finditer(r'```(\w+)?\n(.*?)```', raw, flags=re.S):
        lang = m.group(1) or 'text'
        codes.append((lang, html.unescape(m.group(2).strip())))

    # Extract visible text for a short summary: pick first paragraphs
    body = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', raw, flags=re.S|re.I)
    body = re.sub(r'<[^>]+>', ' ', body)
    body = html.unescape(body)
    body = re.sub(r'\s+', ' ', body).strip()
    summary = text_snippet(body, maxlen=1200)

    # Build markdown
    out = []
    out.append('# Extracted from link')
    if title:
        out.append('\n**Title:** ' + title + '\n')
    out.append('\n## Short summary\n')
    out.append(summary + '\n')

    out.append('\n## Code snippets\n')
    if not codes:
        out.append('_No code blocks detected._\n')
    else:
        for i, (lang, code) in enumerate(codes, start=1):
            lang = (lang or 'text').lower()
            out.append(f'### Snippet {i} ({lang})\n')
            out.append('```' + lang + '\n' + code + '\n```\n')

    out.append('\n## Suggested follow-ups / integration points\n')
    out.append('- Review code snippets for licenses and sensitive data (PII, API keys).\n')
    out.append('- Identify any runnable scripts and add them under `scripts/` with tests.\n')
    out.append('- If provenance or provenance-like assertions exist, map them to `codex/manifest.*` and `scripts/provenance_v4.py`.\n')
    out.append('- Add anything important to `docs/` and reference in README.\n')

    open(output_path, 'w', encoding='utf-8').write('\n'.join(out))
    print('wrote', output_path)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: extract_link.py <input-html> <output-md>')
        sys.exit(2)
    extract(sys.argv[1], sys.argv[2])
