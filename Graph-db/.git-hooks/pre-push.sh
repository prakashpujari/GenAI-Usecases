#!/bin/bash

# Pre-push hook to validate before deployment
# Copy to .git/hooks/pre-push and make executable: chmod +x .git/hooks/pre-push

echo "🔍 Running pre-push validation..."

# Check if we're pushing to main
BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$BRANCH" == "main" ]; then
    echo "📤 Pushing to main branch - running validation checks..."

    # Check 1: Ensure no uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        echo "❌ ERROR: You have uncommitted changes. Please commit or stash them."
        exit 1
    fi

    # Check 2: Verify render.yaml is valid YAML
    if command -v yamllint &> /dev/null; then
        echo "✓ Validating render.yaml..."
        if ! yamllint render.yaml; then
            echo "❌ ERROR: Invalid render.yaml syntax"
            exit 1
        fi
    fi

    # Check 3: Verify backend requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        echo "❌ ERROR: requirements.txt not found"
        exit 1
    fi

    # Check 4: Verify frontend package.json exists
    if [ ! -f "frontend/package.json" ]; then
        echo "❌ ERROR: frontend/package.json not found"
        exit 1
    fi

    # Check 5: Optional - run tests if they exist
    if [ -d "tests" ]; then
        echo "🧪 Running tests..."
        if command -v pytest &> /dev/null; then
            if ! pytest -q; then
                echo "❌ ERROR: Tests failed"
                exit 1
            fi
        fi
    fi

    echo "✅ All checks passed!"
    echo "🚀 Ready to deploy to Render on push"
fi

exit 0
