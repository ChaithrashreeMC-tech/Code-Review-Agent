---
name: skill-eng-security
description: >-
  Activate when reviewing code changes involving security, vulnerability mitigation,
  authentication, authorization, access control, input validation, injection flaws,
  cross-site scripting (XSS), cross-site request forgery (CSRF), server-side request
  forgery (SSRF), cryptography, secrets management, dependency security, secure logging,
  or security configuration across any programming language, framework, or architecture.
---

# Engineering Security Review Skill

## 1. Purpose & Activation

This skill evaluates pull requests for security vulnerabilities, authentication/authorization flaws, injection vulnerabilities, cryptographic weaknesses, sensitive data leakage, and insecure configurations across any software codebase.

**Activate when** code changes touch authentication flows, authorization controls, user input processing, database queries, API endpoints, external network calls, cryptographic operations, secrets handling, dependency manifests, CORS/headers configuration, or security logging; or when review context cites security, vulnerability, CVE, OWASP, auth, encryption, or secrets across any language or platform.

## 2. Technology Context

Infer the relevant technology stack, runtime, frameworks, and architectural style from changed files, imports, and configuration. Apply universal security rules consistently regardless of technology  or architecture.
Refer to `references/checklist.md` for technology- and paradigm-specific evidence patterns and remediation guidance.

Technology detection contextualizes evidence interpretation and idiomatic remediation—it does not restrict review applicability or diminish universal security requirements.

## 3. Security Rules

| ID | Rule | Objective |
|---|---|---|
| SEC01 | Injection Flaws & Sanitization | Prevent SQL, NoSQL, Command, Code, and XPath injection via untrusted inputs. |
| SEC02 | Authentication & Credential Management | Eliminate hardcoded secrets, weak password hashing, and flawed auth flows. |
| SEC03 | Authorization & Access Control | Prevent Broken Object Level Authorization (BOLA/IDOR) and missing access checks. |
| SEC04 | Data Exposure & Encryption | Protect sensitive data in transit/at rest (PII, tokens, keys) using strong cryptography. |
| SEC05 | Input Validation & Boundaries | Enforce strict validation, size caps, and type checks on external inputs. |
| SEC06 | XSS & Output Encoding | Prevent Reflected, Stored, and DOM XSS via context-aware output encoding. |
| SEC07 | CSRF & State Request Safety | Enforce CSRF tokens, `SameSite` cookies, and origin validation on state changes. |
| SEC08 | Dependency & Supply Chain Security | Block vulnerable, unpinned, or compromised third-party packages and containers. |
| SEC09 | Security Hardening & Config | Eliminate default credentials, debug modes in prod, and permissive CORS. |
| SEC10 | SSRF & Remote Request Safety | Prevent Server-Side Request Forgery and unsafe URL fetching/deserialization. |
| SEC11 | Cryptography & Randomness | Block weak algorithms (MD5/SHA1/DES) and non-cryptographic PRNGs for security. |
| SEC12 | Logging, Audit & Secret Masking | Prevent sensitive data leakage in logs and ensure auditability of security events. |

*Detailed criteria, evidence, and remediation per rule are defined in [`references/checklist.md`](references/checklist.md).*

## 4. Review Workflow

1. **Inspect Context**: Review diffs, API parameters, query builders, auth checks, headers, and dependency changes.
2. **Detect Stack & Paradigm**: Identify runtime, web frameworks, ORM/query builders, and security middleware.
3. **Select Rules**: Match code changes against universal security rules (SEC01–SEC12).
4. **Evaluate Evidence**: Consult [`references/checklist.md`](references/checklist.md) to substantiate findings with visible code patterns and exploit paths.
5. **Score & Deduplicate**: Apply [`references/scoring-guide.md`](references/scoring-guide.md). Consolidate symptoms sharing one root cause into one finding.
6. **Generate Output**: Format findings using the Scorecard Aggregator schema below.

## 5. Review Principles

- **Universal Principles, Stack-Idiomatic Remediation**: Apply core security rules everywhere while tailoring fix recommendations to stack conventions.
- **Evidence-Based Vulnerability Identification**: Report security findings only when visible code patterns present a realistic exploit path; record uncertainties in `uncertainty_notes`.
- **Defense in Depth**: Evaluate multiple security layers (validation, authz, sanitization, encryption) rather than relying on a single control.
- **No Blanket False Positives**: Differentiate between safe, parameterized APIs and genuine unsafe string interpolations.
- **Root-Cause Deduplication**: One underlying defect (e.g. unauthenticated API endpoint) produces one finding, not separate findings for every exposed internal method.
- **Review Only**: Identify security flaws and provide actionable guidance; do not execute automated code changes.

## 6. Output Contract & References

Return structured output compatible with the Code Review Portal Scorecard Aggregator:

```json
{
  "dimension": "security",
  "score": 7.5,
  "findings": [
    {
      "ruleId": "SEC01",
      "title": "SQL Injection in User Search Endpoint",
      "severity": "critical",
      "confidence": "high",
      "file": "src/controllers/user_controller.py",
      "lineStart": 45,
      "lineEnd": 48,
      "evidence": "Unsanitized user input string directly concatenated into raw SQL query string",
      "impact": "Allows arbitrary SQL execution, data exfiltration, or database manipulation",
      "recommendation": "Use parameterized queries or ORM query builder bindings",
      "technology": "Python/Flask",
      "status": "open"
    }
  ],
  "uncertainty_notes": [],
  "blocked": true
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `ruleId` | string | Yes | SEC01–SEC12 stable identifier |
| `title` | string | Yes | Concise issue summary |
| `severity` | string | Yes | `critical`, `high`, `medium`, or `low` |
| `confidence` | string | Yes | `high`, `medium`, or `low` |
| `file` | string | Yes | Repository-relative path |
| `lineStart` | integer | Yes | First line number of the relevant code |
| `lineEnd` | integer | No | End line number of the relevant code block |
| `evidence` | string | Yes | Concrete code observation supporting the finding |
| `impact` | string | Yes | Exploitability or security risk consequence |
| `recommendation` | string | Yes | Stack-specific actionable remediation guidance |
| `technology` | string | No | Inferred technology stack |
| `status` | string | No | Finding lifecycle status (default: `open`) |

Integration rules for the aggregator:
- `score` starts at 10 (0–10 scale directly), reduced by deductions according to [`references/scoring-guide.md`](references/scoring-guide.md).
- `blocked` is set to `true` when the final score is below 9/10 (below 9.0) OR when any confirmed critical vulnerability is present.
- A score of 9–10 (9.0–10.0) passes (`blocked: false`) only if no critical vulnerability exists and findings satisfy the minor-issue allowance (at most one minor finding).
- Low-confidence observations must be recorded in `uncertainty_notes` and incur 0 deductions.

## 7. Supporting References

- **Inspection Checklist**: [`references/checklist.md`](references/checklist.md) — Detailed criteria, evidence, and remediation per rule across languages and paradigms.
- **Scoring Guide**: [`references/scoring-guide.md`](references/scoring-guide.md) — Severity tiers, deduction formulas, exceptions, and merge blocking.
- **Validation Suite**: [`validation/test-suite.json`](validation/test-suite.json) — Automated test cases for detection and false-positive verification.

