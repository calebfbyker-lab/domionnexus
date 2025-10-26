#!/usr/bin/env bash
"""
Cosign wrapper for signature verification
"""
import subprocess
import sys
import json
from typing import Optional, Dict, Any

def verify_image_signature(image: str, key_path: Optional[str] = None, 
                          keyless: bool = False) -> Dict[str, Any]:
    """
    Verify container image signature using cosign
    
    Args:
        image: Container image reference (e.g., docker.io/myorg/myimage:tag)
        key_path: Path to public key file
        keyless: Use keyless verification (Fulcio/Rekor)
    
    Returns:
        dict: Verification result with status and details
    """
    cmd = ["cosign", "verify"]
    
    if keyless:
        # Keyless verification (requires OIDC)
        cmd.extend(["--certificate-identity-regexp", ".*", 
                   "--certificate-oidc-issuer-regexp", ".*"])
    elif key_path:
        cmd.extend(["--key", key_path])
    else:
        return {
            "verified": False,
            "error": "Must specify either key_path or keyless=True"
        }
    
    cmd.append(image)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse JSON output
        try:
            verification_data = json.loads(result.stdout)
            return {
                "verified": True,
                "image": image,
                "signatures": verification_data
            }
        except json.JSONDecodeError:
            return {
                "verified": True,
                "image": image,
                "output": result.stdout
            }
            
    except subprocess.CalledProcessError as e:
        return {
            "verified": False,
            "image": image,
            "error": e.stderr or str(e)
        }
    except FileNotFoundError:
        return {
            "verified": False,
            "error": "cosign not installed. Install from: https://github.com/sigstore/cosign"
        }

def verify_blob_signature(blob_path: str, signature_path: str, key_path: str) -> Dict[str, Any]:
    """
    Verify blob signature using cosign
    
    Args:
        blob_path: Path to the blob/artifact
        signature_path: Path to signature file
        key_path: Path to public key
    
    Returns:
        dict: Verification result
    """
    cmd = [
        "cosign", "verify-blob",
        "--key", key_path,
        "--signature", signature_path,
        blob_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        return {
            "verified": True,
            "blob": blob_path,
            "output": result.stdout
        }
        
    except subprocess.CalledProcessError as e:
        return {
            "verified": False,
            "blob": blob_path,
            "error": e.stderr or str(e)
        }
    except FileNotFoundError:
        return {
            "verified": False,
            "error": "cosign not installed"
        }

def main():
    """CLI interface for cosign verification"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cosign verification wrapper")
    parser.add_argument("--image", help="Container image to verify")
    parser.add_argument("--blob", help="Blob/artifact file to verify")
    parser.add_argument("--signature", help="Signature file (for blob verification)")
    parser.add_argument("--key", help="Public key file path")
    parser.add_argument("--keyless", action="store_true", 
                       help="Use keyless verification")
    
    args = parser.parse_args()
    
    if args.image:
        print(f"Verifying image signature: {args.image}")
        result = verify_image_signature(args.image, args.key, args.keyless)
    elif args.blob and args.signature and args.key:
        print(f"Verifying blob signature: {args.blob}")
        result = verify_blob_signature(args.blob, args.signature, args.key)
    else:
        parser.print_help()
        return 1
    
    print(json.dumps(result, indent=2))
    return 0 if result.get("verified") else 1

if __name__ == "__main__":
    sys.exit(main())
