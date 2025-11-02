"""
Test suite for Codex Automation tools
"""
import json
import pytest
from pathlib import Path


def test_tools_exist():
    """Verify that all required tools exist."""
    tools_dir = Path("tools")
    assert tools_dir.exists(), "tools directory should exist"
    
    required_tools = [
        "monetization_verify.py",
        "treasury_split.py",
        "codex_capsule.py"
    ]
    
    for tool in required_tools:
        tool_path = tools_dir / tool
        assert tool_path.exists(), f"{tool} should exist"


def test_required_directories_exist():
    """Verify that all required directories exist."""
    required_dirs = ["tools", "tests", "chain", "examples"]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        assert dir_path.exists(), f"{dir_name} directory should exist"


def test_makefile_exists():
    """Verify that Makefile exists."""
    makefile = Path("Makefile")
    assert makefile.exists(), "Makefile should exist"


def test_requirements_txt_exists():
    """Verify that requirements.txt exists."""
    requirements = Path("requirements.txt")
    assert requirements.exists(), "requirements.txt should exist"


def test_mkdocs_config_exists():
    """Verify that mkdocs.yml exists."""
    mkdocs = Path("mkdocs.yml")
    assert mkdocs.exists(), "mkdocs.yml should exist"


def test_codex_agent_prompt_exists():
    """Verify that CODEX_AGENT_PROMPT.md exists."""
    prompt = Path(".github/CODEX_AGENT_PROMPT.md")
    assert prompt.exists(), "CODEX_AGENT_PROMPT.md should exist"


def test_workflow_exists():
    """Verify that codex_build.yml workflow exists."""
    workflow = Path(".github/workflows/codex_build.yml")
    assert workflow.exists(), "codex_build.yml workflow should exist"


def test_json_files_valid():
    """Test that generated JSON files are valid."""
    json_files = [
        "OMEGA_LOCK.json",
        "FINAL_ATTEST.json",
        "treasury_allocation.json",
        "economy_monetization.json"
    ]
    
    for json_file in json_files:
        file_path = Path(json_file)
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
            assert isinstance(data, dict), f"{json_file} should contain a JSON object"


def test_treasury_allocation_structure():
    """Test treasury allocation has required fields."""
    treasury_file = Path("treasury_allocation.json")
    if treasury_file.exists():
        with open(treasury_file, 'r') as f:
            treasury = json.load(f)
        
        required_fields = ["owner", "reserve", "community"]
        for field in required_fields:
            assert field in treasury, f"treasury_allocation.json should have {field} field"


def test_economy_monetization_structure():
    """Test economy monetization has required fields."""
    economy_file = Path("economy_monetization.json")
    if economy_file.exists():
        with open(economy_file, 'r') as f:
            economy = json.load(f)
        
        required_fields = ["version", "treasury_splits", "policies"]
        for field in required_fields:
            assert field in economy, f"economy_monetization.json should have {field} field"
