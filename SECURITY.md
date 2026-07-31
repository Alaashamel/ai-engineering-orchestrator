# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |
| < 0.1   | No        |

## Reporting a Vulnerability

We take the security of AI Engineering Orchestrator seriously. If you believe you've found a security vulnerability, please report it to us by opening a private issue or contacting the maintainers directly.

**Please do not report security vulnerabilities through public GitHub issues.**

## Security Practices

- All API keys are stored in environment variables, never committed
- Path traversal protection on file operations
- Input validation on all API endpoints
- Rate limiting via configurable middleware
