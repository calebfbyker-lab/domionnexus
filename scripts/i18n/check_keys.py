#!/usr/bin/env python3
"""
i18n Key Checker for Codex Immortal v26.0
Validates i18n translation files for consistency and completeness.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Set, List


def load_i18n_file(filepath: Path) -> Dict:
    """Load an i18n JSON file."""
    if not filepath.exists():
        print(f"❌ File not found: {filepath}", file=sys.stderr)
        return {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_all_keys(obj: Dict, prefix: str = "") -> Set[str]:
    """
    Recursively get all keys from a nested dictionary.
    
    Args:
        obj: Dictionary to extract keys from
        prefix: Key prefix for nested objects
    
    Returns:
        set: All flattened keys
    """
    keys = set()
    
    for key, value in obj.items():
        full_key = f"{prefix}.{key}" if prefix else key
        
        if isinstance(value, dict):
            keys.update(get_all_keys(value, full_key))
        else:
            keys.add(full_key)
    
    return keys


def compare_translations(reference: Dict, translation: Dict, lang: str) -> Dict:
    """
    Compare translation files against a reference.
    
    Args:
        reference: Reference translation (e.g., en.json)
        translation: Translation to check
        lang: Language code
    
    Returns:
        dict: Comparison result
    """
    ref_keys = get_all_keys(reference)
    trans_keys = get_all_keys(translation)
    
    missing_keys = ref_keys - trans_keys
    extra_keys = trans_keys - ref_keys
    
    return {
        "language": lang,
        "total_keys": len(ref_keys),
        "translated_keys": len(trans_keys),
        "missing_keys": sorted(list(missing_keys)),
        "extra_keys": sorted(list(extra_keys)),
        "coverage": len(trans_keys) / len(ref_keys) if ref_keys else 0
    }


def main():
    """Main entry point for i18n key checking."""
    print("=" * 60)
    print("i18n Translation Key Checker")
    print("=" * 60)
    
    i18n_dir = Path(__file__).parent.parent.parent / "i18n"
    
    # Load reference translation (English)
    en_path = i18n_dir / "en.json"
    en_data = load_i18n_file(en_path)
    
    if not en_data:
        print("❌ Failed to load reference translation (en.json)")
        return 1
    
    print(f"\n✅ Loaded reference: en.json")
    print(f"   Total keys: {len(get_all_keys(en_data))}")
    
    # Find all translation files
    translation_files = [f for f in i18n_dir.glob("*.json") if f.name != "en.json"]
    
    if not translation_files:
        print("\n⚠️  No translation files found (besides en.json)")
        return 0
    
    print(f"\n📊 Checking {len(translation_files)} translation(s):")
    
    all_results = []
    has_issues = False
    
    for trans_file in translation_files:
        lang = trans_file.stem
        trans_data = load_i18n_file(trans_file)
        
        print(f"\n   🌍 {lang}.json")
        
        result = compare_translations(en_data, trans_data, lang)
        all_results.append(result)
        
        print(f"      Coverage: {result['coverage']:.1%}")
        print(f"      Translated: {result['translated_keys']}/{result['total_keys']}")
        
        if result['missing_keys']:
            has_issues = True
            print(f"      ⚠️  Missing {len(result['missing_keys'])} key(s):")
            for key in result['missing_keys'][:5]:  # Show first 5
                print(f"         - {key}")
            if len(result['missing_keys']) > 5:
                print(f"         ... and {len(result['missing_keys']) - 5} more")
        
        if result['extra_keys']:
            has_issues = True
            print(f"      ⚠️  Extra {len(result['extra_keys'])} key(s):")
            for key in result['extra_keys'][:5]:  # Show first 5
                print(f"         - {key}")
            if len(result['extra_keys']) > 5:
                print(f"         ... and {len(result['extra_keys']) - 5} more")
        
        if not result['missing_keys'] and not result['extra_keys']:
            print(f"      ✅ All keys match!")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    avg_coverage = sum(r['coverage'] for r in all_results) / len(all_results) if all_results else 0
    print(f"\n📊 Average coverage: {avg_coverage:.1%}")
    
    if not has_issues:
        print("\n✅ All translations are complete and consistent!")
        return 0
    else:
        print("\n⚠️  Some translations have missing or extra keys")
        print("   Update translation files to match en.json")
        return 1


if __name__ == "__main__":
    sys.exit(main())
