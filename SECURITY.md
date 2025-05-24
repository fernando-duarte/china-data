# Security Policy

## Security Improvements Implemented

### 1. Eliminated sys.path Manipulation
- Removed all `sys.path.insert()` calls from test files
- Configured proper Python package structure with modular utils organization
- Tests now use proper imports without path manipulation

### 2. Enhanced SSL/TLS Security
- Added explicit SSL certificate verification in `pwt_downloader.py`
- Set connection timeouts to prevent hanging connections
- Using `session.verify = True` to ensure certificate validation

### 3. Secure Temporary File Handling
- Set secure file permissions (0o600) for temporary files
- Proper cleanup with error handling for temporary files
- Using context managers for safe resource management

### 4. Dependency Management
- All dependencies are pinned to specific version ranges in `requirements.txt`
- Regular security updates should be performed

## Security Best Practices

### For Developers

1. **Never disable SSL verification** - Always use `verify=True` for requests
2. **Avoid sys.path manipulation** - Use proper package structure instead
3. **Secure file operations** - Set appropriate permissions for sensitive files
4. **Input validation** - Always validate and sanitize user inputs
5. **Use timeouts** - Set timeouts for all network operations

### Regular Security Maintenance

1. **Update dependencies regularly**:
   ```bash
   ./venv/bin/pip list --outdated
   ./venv/bin/pip install --upgrade [package-name]
   ```

2. **Security scanning**:
   ```bash
   ./venv/bin/pip install safety
   ./venv/bin/safety check
   ```

3. **Code review** - Review all code changes for security implications

## Reporting Security Vulnerabilities

If you discover a security vulnerability, please report it via:
1. Create a private security advisory on GitHub
2. Email the maintainers directly
3. Do not create public issues for security vulnerabilities

## Security Checklist for New Code

- [ ] No hardcoded credentials or secrets
- [ ] SSL/TLS verification enabled for all HTTP requests
- [ ] Proper input validation and sanitization
- [ ] Secure file permissions for sensitive files
- [ ] No use of `eval()`, `exec()`, or `pickle.loads()` with untrusted data
- [ ] Timeouts set for all network operations
- [ ] Proper error handling without exposing sensitive information 