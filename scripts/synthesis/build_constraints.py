#!/usr/bin/env python3
"""
UCSE Build Constraints Script
Builds constraint graph from rule families for deterministic evaluation.
v27.77 - sparse synthesis of multi-domain rule families
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class Constraint:
    constraint_id: str
    family_id: str
    type: str
    expression: str
    severity: str
    priority: int = 0


class ConstraintBuilder:
    """Builds unified constraint graph from all rule families."""
    
    def __init__(self, families_dir: str = "families", config_file: str = "config/ucse_heuristics.json"):
        self.families_dir = Path(families_dir)
        self.config_file = Path(config_file)
        self.constraints: List[Constraint] = []
        self.config: Dict[str, Any] = {}
        
    def load_config(self) -> None:
        """Load UCSE configuration."""
        with open(self.config_file) as f:
            self.config = json.load(f)
        print(f"✓ Loaded configuration from {self.config_file}")
        
    def load_families(self) -> List[Dict[str, Any]]:
        """Load all rule family definitions."""
        families = []
        for family_file in self.families_dir.glob("*.json"):
            with open(family_file) as f:
                family = json.load(f)
                families.append(family)
                print(f"✓ Loaded family: {family['family_id']}")
        return families
    
    def extract_constraints(self, families: List[Dict[str, Any]]) -> None:
        """Extract constraints from all families."""
        for family in families:
            family_id = family['family_id']
            
            # Extract rule-based constraints
            for rule in family.get('rules', []):
                if rule['type'] in ['constraint', 'validation']:
                    constraint = Constraint(
                        constraint_id=f"{family_id}_{rule['rule_id']}",
                        family_id=family_id,
                        type=rule['type'],
                        expression=str(rule.get('condition', {})),
                        severity="error",
                        priority=rule['priority']
                    )
                    self.constraints.append(constraint)
            
            # Extract explicit constraints
            for constraint_def in family.get('constraints', []):
                constraint = Constraint(
                    constraint_id=f"{family_id}_{constraint_def['constraint_id']}",
                    family_id=family_id,
                    type=constraint_def['type'],
                    expression=constraint_def['expression'],
                    severity=constraint_def['severity'],
                    priority=900  # High priority for explicit constraints
                )
                self.constraints.append(constraint)
        
        # Sort by priority (descending)
        self.constraints.sort(key=lambda c: c.priority, reverse=True)
        print(f"✓ Extracted {len(self.constraints)} constraints")
    
    def build_graph(self) -> Dict[str, Any]:
        """Build constraint dependency graph."""
        graph = {
            "metadata": {
                "version": self.config.get('ucse_config', {}).get('version', '27.77'),
                "total_constraints": len(self.constraints),
                "evaluation_mode": "deterministic",
                "built_at": "2025-10-23T00:00:00Z"
            },
            "constraints": [asdict(c) for c in self.constraints],
            "dependencies": self._analyze_dependencies()
        }
        return graph
    
    def _analyze_dependencies(self) -> Dict[str, List[str]]:
        """Analyze constraint dependencies for deterministic ordering."""
        # Simple dependency analysis - can be enhanced
        dependencies = {}
        for constraint in self.constraints:
            dependencies[constraint.constraint_id] = []
        return dependencies
    
    def save_graph(self, output_file: str = "config/constraint_graph.json") -> None:
        """Save constraint graph to file."""
        graph = self.build_graph()
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(graph, f, indent=2)
        
        print(f"✓ Saved constraint graph to {output_path}")
        print(f"  Total constraints: {graph['metadata']['total_constraints']}")
    
    def run(self) -> int:
        """Execute constraint building process."""
        try:
            print("=" * 60)
            print("UCSE Constraint Builder v27.77")
            print("Sparse synthesis of multi-domain rule families")
            print("=" * 60)
            
            self.load_config()
            families = self.load_families()
            self.extract_constraints(families)
            self.save_graph()
            
            print("=" * 60)
            print("✓ Constraint graph built successfully")
            print("=" * 60)
            return 0
            
        except Exception as e:
            print(f"✗ Error building constraints: {e}", file=sys.stderr)
            return 1


def main():
    builder = ConstraintBuilder()
    return builder.run()


if __name__ == "__main__":
    sys.exit(main())
