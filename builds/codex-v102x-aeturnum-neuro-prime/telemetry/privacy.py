import json, re
EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
IP = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
TOKEN = re.compile(r'(?:(?:api|token|secret|key)[:=]\s*)([A-Za-z0-9\-_.=]+)', re.I)

def scrub(o: dict) -> dict:
    s = json.dumps(o, separators=(',', ':'))
    s = EMAIL.sub('[REDACTED_EMAIL]', s)
    s = IP.sub('[REDACTED_IP]', s)
    s = TOKEN.sub('SECRET=[REDACTED]', s)
    return json.loads(s)
