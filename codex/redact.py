import re
RE_EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
RE_IP = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
def redact(s: str)->str:
    s = RE_EMAIL.sub('[REDACTED_EMAIL]', s)
    s = RE_IP.sub('[REDACTED_IP]', s)
    return s
