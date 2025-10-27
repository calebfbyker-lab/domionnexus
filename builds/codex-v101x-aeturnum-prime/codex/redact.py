import re, json
RE_EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
RE_IP    = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
RE_TOKEN = re.compile(r'(?:api|token|secret|key)[=:\s]([A-Za-z0-9_\-]{12,})', re.I)
def scrub_obj(o):
    s=json.dumps(o, separators=(',',':'))
    s = RE_EMAIL.sub('[REDACTED_EMAIL]', s)
    s = RE_IP.sub('[REDACTED_IP]', s)
    s = RE_TOKEN.sub('SECRET=[REDACTED]', s)
    return json.loads(s)
