"""
TUF-lite Metadata Manager for Codex v98 Orthos
Lightweight implementation of The Update Framework for artifact distribution
"""
import json
import os
import time
import hashlib
from pathlib import Path

METADATA_DIR = "tuf/metadata"
TARGETS_DIR = "tuf/targets"


class TUFLite:
    """Lightweight TUF implementation for secure artifact distribution"""
    
    def __init__(self, metadata_dir=METADATA_DIR, targets_dir=TARGETS_DIR):
        self.metadata_dir = metadata_dir
        self.targets_dir = targets_dir
        os.makedirs(metadata_dir, exist_ok=True)
        os.makedirs(targets_dir, exist_ok=True)
    
    def _calculate_hash(self, filepath):
        """Calculate SHA256 hash of file"""
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def _get_file_size(self, filepath):
        """Get file size in bytes"""
        return os.path.getsize(filepath)
    
    def create_root_metadata(self, version=1):
        """Create root metadata (trust anchor)"""
        root = {
            "_type": "root",
            "spec_version": "1.0.0-lite",
            "version": version,
            "expires": int(time.time()) + (365 * 86400),  # 1 year
            "consistent_snapshot": False,
            "keys": {
                "root-key-1": {
                    "keytype": "ed25519",
                    "scheme": "ed25519",
                    "keyval": {
                        "public": "PLACEHOLDER_PUBLIC_KEY"
                    }
                }
            },
            "roles": {
                "root": {
                    "keyids": ["root-key-1"],
                    "threshold": 1
                },
                "targets": {
                    "keyids": ["root-key-1"],
                    "threshold": 1
                },
                "snapshot": {
                    "keyids": ["root-key-1"],
                    "threshold": 1
                },
                "timestamp": {
                    "keyids": ["root-key-1"],
                    "threshold": 1
                }
            }
        }
        
        root_path = os.path.join(self.metadata_dir, "root.json")
        with open(root_path, 'w') as f:
            json.dump(root, f, indent=2)
        
        return root
    
    def create_targets_metadata(self, version=1):
        """Create targets metadata (list of available artifacts)"""
        targets = {
            "_type": "targets",
            "spec_version": "1.0.0-lite",
            "version": version,
            "expires": int(time.time()) + (90 * 86400),  # 90 days
            "targets": {}
        }
        
        # Scan targets directory
        if os.path.exists(self.targets_dir):
            for filename in os.listdir(self.targets_dir):
                filepath = os.path.join(self.targets_dir, filename)
                if os.path.isfile(filepath):
                    targets["targets"][filename] = {
                        "length": self._get_file_size(filepath),
                        "hashes": {
                            "sha256": self._calculate_hash(filepath)
                        },
                        "custom": {
                            "added_at": int(time.time())
                        }
                    }
        
        targets_path = os.path.join(self.metadata_dir, "targets.json")
        with open(targets_path, 'w') as f:
            json.dump(targets, f, indent=2)
        
        return targets
    
    def create_snapshot_metadata(self, version=1):
        """Create snapshot metadata (hash of targets metadata)"""
        targets_path = os.path.join(self.metadata_dir, "targets.json")
        
        snapshot = {
            "_type": "snapshot",
            "spec_version": "1.0.0-lite",
            "version": version,
            "expires": int(time.time()) + (7 * 86400),  # 7 days
            "meta": {
                "targets.json": {
                    "version": version
                }
            }
        }
        
        if os.path.exists(targets_path):
            snapshot["meta"]["targets.json"]["hashes"] = {
                "sha256": self._calculate_hash(targets_path)
            }
            snapshot["meta"]["targets.json"]["length"] = self._get_file_size(targets_path)
        
        snapshot_path = os.path.join(self.metadata_dir, "snapshot.json")
        with open(snapshot_path, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        return snapshot
    
    def create_timestamp_metadata(self, version=1):
        """Create timestamp metadata (hash of snapshot, updated frequently)"""
        snapshot_path = os.path.join(self.metadata_dir, "snapshot.json")
        
        timestamp = {
            "_type": "timestamp",
            "spec_version": "1.0.0-lite",
            "version": version,
            "expires": int(time.time()) + (1 * 86400),  # 1 day
            "meta": {
                "snapshot.json": {
                    "version": version
                }
            }
        }
        
        if os.path.exists(snapshot_path):
            timestamp["meta"]["snapshot.json"]["hashes"] = {
                "sha256": self._calculate_hash(snapshot_path)
            }
            timestamp["meta"]["snapshot.json"]["length"] = self._get_file_size(snapshot_path)
        
        timestamp_path = os.path.join(self.metadata_dir, "timestamp.json")
        with open(timestamp_path, 'w') as f:
            json.dump(timestamp, f, indent=2)
        
        return timestamp
    
    def add_target(self, filepath, target_name=None):
        """Add a target artifact"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if target_name is None:
            target_name = os.path.basename(filepath)
        
        target_path = os.path.join(self.targets_dir, target_name)
        
        # Copy file to targets directory
        import shutil
        shutil.copy2(filepath, target_path)
        
        return target_name
    
    def update_metadata(self):
        """Update all metadata files"""
        # Get current version from timestamp if it exists
        timestamp_path = os.path.join(self.metadata_dir, "timestamp.json")
        version = 1
        if os.path.exists(timestamp_path):
            with open(timestamp_path, 'r') as f:
                ts = json.load(f)
                version = ts.get("version", 0) + 1
        
        # Update in order: root, targets, snapshot, timestamp
        self.create_root_metadata(version)
        self.create_targets_metadata(version)
        self.create_snapshot_metadata(version)
        self.create_timestamp_metadata(version)
        
        return version
    
    def verify_target(self, target_name):
        """Verify a target artifact against metadata"""
        targets_path = os.path.join(self.metadata_dir, "targets.json")
        if not os.path.exists(targets_path):
            return False, "Targets metadata not found"
        
        with open(targets_path, 'r') as f:
            targets = json.load(f)
        
        if target_name not in targets.get("targets", {}):
            return False, f"Target '{target_name}' not in metadata"
        
        target_meta = targets["targets"][target_name]
        target_path = os.path.join(self.targets_dir, target_name)
        
        if not os.path.exists(target_path):
            return False, f"Target file not found: {target_path}"
        
        # Verify hash
        expected_hash = target_meta["hashes"]["sha256"]
        actual_hash = self._calculate_hash(target_path)
        
        if expected_hash != actual_hash:
            return False, f"Hash mismatch: expected {expected_hash}, got {actual_hash}"
        
        # Verify size
        expected_size = target_meta["length"]
        actual_size = self._get_file_size(target_path)
        
        if expected_size != actual_size:
            return False, f"Size mismatch: expected {expected_size}, got {actual_size}"
        
        return True, "Target verified successfully"
    
    def list_targets(self):
        """List all targets in metadata"""
        targets_path = os.path.join(self.metadata_dir, "targets.json")
        if not os.path.exists(targets_path):
            return []
        
        with open(targets_path, 'r') as f:
            targets = json.load(f)
        
        return list(targets.get("targets", {}).keys())
    
    def get_metadata_info(self):
        """Get info about all metadata files"""
        info = {}
        
        for meta_file in ["root.json", "targets.json", "snapshot.json", "timestamp.json"]:
            path = os.path.join(self.metadata_dir, meta_file)
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                info[meta_file] = {
                    "version": data.get("version"),
                    "expires": data.get("expires"),
                    "type": data.get("_type")
                }
        
        return info


def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python tuf_lite.py <command>")
        print("Commands: init, update, add <file>, verify <target>, list")
        sys.exit(1)
    
    tuf = TUFLite()
    command = sys.argv[1]
    
    if command == "init":
        tuf.update_metadata()
        print("✓ TUF metadata initialized")
    
    elif command == "update":
        version = tuf.update_metadata()
        print(f"✓ TUF metadata updated to version {version}")
    
    elif command == "add" and len(sys.argv) > 2:
        filepath = sys.argv[2]
        target_name = tuf.add_target(filepath)
        tuf.update_metadata()
        print(f"✓ Added target: {target_name}")
    
    elif command == "verify" and len(sys.argv) > 2:
        target_name = sys.argv[2]
        ok, msg = tuf.verify_target(target_name)
        print("✓" if ok else "✗", msg)
        sys.exit(0 if ok else 1)
    
    elif command == "list":
        targets = tuf.list_targets()
        print(f"Targets ({len(targets)}):")
        for t in targets:
            print(f"  - {t}")
    
    elif command == "info":
        info = tuf.get_metadata_info()
        print(json.dumps(info, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
