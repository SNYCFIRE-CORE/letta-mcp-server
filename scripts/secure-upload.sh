#!/bin/bash
# Secure PyPI Upload Script for letta-mcp-server
# This script ensures safe upload without exposing API tokens

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Secure PyPI Upload Script ===${NC}"
echo

# Function to check if API token is set
check_api_token() {
    if [ -z "${PYPI_API_KEY:-}" ]; then
        echo -e "${RED}ERROR: PYPI_API_KEY environment variable not set${NC}"
        echo
        echo "To set it securely:"
        echo "  export PYPI_API_KEY='your-pypi-token-here'"
        echo
        echo "IMPORTANT: Never commit this token to git!"
        exit 1
    fi
    
    # Validate token format
    if [[ ! "$PYPI_API_KEY" =~ ^pypi- ]]; then
        echo -e "${YELLOW}WARNING: API key doesn't start with 'pypi-'${NC}"
        echo "Make sure you're using a PyPI API token, not a password"
    fi
}

# Function to perform security audit
security_audit() {
    echo -e "${YELLOW}Running security audit...${NC}"
    
    # Check for API tokens in source
    echo "Checking for exposed tokens in source code..."
    if grep -r "pypi-" . --exclude-dir=.git --exclude-dir=.venv --exclude-dir=node_modules --exclude="*.log" 2>/dev/null | grep -v "^Binary file" | grep -v "# " | grep -v "scripts/secure-upload.sh"; then
        echo -e "${RED}CRITICAL: Found potential API tokens in source!${NC}"
        echo "Please remove them before continuing"
        exit 1
    fi
    
    # Check distribution contents
    echo "Checking distribution contents..."
    if [ -f "dist/*.tar.gz" ]; then
        tar -tzf dist/*.tar.gz | grep -E "(\.env|\.pypirc|auth\.toml|token|secret)" && {
            echo -e "${RED}CRITICAL: Sensitive files found in distribution!${NC}"
            exit 1
        } || echo -e "${GREEN}✓ No sensitive files in distribution${NC}"
    fi
    
    echo -e "${GREEN}✓ Security audit passed${NC}"
    echo
}

# Function to build package
build_package() {
    echo -e "${YELLOW}Building package...${NC}"
    
    # Clean previous builds
    rm -rf dist/ build/ *.egg-info
    
    # Build with python -m build
    python -m build
    
    echo -e "${GREEN}✓ Package built successfully${NC}"
    echo
}

# Function to validate package
validate_package() {
    echo -e "${YELLOW}Validating package...${NC}"
    
    # Check with twine
    twine check dist/*
    
    echo -e "${GREEN}✓ Package validation passed${NC}"
    echo
}

# Function to upload to PyPI
upload_to_pypi() {
    local repo="${1:-pypi}"
    
    echo -e "${YELLOW}Uploading to $repo...${NC}"
    
    # Set environment variables for twine
    export TWINE_USERNAME="__token__"
    export TWINE_PASSWORD="$PYPI_API_KEY"
    export TWINE_NON_INTERACTIVE=1
    
    if [ "$repo" = "testpypi" ]; then
        twine upload --repository testpypi dist/*
    else
        twine upload dist/*
    fi
    
    # Clear sensitive environment variables
    unset TWINE_PASSWORD
    
    echo -e "${GREEN}✓ Successfully uploaded to $repo${NC}"
    echo
}

# Main execution
main() {
    # Parse arguments
    local action="${1:-help}"
    
    case "$action" in
        build)
            security_audit
            build_package
            validate_package
            ;;
        test)
            check_api_token
            security_audit
            build_package
            validate_package
            upload_to_pypi testpypi
            ;;
        release)
            check_api_token
            security_audit
            build_package
            validate_package
            
            # Final confirmation
            echo -e "${YELLOW}Ready to upload to PyPI (production)${NC}"
            echo "Version: $(python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')"
            echo
            read -p "Are you sure you want to upload to PyPI? (yes/no): " confirm
            
            if [ "$confirm" = "yes" ]; then
                upload_to_pypi pypi
                echo -e "${GREEN}🎉 Release complete!${NC}"
            else
                echo -e "${YELLOW}Upload cancelled${NC}"
            fi
            ;;
        audit)
            security_audit
            ;;
        help|*)
            echo "Usage: $0 [build|test|release|audit|help]"
            echo
            echo "Commands:"
            echo "  build    - Build and validate package only"
            echo "  test     - Build and upload to TestPyPI"
            echo "  release  - Build and upload to PyPI (production)"
            echo "  audit    - Run security audit only"
            echo "  help     - Show this help message"
            echo
            echo "Environment variables:"
            echo "  PYPI_API_KEY - Your PyPI API token (required for test/release)"
            echo
            echo "Example:"
            echo "  export PYPI_API_KEY='pypi-...'"
            echo "  $0 release"
            ;;
    esac
}

# Run main function
main "$@"