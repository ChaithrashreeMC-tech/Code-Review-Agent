# Gate 1 Report Schema and Output Specification

This document defines the structured JSON contract and Markdown reporting format for Gate 1 local code reviews.

---

## 1. JSON Report Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Gate1ValidationReport",
  "type": "object",
  "properties": {
    "gate": { "type": "string", "enum": ["GATE_1_LOCAL", "GATE_1_ENTRY_GUARD"] },
    "timestamp": { "type": "string", "format": "date-time" },
    "status": { "type": "string", "enum": ["PASS", "BLOCKED", "INCOMPLETE"] },
    "ready_for_pr": { "type": "boolean" },
    "repository": {
      "type": "object",
      "required": ["root", "branch", "stacks", "changed_files"],
      "properties": {
        "root": { "type": "string" },
        "branch": { "type": "string" },
        "stacks": { "type": "array", "items": { "type": "string" } },
        "changed_files": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["path", "status"],
            "properties": {
              "path": { "type": "string" },
              "status": { "type": "string", "enum": ["modified", "added", "deleted", "untracked"] },
              "lines_added": { "type": "integer" },
              "lines_removed": { "type": "integer" }
            }
          }
        }
      }
    },
    "build_and_static": {
      "type": "object",
      "required": ["status", "errors", "warnings"],
      "properties": {
        "status": { "type": "string", "enum": ["passed", "failed", "skipped", "unavailable"] },
        "command": { "type": ["string", "null"] },
        "duration_ms": { "type": "integer" },
        "errors": { "type": "array", "items": { "type": "string" } },
        "warnings": { "type": "array", "items": { "type": "string" } }
      }
    },
    "automated_tests": {
      "type": "object",
      "required": ["status", "total", "passed", "failed", "skipped"],
      "properties": {
        "status": { "type": "string", "enum": ["passed", "failed", "skipped", "unavailable"] },
        "command": { "type": ["string", "null"] },
        "total": { "type": "integer" },
        "passed": { "type": "integer" },
        "failed": { "type": "integer" },
        "skipped": { "type": "integer" },
        "duration_ms": { "type": "integer" },
        "failures": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["test_name", "error_message"],
            "properties": {
              "test_name": { "type": "string" },
              "error_message": { "type": "string" },
              "file": { "type": "string" }
            }
          }
        }
      }
    },
    "dimensions": {
      "type": "object",
      "required": ["security", "performance", "maintainability", "modularity", "business_logic"],
      "properties": {
        "security": { "$ref": "#/definitions/DimensionResult" },
        "performance": { "$ref": "#/definitions/DimensionResult" },
        "maintainability": { "$ref": "#/definitions/DimensionResult" },
        "modularity": { "$ref": "#/definitions/DimensionResult" },
        "business_logic": { "$ref": "#/definitions/DimensionResult" }
      }
    },
    "summary": {
      "type": "object",
      "required": ["total_findings", "critical_count", "high_count", "medium_count", "low_count", "average_score"],
      "properties": {
        "total_findings": { "type": "integer" },
        "critical_count": { "type": "integer" },
        "high_count": { "type": "integer" },
        "medium_count": { "type": "integer" },
        "low_count": { "type": "integer" },
        "average_score": { "type": "number" }
      }
    },
    "blocking_reasons": { "type": "array", "items": { "type": "string" } },
    "uncertainty_notes": { "type": "array", "items": { "type": "string" } },
    "remediation_items": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["priority", "dimension", "action", "file"],
        "properties": {
          "priority": { "type": "string", "enum": ["immediate", "recommended", "optional"] },
          "dimension": { "type": "string" },
          "ruleId": { "type": "string" },
          "action": { "type": "string" },
          "file": { "type": "string" },
          "line": { "type": "integer" }
        }
      }
    }
  },
  "definitions": {
    "DimensionResult": {
      "type": "object",
      "required": ["score", "blocked", "findings", "uncertainty_notes"],
      "properties": {
        "score": { "type": "number", "minimum": 0.0, "maximum": 10.0 },
        "blocked": { "type": "boolean" },
        "findings": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["ruleId", "title", "severity", "confidence", "file", "lineStart", "evidence", "impact", "recommendation"],
            "properties": {
              "ruleId": { "type": "string" },
              "title": { "type": "string" },
              "severity": { "type": "string", "enum": ["critical", "high", "medium", "low"] },
              "confidence": { "type": "string", "enum": ["high", "medium", "low"] },
              "file": { "type": "string" },
              "lineStart": { "type": "integer" },
              "lineEnd": { "type": "integer" },
              "evidence": { "type": "string" },
              "impact": { "type": "string" },
              "recommendation": { "type": "string" }
            }
          }
        },
        "uncertainty_notes": { "type": "array", "items": { "type": "string" } }
      }
    }
  }
}
```

---

## 2. Markdown Report Template

```markdown
# 🛡️ Gate 1 Local Code Review Report

**Status**: [ PASS | 🔴 BLOCKED | ⚠️ INCOMPLETE ] | **Ready for PR**: [ Yes | No ]
**Repository**: `<repo-root>` | **Branch**: `<branch-name>` | **Stacks**: Python, TypeScript

---

### Executive Summary

| Stage / Dimension | Status / Score | Details |
|---|---|---|
| **Build & Static Checks** | Passed / Failed | `<command>` execution details |
| **Automated Tests** | Passed / Failed | `X/Y` tests passed (`Z` failures) |
| **Security** | `10.0 / 10` | Confirmed findings count |
| **Performance** | `10.0 / 10` | Confirmed findings count |
| **Maintainability** | `9.0 / 10` | Confirmed findings count |
| **Modularity** | `10.0 / 10` | Confirmed findings count |
| **Business Logic** | `10.0 / 10` | Confirmed findings count |

---

### Findings & Remediation
- **[<RuleID>] <Title>** (`<file>:<line>`) — **Severity**: `<Severity>` | **Confidence**: `<Confidence>`
  - **Evidence**: `<Code excerpt / defect trace>`
  - **Impact**: `<Operational risk>`
  - **Action**: `<Remediation instructions>`

---

### Blocking Reasons
- `<List of blocking reasons or "None. Ready for PR creation.">`
```
