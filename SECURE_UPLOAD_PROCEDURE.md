# 🔒 SECURE PyPI UPLOAD PROCEDURE for letta-mcp-server v1.0.3

## 🚨 CRITICAL CONTEXT
**SECURITY INCIDENT**: The PyPI API token was exposed in v1.0.2 and has been revoked.  
**NEW TOKEN**: You have been provided with a new secure token.  
**OBJECTIVE**: Upload v1.0.3 securely without exposing the token.

## ✅ PRE-UPLOAD CHECKLIST

1. **Verify Current Directory**
   ```bash
   pwd
   # Should output: /root/letta-mcp-server-enhanced
   ```

2. **Run Security Audit**
   ```bash
   ./scripts/secure-upload.sh audit
   ```
   ✓ Should show "Security audit passed"

3. **Verify Package Version**
   ```bash
   python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])'
   # Should output: 1.0.3
   ```

4. **Check Distribution Files**
   ```bash
   ls -la dist/
   # Should show:
   # letta_mcp_server-1.0.3-py3-none-any.whl
   # letta_mcp_server-1.0.3.tar.gz
   ```

## 🔐 SECURE UPLOAD STEPS

### Option 1: Using Secure Upload Script (RECOMMENDED)

1. **Set the API Token as Environment Variable**
   ```bash
   export PYPI_API_KEY="pypi-YOUR-TOKEN-HERE"
   ```
   
2. **Verify Token is Set (without exposing it)**
   ```bash
   echo ${PYPI_API_KEY:0:10}...
   # Should show: pypi-XXXXX...
   ```

3. **Run the Secure Upload**
   ```bash
   ./scripts/secure-upload.sh release
   ```
   
4. **Confirm When Prompted**
   - The script will show version 1.0.3
   - Type `yes` when asked to confirm

5. **Clear the Token After Upload**
   ```bash
   unset PYPI_API_KEY
   ```

### Option 2: Using Python Release Script

1. **Set Environment Variable**
   ```bash
   export PYPI_API_KEY="pypi-YOUR-TOKEN-HERE"
   ```

2. **Run Release Script**
   ```bash
   python scripts/release.py --full-release
   ```

3. **Clear Token**
   ```bash
   unset PYPI_API_KEY
   ```

### Option 3: Manual Twine Upload

1. **Set Twine Environment Variables**
   ```bash
   export TWINE_USERNAME="__token__"
   export TWINE_PASSWORD="pypi-YOUR-TOKEN-HERE"
   export TWINE_NON_INTERACTIVE=1
   ```

2. **Upload to PyPI**
   ```bash
   twine upload dist/*
   ```

3. **Clear All Sensitive Variables**
   ```bash
   unset TWINE_PASSWORD
   unset TWINE_USERNAME
   unset TWINE_NON_INTERACTIVE
   ```

## 🔍 POST-UPLOAD VERIFICATION

1. **Check PyPI Page**
   - Visit: https://pypi.org/project/letta-mcp-server/1.0.3/
   - Verify version shows as 1.0.3
   - Check upload timestamp

2. **Test Installation**
   ```bash
   # In a new virtual environment
   python -m venv test_env
   source test_env/bin/activate
   pip install letta-mcp-server==1.0.3
   letta-mcp --help
   ```

3. **Verify No Token Exposure**
   ```bash
   # Download and check the uploaded package
   pip download letta-mcp-server==1.0.3 --no-deps -d /tmp/
   cd /tmp/
   tar -tzf letta_mcp_server-1.0.3.tar.gz | grep -i token
   # Should return nothing
   ```

## 🚨 EMERGENCY PROCEDURES

### If Token is Accidentally Exposed:

1. **IMMEDIATELY** go to https://pypi.org/manage/account/#api-tokens
2. Click "Revoke" on the exposed token
3. Generate a new token
4. Delete any files containing the exposed token
5. Run full security audit: `grep -r "pypi-" . --exclude-dir=.git`

### If Upload Fails:

1. Check error message for specific issue
2. Common issues:
   - Token not set: Ensure PYPI_API_KEY is exported
   - Wrong token format: Must start with "pypi-"
   - Network issues: Retry after a few minutes
   - Version conflict: Check if 1.0.3 already exists

## 📋 FINAL CHECKLIST

- [ ] Token set as environment variable only
- [ ] Security audit passed
- [ ] Version verified as 1.0.3
- [ ] Upload completed successfully
- [ ] PyPI page shows new version
- [ ] Test installation works
- [ ] All sensitive environment variables cleared
- [ ] This document reviewed and followed

## 🎉 SUCCESS INDICATORS

- PyPI shows version 1.0.3 available
- No security warnings or errors
- Installation test passes
- No tokens found in any committed files
- Community can install: `pip install letta-mcp-server`

---

**Remember**: Security is paramount. When in doubt, stop and verify. Never expose tokens!