#!/usr/bin/env python3
"""
Ingest Site Script - v18 Continuum Layer

This stub script:
1. Reads config/domains.json
2. Hashes existing data in data/sites/
"""

import json
import hashlib
import os
from pathlib import Path


def load_domains_config(config_path="config/domains.json"):
    """Load the domains configuration from JSON file."""
    with open(config_path, 'r') as f:
        return json.load(f)


def hash_file(filepath):
    """Generate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read file in chunks to handle large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def hash_sites_directory(sites_dir="data/sites"):
    """
    Hash all files in the data/sites/ directory.
    
    Returns a dictionary mapping file paths to their SHA-256 hashes.
    """
    sites_path = Path(sites_dir)
    hashes = {}
    
    if not sites_path.exists():
        print(f"Directory {sites_dir} does not exist yet.")
        return hashes
    
    # Recursively find all files
    for filepath in sites_path.rglob('*'):
        if filepath.is_file():
            relative_path = str(filepath.relative_to(sites_path))
            file_hash = hash_file(filepath)
            hashes[relative_path] = file_hash
            print(f"Hashed {relative_path}: {file_hash}")
    
    return hashes


def main():
    """Main entry point for the ingest site script."""
    print("=" * 60)
    print("Domion Nexus - Ingest Site Script")
    print("v18 Continuum Layer")
    print("=" * 60)
    
    # Load domains configuration
    print("\nLoading domains configuration...")
    try:
        config = load_domains_config()
        sources = config.get("sources", [])
        print(f"Found {len(sources)} source(s):")
        for source in sources:
            print(f"  - {source['id']}: {source['base']} ({source['kind']})")
    except FileNotFoundError:
        print("ERROR: config/domains.json not found!")
        return 1
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in config/domains.json: {e}")
        return 1
    
    # Hash existing data/sites/ directory
    print("\nHashing data/sites/ directory...")
    hashes = hash_sites_directory()
    
    if hashes:
        print(f"\nTotal files hashed: {len(hashes)}")
    else:
        print("\nNo files found in data/sites/ directory.")
    
    print("\n" + "=" * 60)
    print("Ingest complete.")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())
