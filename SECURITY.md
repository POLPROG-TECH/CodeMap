# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.0.x   | ✅ Current release |

## Reporting a Vulnerability

If you discover a security vulnerability in CodeMap, please report it responsibly.

**Do not open a public issue.**

Instead, please email **contact@polprog.pl** with:

- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge your report within **48 hours** and aim to provide a fix or mitigation within **7 days** for critical issues.

## Scope

Security concerns relevant to CodeMap include:

- **Path traversal** during repository scanning or when resolving include/exclude patterns
- **Arbitrary code execution** through language extractors or plug-in discovery
- **Output safety** - XSS or HTML injection in the rendered HTML reports
- **Sensitive data leakage** - internal paths, author emails, or config values exposed in rendered output
- **Dependency vulnerabilities** in third-party packages

## Disclosure Policy

We follow coordinated disclosure:

1. Report the issue privately via the contact above.
2. We confirm receipt and begin investigation.
3. Once a fix is released, we publicly acknowledge the reporter (with their consent).
