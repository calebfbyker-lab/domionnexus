"""
Shadow Deploy Metrics - Track canary deployments and auto-rollback
"""
import json
import os
import time
from pathlib import Path

METRICS_FILE = "rollout/shadow_metrics.json"
ROLLBACK_THRESHOLD = 0.05  # 5% error rate triggers rollback


class ShadowMetrics:
    """Track shadow deployment metrics for auto-rollback decisions"""
    
    def __init__(self, metrics_file=METRICS_FILE):
        self.metrics_file = metrics_file
        self.data = self._load_metrics()
    
    def _load_metrics(self):
        """Load metrics from disk"""
        if not os.path.exists(self.metrics_file):
            return {
                "deployments": {},
                "current_deployment": None
            }
        
        try:
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {
                "deployments": {},
                "current_deployment": None
            }
    
    def _save_metrics(self):
        """Save metrics to disk"""
        os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
        with open(self.metrics_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def start_deployment(self, deployment_id, version, initial_percent=5):
        """Start tracking a new shadow deployment"""
        self.data["current_deployment"] = deployment_id
        self.data["deployments"][deployment_id] = {
            "deployment_id": deployment_id,
            "version": version,
            "started_at": int(time.time()),
            "state": "canary",
            "percent": initial_percent,
            "requests": {
                "total": 0,
                "success": 0,
                "errors": 0,
                "timeouts": 0
            },
            "health_checks": {
                "passed": 0,
                "failed": 0
            },
            "error_rate": 0.0,
            "rollback_triggered": False
        }
        self._save_metrics()
        return self.data["deployments"][deployment_id]
    
    def record_request(self, deployment_id, success=True, duration_ms=None):
        """Record a request to shadow deployment"""
        if deployment_id not in self.data["deployments"]:
            return False
        
        dep = self.data["deployments"][deployment_id]
        dep["requests"]["total"] += 1
        
        if success:
            dep["requests"]["success"] += 1
        else:
            dep["requests"]["errors"] += 1
        
        # Calculate error rate
        total = dep["requests"]["total"]
        if total > 0:
            dep["error_rate"] = dep["requests"]["errors"] / total
        
        self._save_metrics()
        return True
    
    def record_health_check(self, deployment_id, passed=True):
        """Record a health check result"""
        if deployment_id not in self.data["deployments"]:
            return False
        
        dep = self.data["deployments"][deployment_id]
        if passed:
            dep["health_checks"]["passed"] += 1
        else:
            dep["health_checks"]["failed"] += 1
        
        self._save_metrics()
        return True
    
    def should_rollback(self, deployment_id):
        """
        Check if deployment should be rolled back based on metrics
        
        Returns:
            tuple: (should_rollback: bool, reason: str)
        """
        if deployment_id not in self.data["deployments"]:
            return False, "Deployment not found"
        
        dep = self.data["deployments"][deployment_id]
        
        # Check error rate
        if dep["error_rate"] > ROLLBACK_THRESHOLD:
            return True, f"Error rate {dep['error_rate']:.2%} exceeds threshold {ROLLBACK_THRESHOLD:.2%}"
        
        # Check health checks
        health_total = dep["health_checks"]["passed"] + dep["health_checks"]["failed"]
        if health_total >= 3:  # Need at least 3 checks
            fail_rate = dep["health_checks"]["failed"] / health_total
            if fail_rate > 0.5:  # More than 50% failing
                return True, f"Health check failure rate {fail_rate:.2%} too high"
        
        return False, "Metrics within acceptable range"
    
    def advance_deployment(self, deployment_id, new_percent):
        """Advance deployment to higher traffic percentage"""
        if deployment_id not in self.data["deployments"]:
            return False
        
        dep = self.data["deployments"][deployment_id]
        dep["percent"] = min(100, new_percent)
        
        if dep["percent"] >= 100:
            dep["state"] = "complete"
            dep["completed_at"] = int(time.time())
        
        self._save_metrics()
        return True
    
    def trigger_rollback(self, deployment_id, reason):
        """Trigger rollback for a deployment"""
        if deployment_id not in self.data["deployments"]:
            return False
        
        dep = self.data["deployments"][deployment_id]
        dep["rollback_triggered"] = True
        dep["rollback_reason"] = reason
        dep["rollback_at"] = int(time.time())
        dep["state"] = "rolled_back"
        
        self._save_metrics()
        return True
    
    def get_current_deployment(self):
        """Get current active deployment metrics"""
        current_id = self.data.get("current_deployment")
        if not current_id or current_id not in self.data["deployments"]:
            return None
        return self.data["deployments"][current_id]
    
    def get_deployment(self, deployment_id):
        """Get specific deployment metrics"""
        return self.data["deployments"].get(deployment_id)
    
    def list_deployments(self, limit=10):
        """List recent deployments"""
        deps = list(self.data["deployments"].values())
        # Sort by started_at descending
        deps.sort(key=lambda d: d.get("started_at", 0), reverse=True)
        return deps[:limit]


def check_and_rollback():
    """Check current deployment and auto-rollback if needed"""
    metrics = ShadowMetrics()
    current = metrics.get_current_deployment()
    
    if not current:
        print("No active deployment")
        return
    
    deployment_id = current["deployment_id"]
    should_rb, reason = metrics.should_rollback(deployment_id)
    
    if should_rb:
        print(f"⚠️  AUTO-ROLLBACK TRIGGERED: {reason}")
        metrics.trigger_rollback(deployment_id, reason)
        print(f"✓ Deployment {deployment_id} rolled back")
    else:
        print(f"✓ Deployment {deployment_id} metrics healthy: {reason}")


if __name__ == "__main__":
    check_and_rollback()
