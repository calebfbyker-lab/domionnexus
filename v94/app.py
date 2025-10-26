#!/usr/bin/env python3
"""
Codex v94 - FastAPI Server with JWKS-by-kid verification and Glyph Guard
"""
import os
import json
import hashlib
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
import jwt
from jwt import PyJWKClient
import uvicorn

app = FastAPI(
    title="Codex v94 Sentinel",
    description="Auth hardening + Glyph Guard + Supply Chain Security",
    version="94.0.0"
)

# Configuration
JWKS_URL = os.getenv("JWKS_URL", "")
OIDC_ENABLED = os.getenv("OIDC_ENABLED", "false").lower() == "true"
GLYPH_POLICY_PATH = os.getenv("GLYPH_POLICY_PATH", "glyph_policy.yaml")

# JWKS client for token verification
jwks_client = None
if OIDC_ENABLED and JWKS_URL:
    jwks_client = PyJWKClient(JWKS_URL)

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token using JWKS-by-kid"""
    if not OIDC_ENABLED or not jwks_client:
        return None
    
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "ES256"],
            options={"verify_exp": True}
        )
        return payload
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "94.0.0",
        "features": {
            "oidc_enabled": OIDC_ENABLED,
            "glyph_guard": True,
            "sbom_gating": True,
            "provenance_v4": True
        }
    }

@app.post("/api/glyph/verify")
async def verify_glyph(
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Verify glyph against policy"""
    # Token verification
    if OIDC_ENABLED and authorization:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.split("Bearer ")[1]
        payload = verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Token verification failed")
    
    # Get glyph data
    data = await request.json()
    glyph_text = data.get("glyph", "")
    
    # Verify with glyph guard
    from glyph_guard_v14 import verify_glyph_policy
    result = verify_glyph_policy(glyph_text, GLYPH_POLICY_PATH)
    
    return {
        "verified": result["valid"],
        "policy_version": "v14",
        "details": result
    }

@app.get("/api/provenance/v4")
async def get_provenance():
    """Get provenance v4 information"""
    return {
        "version": "v4",
        "materials": [
            {
                "uri": "pkg:pypi/fastapi@0.104.1",
                "digest": {"sha256": "..."}
            }
        ],
        "builder": {
            "id": "https://github.com/calebfbyker-lab/domionnexus"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=False
    )
