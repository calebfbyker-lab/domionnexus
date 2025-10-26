#!/usr/bin/env python3
import os, base64, hmac, hashlib
key = os.getenv('CODEX_HMAC_KEY','dev-hmac').encode()
body = open('policy/runtime.json','rb').read()
sig = base64.urlsafe_b64encode(hmac.new(key, body, hashlib.sha256).digest()).decode().rstrip('=')
open('policy/runtime.sig','w').write(sig)
print('policy/runtime.sig written')
