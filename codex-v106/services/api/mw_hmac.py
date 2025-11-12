import base64, hmac, hashlib, json
def sign(spec:dict, key:str)->str:
  body=json.dumps(spec, separators=(",",":")).encode()
  return base64.urlsafe_b64encode(hmac.new(key.encode(), body, hashlib.sha256).digest()).decode().rstrip("=")
