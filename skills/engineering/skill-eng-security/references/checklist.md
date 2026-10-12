# Security Rules & Threat Inspection Checklist

Use during code review to identify security vulnerabilities, authorization flaws, data exposure, and configuration risks across any technology stack.

---

## Security Vulnerabilities & Threat Reference Table

| Anti-Pattern | Rule ID | Description | Remediation |
| :--- | :---: | :--- | :--- |
| **SQL / Command / Code Injection** | SEC01 | Untrusted input directly formatted or concatenated into SQL, shell commands, or code execution contexts. | Use parameterized queries, ORMs, exec File arrays, or strict context sanitization. |
| **Hardcoded Secret / Weak Auth** | SEC02 | Plaintext API keys, passwords, private keys, or weak password hashing (MD5/SHA1) in code. | Load secrets from environment/vault; use Argon2id/bcrypt/PBKDF2 for passwords. |
| **BOLA / Missing Authorization** | SEC03 | Endpoint processes object requests without checking if authenticated caller owns or is authorized for target resource ID. | Enforce row-level ownership checks and attribute-based access control (ABAC/RBAC) on every request. |
| **Unencrypted PII / Data Exposure** | SEC04 | Sensitive data (PII, tokens, credit card info) transmitted over HTTP or stored unencrypted. | Enforce TLS 1.3 in transit and AES-256-GCM / field-level encryption at rest. |
| **Missing Input Boundary Checks** | SEC05 | Accepting unbounded file uploads, raw JSON payloads, or string parameters without schema validation or size limits. | Enforce strict schema validation (Zod, Pydantic, Bean Validation) and file size caps. |
| **Unencoded UI Output (XSS)** | SEC06 | Rendering raw HTML or unescaped user input directly into the browser DOM (`dangerouslySetInnerHTML`, `v-html`, `innerHTML`). | Encode contextually; use framework auto-escaping and strict Content Security Policy (CSP). |
| **State Request Without CSRF Token** | SEC07 | State-changing HTTP endpoints (POST, PUT, DELETE) lacking CSRF token verification or `SameSite` cookies. | Enforce Anti-CSRF tokens and `SameSite=Lax` or `Strict` cookie attributes. |
| **Vulnerable / Unpinned Package** | SEC08 | Importing dependencies with known CVEs or using unpinned floating version tags (`*`, `latest`). | Pin exact package versions; run automated dependency security scanners (`npm audit`, `pip-audit`). |
| **Insecure Security Configuration** | SEC09 | Permissive CORS (`Access-Control-Allow-Origin: *` with credentials), enabled debug modes, or default admin credentials in config. | Restrict CORS origins explicitly, disable debug modes in production, and remove default accounts. |
| **SSRF / Unrestricted Fetch** | SEC10 | Server fetching user-supplied URLs without restricting IP ranges or protocol schemes. | Validate URLs against strict allowed domain lists and block internal IP ranges (127.0.0.1, 10.0.0.0/8, 169.254.169.254). |
| **Weak Cryptography & PRNG** | SEC11 | Using legacy ciphers (DES, RC4), broken hashes (MD5, SHA1), or standard `Math.random()` / `random.random()` for security tokens. | Use cryptographically secure PRNGs (`crypto.getRandomValues`, `secrets` module) and standard ciphers. |
| **Sensitive Data in Logs** | SEC12 | Writing passwords, bearer tokens, API secrets, or PII directly to application logs or error traces. | Redact/mask sensitive fields before logging; filter request headers/bodies in log formatters. |

---

## Per-Rule Detailed Criteria

### SEC01: Injection Flaws & Sanitization
- **Objective & Scope**: Prevent SQL, NoSQL, OS Command, Code, and XPath injection vulnerabilities.
- **Detection Criteria**: Inspect data flow from request parameters, headers, or external payloads into raw query builders, `exec()`, `eval()`, or shell invocations.
- **Evidence Requirements**: Show the unformatted input source line and its direct concatenation into execution sinks.
- **False-Positive Guidance**: Static string queries or parameterized ORM calls with bound parameters are compliant.
- **Severity Guidance**: Critical (−15 deduction) per instance.
- **Remediation Guidance**: Replace raw string concatenation with parameterized statements, ORM methods, or argument arrays.

### SEC02: Authentication & Credential Management
- **Objective & Scope**: Eliminate hardcoded credentials and ensure secure authentication mechanisms.
- **Detection Criteria**: Flag hardcoded secrets, API tokens, private keys, or weak password hashing algorithms (MD5, SHA1).
- **Evidence Requirements**: Highlight literal secret strings or legacy hashing function calls in source code.
- **False-Positive Guidance**: Mock secret placeholders in test fixtures or public non-sensitive configuration keys are compliant.
- **Severity Guidance**: Critical (−15 deduction) per instance.
- **Remediation Guidance**: Externalize secrets to environment variables or secret vaults; use Argon2id/bcrypt for passwords.

### SEC03: Authorization & Access Control
- **Objective & Scope**: Prevent Broken Object Level Authorization (BOLA/IDOR) and unauthorized privilege escalation.
- **Detection Criteria**: Flag endpoints that fetch or modify resources by ID without validating that the authenticated user owns or has explicit permission for that resource.
- **Evidence Requirements**: Show the resource lookup method and demonstrate the missing ownership or role check.
- **False-Positive Guidance**: Endpoints operating strictly on public data or where authorization is handled by upstream middleware are compliant.
- **Severity Guidance**: Critical (−15 deduction) per endpoint.
- **Remediation Guidance**: Add explicit tenant/user ownership checks or attribute-based authorization guards before resource access.

### SEC04: Data Exposure & Encryption
- **Objective & Scope**: Protect sensitive data (PII, credentials, tokens) during transmission and storage.
- **Detection Criteria**: Flag plaintext transmission of sensitive data, HTTP without TLS, or unencrypted storage of sensitive fields.
- **Evidence Requirements**: Identify sensitive fields being transmitted over unencrypted channels or written unencrypted to storage.
- **False-Positive Guidance**: Non-sensitive operational metrics or public metadata stored without encryption are compliant.
- **Severity Guidance**: High (−12 deduction) per instance.
- **Remediation Guidance**: Enforce TLS for all endpoints and encrypt sensitive database fields using strong ciphers (AES-256-GCM).

### SEC05: Input Validation & Boundaries
- **Objective & Scope**: Ensure all external inputs are strictly validated against type, format, and length boundaries.
- **Detection Criteria**: Flag endpoint handlers accepting raw untyped dictionaries, unbounded payload bodies, or missing size limits on file uploads.
- **Evidence Requirements**: Reference parameter receiving external data without schema validation or boundary checks.
- **False-Positive Guidance**: Internal strongly-typed method calls between trusted system components are compliant.
- **Severity Guidance**: Medium (−8 deduction) per handler.
- **Remediation Guidance**: Apply strict schema validation libraries (Pydantic, Zod, JOI) and set explicit payload size limits.

### SEC06: XSS & Output Encoding
- **Objective & Scope**: Prevent Cross-Site Scripting (XSS) in web interfaces and dynamic content rendering.
- **Detection Criteria**: Flag unescaped user input rendered into HTML DOM, `dangerouslySetInnerHTML`, `v-html`, or raw template interpolation without escaping.
- **Evidence Requirements**: Point to user-controlled variable passed directly to raw HTML rendering property.
- **False-Positive Guidance**: Standard JSX/Vue template bindings that apply automatic contextual HTML escaping are compliant.
- **Severity Guidance**: High (−12 deduction) per component.
- **Remediation Guidance**: Use framework auto-escaping, apply DOMPurify for intentional rich text, and configure strict CSP headers.

### SEC07: CSRF & State Request Safety
- **Objective & Scope**: Protect state-changing HTTP requests against Cross-Site Request Forgery attacks.
- **Detection Criteria**: Flag POST, PUT, DELETE endpoints lacking CSRF token verification or missing `SameSite` cookie flags for session cookies.
- **Evidence Requirements**: Show state-changing route definition lacking CSRF middleware protection or cookie configuration without `SameSite`.
- **False-Positive Guidance**: Stateless REST APIs relying exclusively on `Authorization: Bearer` headers (not ambient browser cookies) are exempt from CSRF.
- **Severity Guidance**: High (−10 deduction) per handler.
- **Remediation Guidance**: Enforce CSRF token protection on cookie-authenticated web forms and set `SameSite=Lax` or `Strict`.

### SEC08: Dependency & Supply Chain Security
- **Objective & Scope**: Prevent security risks from vulnerable or unpinned third-party dependencies.
- **Detection Criteria**: Flag dependencies using wildcard version selectors (`*`, `>=`), unpinned container bases, or packages with known high-severity CVEs.
- **Evidence Requirements**: Cite package manifest file line with unpinned or vulnerable dependency specification.
- **False-Positive Guidance**: Strictly pinned exact dependency versions or internal verified corporate package registries are compliant.
- **Severity Guidance**: Medium (−8 deduction) per package.
- **Remediation Guidance**: Pin exact dependency versions (`lockfile`) and integrate automated vulnerability scanners (`npm audit`, `Snyk`).

### SEC09: Security Hardening & Config
- **Objective & Scope**: Eliminate dangerous default settings, verbose debugging, and overly permissive security headers.
- **Detection Criteria**: Flag `DEBUG=True` flags in production settings, permissive `CORS (*)` with credentials, or missing security headers (HSTS, X-Content-Type-Options).
- **Evidence Requirements**: Reference configuration files or middleware setups enabling debug or permissive CORS.
- **False-Positive Guidance**: Development environment configuration files explicitly isolated from production builds are compliant.
- **Severity Guidance**: High (−10 deduction) per config.
- **Remediation Guidance**: Restrict CORS origins explicitly, disable debug modes in production builds, and configure security headers.

### SEC10: SSRF & Remote Request Safety
- **Objective & Scope**: Prevent Server-Side Request Forgery and dangerous remote URL fetching.
- **Detection Criteria**: Flag HTTP client requests where target URL host or IP is directly derived from unvalidated user input.
- **Evidence Requirements**: Show user input controlling host/URL parameter of outbound HTTP request without IP filtering.
- **False-Positive Guidance**: Hardcoded target URLs or domain validation using strict allowlists are compliant.
- **Severity Guidance**: High (−12 deduction) per occurrence.
- **Remediation Guidance**: Validate target domains against strict allowlists and resolve DNS to block private IP ranges (RFC 1918, loopback).

### SEC11: Cryptography & Randomness
- **Objective & Scope**: Ensure strong, modern cryptographic algorithms and secure random number generators.
- **Detection Criteria**: Flag use of MD5, SHA1, DES, RC4, ECB mode, or non-cryptographic PRNGs (`Math.random()`, `random.random()`) for tokens or keys.
- **Evidence Requirements**: Show function call instantiating legacy cipher/hash or non-secure PRNG in security-sensitive contexts.
- **False-Positive Guidance**: Non-security uses of MD5/SHA1 for non-crypto checksums or `Math.random()` for non-security UI animations are compliant.
- **Severity Guidance**: High (−10 deduction) per occurrence.
- **Remediation Guidance**: Use AES-256-GCM, SHA-256/3, and cryptographically secure PRNGs (`secrets` module, `crypto.getRandomValues`).

### SEC12: Logging, Audit & Secret Masking
- **Objective & Scope**: Prevent sensitive data leakage in application logs and ensure security event auditability.
- **Detection Criteria**: Flag log statements writing raw request bodies, authentication headers, passwords, credit card numbers, or tokens to logs.
- **Evidence Requirements**: Reference log function call passing variables containing sensitive credentials or PII.
- **False-Positive Guidance**: Sanitized log formatters or masked strings (`****`) are compliant.
- **Severity Guidance**: Medium (−8 deduction) per log statement.
- **Remediation Guidance**: Implement field-masking log filters to automatically redact credentials and PII prior to log output.

---

## Technology Adaptation

Security requirements apply universally across all technologies, frameworks, and platforms:
- **Backend & Web APIs (Python/Flask/FastAPI/Django, Java/Spring, C#/.NET, Node/Express/Nest, Go, Rust)**: Enforce parameterized queries (SEC01), secret vaults (SEC02), BOLA guards (SEC03), input validation schemas (SEC05), and security headers/CORS (SEC09).
- **Frontend Frameworks (React, Vue, Angular, Svelte)**: Avoid dangerous raw DOM injection (SEC06), enforce CSRF or token-based auth (SEC07), and avoid embedding secrets in client bundles (SEC02).
- **AI Agents & LLM Orchestration (LangChain, LangGraph, AutoGen, LlamaIndex)**: Validate agent tool inputs against command/SQL injection (SEC01), restrict tool SSRF calls (SEC10), mask API keys in logs (SEC12), and enforce tool permission boundaries (SEC03).
- **Cloud, Infrastructure & Containers (Terraform, CloudFormation, Docker, Kubernetes)**: Enforce TLS, block public S3/storage buckets (SEC04), restrict security groups, and avoid hardcoded secrets in manifests or Dockerfiles (SEC02).

