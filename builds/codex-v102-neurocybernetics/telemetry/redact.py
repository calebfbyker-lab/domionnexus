import re, json
RE_EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
RE_IP = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
RE_PID = re.compile(r'("name"|"phone"|"address"\s*:)".*?"', re.I)
def scrub(o: dict)->dict:
    s=json.dumps(o, separators=(',',':'))
    s=RE_EMAIL.sub('[REDACTED_EMAIL]', s)
    s=RE_IP.sub('[REDACTED_IP]', s)
    s=RE_PID.sub('\1"[REDACTED]"', s)
    return json.loads(s)
