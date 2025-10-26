#!/usr/bin/env python3
"""
telemetry_agent.py - Telemetry and monitoring agent for v93.x
Part of Codex v93.x Constellation bundle
"""
import json
import time
import hashlib
import os
import sys
from datetime import datetime
from pathlib import Path


def collect_metrics():
    """Collect system and application metrics"""
    metrics = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "v93.x",
        "subject_id": "2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a"
    }
    
    # Check if audit log exists
    audit_file = "audit.jsonl"
    if os.path.exists(audit_file):
        try:
            with open(audit_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                metrics["audit_events"] = len(lines)
                if lines:
                    last_event = json.loads(lines[-1])
                    metrics["last_audit_root"] = last_event.get("root", "unknown")
        except Exception as e:
            metrics["audit_error"] = str(e)
    
    # Check manifest
    manifest_file = "codex/manifest.v93x.json"
    if os.path.exists(manifest_file):
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest = json.load(f)
                metrics["manifest_files"] = manifest.get("file_count", 0)
                metrics["manifest_version"] = manifest.get("version", "unknown")
        except Exception as e:
            metrics["manifest_error"] = str(e)
    
    # Check SBOM
    sbom_file = "codex/sbom.spdx.json"
    if os.path.exists(sbom_file):
        metrics["sbom_present"] = True
        metrics["sbom_size"] = os.path.getsize(sbom_file)
    else:
        metrics["sbom_present"] = False
    
    # Check provenance
    provenance_file = "codex/provenance.json"
    if os.path.exists(provenance_file):
        metrics["provenance_present"] = True
        metrics["provenance_size"] = os.path.getsize(provenance_file)
    else:
        metrics["provenance_present"] = False
    
    return metrics


def check_integrity():
    """Check integrity of critical files"""
    integrity = {
        "checked_at": datetime.utcnow().isoformat() + "Z",
        "status": "ok"
    }
    
    critical_files = [
        "app.py",
        "tools/glyph_guard_v13.py",
        "plugins/manifest.json",
        "codex/glyphs/xtgs.yaml"
    ]
    
    issues = []
    for filepath in critical_files:
        if not os.path.exists(filepath):
            issues.append(f"Missing: {filepath}")
    
    if issues:
        integrity["status"] = "degraded"
        integrity["issues"] = issues
    
    integrity["files_checked"] = len(critical_files)
    integrity["files_ok"] = len(critical_files) - len(issues)
    
    return integrity


def report_telemetry():
    """Generate and output telemetry report"""
    report = {
        "telemetry_version": "1.0",
        "bundle": "Codex v93.x Constellation",
        "metrics": collect_metrics(),
        "integrity": check_integrity()
    }
    
    # Write report to file
    output_file = "codex/telemetry.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    
    print(json.dumps(report, indent=2))
    print(f"\n✓ Telemetry report written to {output_file}")
    
    return report


def main():
    """Main telemetry agent entry point"""
    try:
        report = report_telemetry()
        
        # Check for issues
        if report["integrity"]["status"] != "ok":
            print(f"\n⚠ Warning: Integrity check found issues", file=sys.stderr)
            sys.exit(1)
        
        print("\n✓ All telemetry checks passed")
        
    except Exception as e:
        print(f"Error: Telemetry agent failed: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
