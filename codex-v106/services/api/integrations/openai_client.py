import os
try:
    import openai
except Exception:
    openai = None

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
if openai and OPENAI_KEY:
    openai.api_key = OPENAI_KEY

def chat_completion(prompt: str, model: str = "gpt-4o-mini", max_tokens: int = 512):
    """Return a dict with 'text' and 'meta'. If OpenAI SDK is unavailable or key missing, return a safe mock."""
    if not openai or not OPENAI_KEY:
        return {"text": f"[mock reply] received: {prompt[:200]}", "meta": {"mock": True}}
    resp = openai.ChatCompletion.create(model=model, messages=[{"role": "user", "content": prompt}], max_tokens=max_tokens)
    # Normalize to a simple payload
    txt = ""
    try:
        choices = resp.get("choices") or []
        if choices:
            txt = choices[0].get("message", {}).get("content", "")
    except Exception:
        txt = str(resp)
    return {"text": txt, "meta": {"ok": True}}
