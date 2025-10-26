#!/bin/bash
# Quick verification script for v94 bundle

set -e

echo "================================="
echo "Codex v94 Bundle Verification"
echo "================================="

# Check Python version
echo "Checking Python version..."
python --version

# Check required files
echo ""
echo "Checking required files..."
files=(
    "app.py"
    "glyph_guard_v14.py"
    "glyph_policy.yaml"
    "requirements.txt"
    "Dockerfile"
    "k8s/deployment-hardened.yaml"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file missing"
        exit 1
    fi
done

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Run syntax checks
echo ""
echo "Running syntax checks..."
python -m py_compile app.py
python -m py_compile glyph_guard_v14.py
echo "  ✓ Syntax checks passed"

# Test glyph guard
echo ""
echo "Testing Glyph Guard..."
python glyph_guard_v14.py "safe-test-glyph" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✓ Glyph Guard working"
else
    echo "  ✗ Glyph Guard test failed"
    exit 1
fi

# Check YAML syntax
echo ""
echo "Checking YAML files..."
python -c "import yaml; yaml.safe_load(open('glyph_policy.yaml'))" > /dev/null 2>&1
echo "  ✓ glyph_policy.yaml valid"

python -c "import yaml; yaml.safe_load(open('k8s/deployment-hardened.yaml'))" > /dev/null 2>&1
echo "  ✓ k8s/deployment-hardened.yaml valid"

# Generate SBOM
echo ""
echo "Generating SBOM..."
python generate_sbom.py > /dev/null 2>&1
if [ -f "sbom.json" ]; then
    echo "  ✓ SBOM generated"
else
    echo "  ⚠ SBOM generation failed (non-critical)"
fi

echo ""
echo "================================="
echo "✓ All verification checks passed!"
echo "================================="
echo ""
echo "Bundle is ready for deployment:"
echo "  • docker build -t codex-v94:latest ."
echo "  • kubectl apply -f k8s/deployment-hardened.yaml"
echo "  • helm install codex-v94 ./helm"
