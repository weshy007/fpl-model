# Security Policy

## Supported Versions

At this early stage, only the latest version on the `main` branch is
considered supported.

## Reporting a Vulnerability

Do not disclose security vulnerabilities through public GitHub issues.

Report security concerns privately to the project maintainer using the
repository's configured security contact.

Include:

- Description
- Steps to reproduce
- Potential impact
- Suggested mitigation, if known

Please allow reasonable time for investigation before public disclosure.

## Secrets

Never commit:

- API keys
- Database credentials
- Authentication tokens
- Passwords
- Private keys
- `.env` files containing secrets

Use `.env.example` to document required environment variables.

## Dependencies

Dependencies should be kept reasonably current and vulnerabilities should be
reviewed before releases.
