# Security Scoring Guide

Evaluates findings from SEC01–SEC12 and calculates the security score (0–10) directly for the Scorecard Aggregator.

---

## 1. Severity Classification

Severity measures potential security impact.

| Severity | Definition |
|---|---|
| **critical** | Direct exploit (RCE, SQLi, auth bypass, data exfiltration). |
| **high** | Material defect (BOLA/IDOR, XSS, plaintext PII, hardcoded secret). |
| **medium** | Degraded posture (missing validation, unpinned package, verbose logs). |
| **low** | Minor defense-in-depth recommendation. |

### Severity Anchors by Rule

| Rule | Critical Example | High Example | Medium Example | Low Example |
|---|---|---|---|---|
| SEC01 | Raw SQL concatenation | Unsanitized OS exec | Raw LDAP query string | Helper validation flaw |
| SEC02 | Plaintext prod password | Hardcoded API key in client bundle | SHA1 password hash | Local dev config token |
| SEC03 | BOLA / IDOR on resource API | Missing admin role check | Inconsistent ACL check | Minor permission check |
| SEC04 | HTTP transmission of PII | Plaintext DB PII storage | Missing non-critical TLS | Cipher config suggestion |
| SEC05 | Unbounded raw file upload | Unvalidated JSON payload | Missing string length cap | Minor optional schema field |
| SEC06 | Direct `innerHTML` render | Reflected unescaped error page | Unsafe DOM property | Missing CSP header |
| SEC07 | Cookie auth POST w/o CSRF | Session cookie missing `SameSite` | Minor endpoint missing CSRF | Header check variant |
| SEC08 | RCE vulnerability in package | Floating dependency tags in prod | Outdated low-severity package | Unpinned devDependency |
| SEC09 | Prod `DEBUG=True` with stack | Permissive CORS (`*`) + creds | Default admin in staging | Missing security header |
| SEC10 | SSRF fetching AWS metadata | SSRF to internal microservice | Unvalidated URL redirect | Missing host allowlist |
| SEC11 | MD5 for auth tokens | `Math.random()` for session key | Legacy DES for internal comms | Non-crypto PRNG in UI |
| SEC12 | Logging passwords/tokens | Unmasked PII in central logs | Verbose stack log w/ token | Operational data in log |

---

## 2. Confidence Levels

Confidence reflects evidence certainty: **high** (direct visible exploit), **medium** (plausible pattern), or **low** (speculative).
Low-confidence concerns must be placed in `uncertainty_notes` (0 deduction).

---

## 3. Score Calculation

Score starts at **10**. Deductions are subtracted and floored at **0**.

### Per-Rule Deduction Guide

| Rule ID | Violation | Deduction |
| :--- | :--- | :--- |
| SEC01 | Injection flaw (SQL, Command, Code, NoSQL) | −1.5 |
| SEC02 | Hardcoded secret / credential in source | −1.5 |
| SEC03 | BOLA / IDOR / missing authorization check | −1.5 |
| SEC04 | Unencrypted PII in transit or storage | −1.2 |
| SEC05 | Missing input boundary checks | −0.8 |
| SEC06 | XSS vulnerability / unescaped DOM render | −1.2 |
| SEC07 | State request missing CSRF protection | −1.0 |
| SEC08 | Known vulnerable / unpinned dependency | −0.8 |
| SEC09 | Security misconfiguration (debug, CORS `*`) | −1.0 |
| SEC10 | SSRF / unsafe URL fetching | −1.2 |
| SEC11 | Weak cryptography / non-crypto PRNG | −1.0 |
| SEC12 | Sensitive data written to logs | −0.8 |

### Base Deductions & Confidence Modifiers

- **Base Deductions**: Critical = 2.5, High = 1.5, Medium = 0.7, Low = 0.2
- **Modifiers**: High = 1.00, Medium = 0.70, Low = 0.30
- **Formula**: `deduction = base_deduction × confidence_multiplier`

### Example Calculation

| Finding | Severity | Confidence | Base | Multiplier | Deduction |
|---|---|---|---|---|---|
| SQLi in search (SEC01) | critical | high | 2.5 | 1.00 | 2.5 |
| Hardcoded secret (SEC02) | high | high | 1.5 | 1.00 | 1.5 |
| Permissive CORS (SEC09) | medium | medium | 0.7 | 0.70 | 0.5 |
| **Total Deduction / Final Score** | | | | | **4.5 / 5.5** |

---

## 4. Rule Influence on Scoring

| Rule | Severity Range | Core Focus |
|---|---|---|
| SEC01 | high – critical | Code execution / data exfiltration |
| SEC02 | high – critical | Credential exposure |
| SEC03 | high – critical | Unauthorized tenant access |
| SEC04 | medium – high | Data exposure & compliance |
| SEC05 | low – medium | Lack of boundary validation |
| SEC06 | medium – high | Client-side XSS execution |
| SEC07 | medium – high | Unverified client state modification |
| SEC08 | low – high | Dependency CVE risks |
| SEC09 | medium – high | Exposed diagnostics / CORS policies |
| SEC10 | high – critical | Internal network scanning / SSRF |
| SEC11 | medium – high | Broken crypto / predictable tokens |
| SEC12 | low – medium | Credential leakage in logs |

---

## 5. Handling Duplicate Findings

Symptoms sharing one root cause produce **one finding** under the primary rule ID (e.g., unauthenticated endpoint SEC03 lacking validation SEC05 counts once as SEC03).

---

## 6. Documented Exceptions and Accepted Trade-offs

Documented trade-offs (code comments / ADRs) reduce deductions by **50%** (`status: "accepted"`).

---

## 7. Insufficient Evidence

Unconfirmed concerns incur **0 deduction** and are recorded in `uncertainty_notes`:
```json
{ "uncertainty_note": "SEC03: Authz check handled by upstream gateway; requires gateway config to verify." }
```

---

## 8. Blocking vs. Advisory Findings

### Blocking Policy

A review dimension is **blocked** (`"blocked": true`) and prevents merging under any of the following conditions:

1. **Numeric Score Below Threshold**: Final dimension score is **below 9/10 (below 9.0)**.
2. **Critical Violation Override**: At least one confirmed **critical** (e.g. SQLi, RCE, BOLA/IDOR, hardcoded production secret) finding is present, regardless of numeric score.
3. **Multiple Minor Findings**: More than one minor finding is present, causing total deductions to exceed the 9/10 allowance.

When blocked, the review output sets `"blocked": true` and provides a `block_reason`:
```json
{
  "dimension": "security",
  "score": 8.3,
  "blocked": true,
  "block_reason": "Dimension score is below 9/10 (8.3/10) due to security findings requiring resolution before merge."
}
```

### Passing Policy

A review dimension is **passing** (`"blocked": false`) only when:
- **10/10**: Zero confirmed violations.
- **9/10 (9.0–9.9)**: At most ONE minor non-blocking finding is present, with zero critical/high security vulnerabilities.

---

## 9. Scorecard Aggregator Integration

Outputs a standard result object for the Scorecard Aggregator:

```json
{
  "dimension": "security",
  "score": 9.3,
  "findings": [
    {
      "ruleId": "SEC08",
      "title": "Minor Unpinned Dev Package Version",
      "severity": "low",
      "confidence": "high",
      "file": "package.json",
      "lineStart": 22,
      "lineEnd": 22,
      "evidence": "Dev dependency uses caret range specifier",
      "impact": "Non-reproducible local build environment",
      "recommendation": "Pin exact package version",
      "technology": "JSON/Node",
      "status": "open"
    }
  ],
  "uncertainty_notes": [],
  "blocked": false
}
```

**Aggregator contract rules:**
- `dimension` must be `"security"`
- `score` must be a number in `[0, 10]` directly
- `blocked` must be `true` if score < 9 (below 9/10) or if a critical violation is present
- `findings` must be an array
- `uncertainty_notes` is optional; omit if empty

---

## 10. Score Interpretation Quick Reference

| Score (0–10) | Status | Meaning |
|---|---|---|
| **10 / 10** | ✅ **Passing** | Zero security defects; strict parameterization and auth. |
| **9.0 – 9.9 / 10** | ✅ **Passing (Minor Issue)** | Verified core controls; at most one minor non-blocking finding. |
| **< 9 / 10** (0–8.9) | 🔴 **Blocked** | Score below 9/10 threshold or critical vulnerability present; merge blocked until resolved. |
