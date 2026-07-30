# Security Policy

## Reporting a Vulnerability

Report vulnerabilities by opening an issue or emailing the maintainers.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |
| < 0.1   | No        |

## Security Practices

- All API keys are stored in environment variables, never committed
- Path traversal protection on file operations
- Input validation on all API endpoints
- Rate limiting via configurable middleware
