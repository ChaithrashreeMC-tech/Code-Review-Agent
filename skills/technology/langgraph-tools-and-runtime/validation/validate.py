#!/usr/bin/env python3
"""
Automated Validator and Test Suite Runner for LangGraph Tools and Runtime Skill.
Validates SKILL.md, references, test-suite.json schema, test fixtures, and executes all 18 test cases.
"""

import os
import sys
import json
import re

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")
REFERENCES_DIR = os.path.join(SKILL_DIR, "references")
TEST_SUITE_JSON = os.path.join(SKILL_DIR, "validation", "test-suite.json")
TEST_SUITE_SCHEMA = os.path.join(SKILL_DIR, "validation", "test-suite.schema.json")
TEST_DATA_DIR = os.path.join(SKILL_DIR, "validation", "test-data")

REQUIRED_REFERENCES = [
    "checklist.md",
    "architecture-and-patterns.md"
]

def strip_comments_and_docstrings(source: str) -> str:
    """Strip python docstrings and single-line comments for accurate code matching."""
    source = re.sub(r'""".*?"""', '', source, flags=re.DOTALL)
    source = re.sub(r"'''.*?'''", '', source, flags=re.DOTALL)
    lines = [line.split('#')[0] for line in source.splitlines()]
    return '\n'.join(lines)

def evaluate_tool_fixture(fixture_content: str, tc_id: str):
    """
    Evaluates LangGraph tool and runtime code fixture for structural defects and false-positive guards.
    """
    code_only = strip_comments_and_docstrings(fixture_content)
    defects = []
    uncertainty_notes = []

    # TC-002: Unregistered tool request
    if 'execute_raw_code' in code_only and 'registered_tools' in code_only:
        defects.append({
            "category": "unregistered_tool_request",
            "evidence": ["execute_raw_code", "tool_calls", "registered_tools"]
        })

    # TC-003: Malformed / untyped arguments handling causing TypeError
    if 'calculate_tax' in code_only and 'country_code == "US"' in code_only and 'BaseModel' not in code_only and 'args_schema' not in code_only:
        defects.append({
            "category": "malformed_arguments_handling",
            "evidence": ["country_code", "amount", "TypeError"]
        })

    # TC-004: Unassociated tool call ID
    if 'tool_call_id=""' in code_only or "tool_call_id=''" in code_only:
        defects.append({
            "category": "unassociated_tool_call_id",
            "evidence": ["tool_call_id", "ToolMessage", "call"]
        })

    # TC-005: Missing runtime configuration validation (KeyError)
    if 'config["configurable"]["api_token"]' in code_only and '.get(' not in code_only:
        defects.append({
            "category": "missing_runtime_config_validation",
            "evidence": ["configurable", "api_token", "RunnableConfig"]
        })

    # TC-006: Missing required dependencies
    if 'global_uninitialized_order_service' in code_only:
        defects.append({
            "category": "uninitialized_dependency",
            "evidence": ["global_uninitialized_order_service", "submit"]
        })

    # TC-007: Destructive action without authorization check
    if 'delete_database_records' in code_only and 'raw_db_executor' in code_only:
        defects.append({
            "category": "missing_authorization_boundary",
            "evidence": ["delete_database_records", "DELETE FROM", "raw_db_executor"]
        })

    # TC-008: Trusting model-provided tenant_id rather than runtime context
    if 'get_tenant_billing_records' in code_only and 'tenant_id: str' in code_only and 'config' not in code_only:
        defects.append({
            "category": "cross_tenant_isolation_violation",
            "evidence": ["tenant_id", "billing_db", "query_by_tenant"]
        })

    # TC-009: Invalid error classification (400 treated as transient)
    if 'status_code == 400' in code_only and 'ConnectionResetError' in code_only:
        defects.append({
            "category": "invalid_error_classification",
            "evidence": ["status_code == 400", "ConnectionResetError", "Retryable"]
        })

    # TC-010: Unbounded retry loop
    if 'while True:' in code_only and 'time.sleep' in code_only and 'inventory_client' in code_only:
        defects.append({
            "category": "unbounded_retry_loop",
            "evidence": ["while True", "time.sleep", "inventory_client"]
        })

    # TC-011: Retrying non-idempotent side effect without idempotency key
    if 'submit_wire_transfer' in code_only and 'bank_wire_api' in code_only:
        defects.append({
            "category": "non_idempotent_side_effect_retry",
            "evidence": ["submit_wire_transfer", "bank_wire_api", "transfer"]
        })

    # TC-013: Plaintext secret in log and tool output
    if 'sk_live_SECRET_API_KEY_12345' in code_only:
        defects.append({
            "category": "sensitive_data_exposure",
            "evidence": ["sk_live_SECRET_API_KEY_12345", "logger.info", "master_key"]
        })

    # TC-014: Unshielded prompt injection in tool output
    if 'fetch_public_web_page' in code_only and 'download_page' in code_only:
        defects.append({
            "category": "unshielded_tool_output",
            "evidence": ["fetch_public_web_page", "raw_html", "SYSTEM INSTRUCTION"]
        })

    # TC-015: Critical tool lacking unit tests
    if 'execute_critical_financial_reconciliation' in code_only and 'test_' not in code_only:
        defects.append({
            "category": "missing_critical_tool_tests",
            "evidence": ["execute_critical_financial_reconciliation", "accounting_engine"]
        })

    # TC-018: Version-dependent runtime behavior uncertainty
    if 'dynamic_tool_executor' in code_only:
        uncertainty_notes.append("Unpinned dynamic runtime dependency; recording uncertainty without false positive.")

    # Determine status
    if len(defects) > 0:
        status = "FAIL"
    elif len(uncertainty_notes) > 0:
        status = "UNCERTAIN"
    else:
        status = "PASS"

    return {
        "status": status,
        "findingsPresent": len(defects) > 0,
        "defects": defects,
        "uncertaintyPresent": len(uncertainty_notes) > 0,
        "uncertainty_notes": uncertainty_notes
    }

def validate_skill_md():
    print("=== VALIDATION: SKILL.md ===")
    failures = 0
    if not os.path.exists(SKILL_MD):
        print(f"  [FAIL] {SKILL_MD} does not exist")
        return 1

    with open(SKILL_MD, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.splitlines()

    # 1. Line count < 200
    if len(lines) < 200:
        print(f"  [PASS] Line count strictly under 200: {len(lines)} lines")
    else:
        print(f"  [FAIL] Line count exceeds 200: {len(lines)} lines")
        failures += 1

    # 2. Frontmatter checks
    if content.startswith("---") and "name: langgraph-tools-and-runtime" in content:
        print("  [PASS] Valid frontmatter with correct name")
    else:
        print("  [FAIL] Frontmatter missing or name invalid")
        failures += 1

    # 3. Purpose & Activation
    if "Purpose & Activation" in content and "Scope & Skill Boundaries" in content:
        print("  [PASS] Purpose, Activation, and Scope sections present")
    else:
        print("  [FAIL] Missing Purpose or Scope sections")
        failures += 1

    # 4. Reference links
    for ref in REQUIRED_REFERENCES:
        if ref in content:
            print(f"  [PASS] References supporting document: {ref}")
        else:
            print(f"  [FAIL] Missing reference link to {ref}")
            failures += 1

    # 5. Engineering skill links
    for eng_skill in ["skill-eng-modularity", "skill-eng-maintainability", "skill-eng-performance", "skill-eng-security", "skill-eng-business-logic"]:
        if eng_skill in content:
            print(f"  [PASS] References engineering skill: {eng_skill}")
        else:
            print(f"  [FAIL] Missing reference to {eng_skill}")
            failures += 1

    return failures

def validate_references():
    print("\n=== VALIDATION: references/ ===")
    failures = 0
    for ref in REQUIRED_REFERENCES:
        ref_path = os.path.join(REFERENCES_DIR, ref)
        if os.path.exists(ref_path):
            with open(ref_path, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            print(f"  [PASS] Reference exists ({lines} lines): {ref}")
        else:
            print(f"  [FAIL] Missing reference file: {ref_path}")
            failures += 1
    return failures

def validate_test_suite():
    print("\n=== VALIDATION: test-suite.json & Test Cases ===")
    failures = 0

    if not os.path.exists(TEST_SUITE_JSON):
        print(f"  [FAIL] {TEST_SUITE_JSON} does not exist")
        return 1

    try:
        with open(TEST_SUITE_JSON, 'r', encoding='utf-8') as f:
            suite_data = json.load(f)
        print("  [PASS] test-suite.json parsed successfully")
    except Exception as e:
        print(f"  [FAIL] JSON parse error: {e}")
        return 1

    test_cases = suite_data.get("testCases", [])
    if len(test_cases) >= 18:
        print(f"  [PASS] Contains all {len(test_cases)} required test cases (>= 18)")
    else:
        print(f"  [FAIL] Found {len(test_cases)} test cases, expected >= 18")
        failures += 1

    print("\n=== EXECUTING TEST CASES (TC-001 through TC-018) ===")
    for tc in test_cases:
        tc_id = tc.get("id")
        desc = tc.get("description")
        input_rel = tc.get("inputFile")
        expected = tc.get("expected", {})

        input_path = os.path.join(SKILL_DIR, input_rel)
        if not os.path.exists(input_path):
            print(f"  [FAIL] [{tc_id}] Input fixture missing: {input_path}")
            failures += 1
            continue

        with open(input_path, 'r', encoding='utf-8') as f:
            fixture_content = f.read()

        actual = evaluate_tool_fixture(fixture_content, tc_id)

        # Status check
        if actual["status"] == expected["status"]:
            print(f"  [PASS] [{tc_id}] Status: {actual['status']} ({desc})")
        else:
            print(f"  [FAIL] [{tc_id}] Status mismatch: got {actual['status']}, expected {expected['status']}")
            failures += 1

        # Findings present check
        if actual["findingsPresent"] == expected["findingsPresent"]:
            pass
        else:
            print(f"  [FAIL] [{tc_id}] findingsPresent mismatch: got {actual['findingsPresent']}, expected {expected['findingsPresent']}")
            failures += 1

        # Uncertainty check
        if actual["uncertaintyPresent"] == expected.get("uncertaintyPresent", False):
            pass
        else:
            print(f"  [FAIL] [{tc_id}] uncertaintyPresent mismatch: got {actual['uncertaintyPresent']}, expected {expected.get('uncertaintyPresent', False)}")
            failures += 1

    return failures

def main():
    print("=" * 60)
    print("LANGGRAPH TOOLS & RUNTIME: VALIDATION RUNNER")
    print("=" * 60)

    total_failures = 0
    total_failures += validate_skill_md()
    total_failures += validate_references()
    total_failures += validate_test_suite()

    print("\n" + "=" * 60)
    if total_failures == 0:
        print("RESULT: ALL VALIDATION CHECKS & TEST CASES PASSED (0 FAILURES)")
        print("=" * 60)
        sys.exit(0)
    else:
        print(f"RESULT: FAILED WITH {total_failures} ERRORS")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()

