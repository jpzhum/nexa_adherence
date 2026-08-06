# Security Policy

## Reporting a vulnerability

Please do not disclose vulnerabilities, credentials, personal data, or operational data in a public issue.

Use GitHub's private vulnerability reporting option in the repository's **Security** tab when it is available. If that option is unavailable, open a public issue that requests a private communication channel without including exploit details or sensitive material. A maintainer can then arrange an appropriate private channel.

Include the affected version or commit, a concise impact description, reproducible steps, and any suggested mitigation. Use synthetic data in examples and remove local paths, recipient details, database contents, and logs.

## Scope and handling

The current codebase is a local desktop application. Reports should consider file parsing, generated exports, SQLite storage, logs, local recipient data, and optional Outlook integration. Maintainers will assess reports on a best-effort basis; this repository does not publish a response-time or remediation SLA.

Never commit secrets or real operational data as part of a security fix. If sensitive content is found in Git history, notify the maintainer privately because `.gitignore` changes do not remove historical content.
