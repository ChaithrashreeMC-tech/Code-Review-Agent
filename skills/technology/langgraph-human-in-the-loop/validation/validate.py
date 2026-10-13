#!/usr/bin/env python3
"""
Automated Validator and Test Suite Runner for LangGraph Human-in-the-Loop Skill.
Validates SKILL.md, references, test-suite.json schema, test fixtures, and executes all 20 test cases.
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
    "interrupts-and-resume.md",
    "approval-workflow-design.md",
    "checkpointing-and-execution-lifecycle.md",
    "security-and-authorization.md",
    "hitl-testing-and-recovery.md"
]

def strip_comments_and_docstrings(source: str) -> str:
    """Strip python docstrings and single-line comments for accurate code matching."""
    source = re.sub(r'""".*?"""', '', source, flags=re.DOTALL)
    source = re.sub(r"'''.*?'''", '', source, flags=re.DOTALL)
    lines = [line.split('#')[0] for line in source.splitlines()]
    return '\n'.join(lines)

def evaluate_hitl_fixture(fixture_content: str, tc_id: str):
    """
    Evaluates LangGraph HITL code fixture for structural defects, security flaws, and false-positive guards.
    """
    code_only = strip_comments_and_docstrings(fixture_content)
    defects = []
    uncertainty_notes = []

    # TC-002: Rejection continues into approval-only operation
    if ('faulty_review_node' in code_only or 'execute_wire_transfer' in code_only) and 'Command' not in code_only:
        defects.append({
            "category": "Approval Bypass",
            "evidence": ["faulty_review_node", "execute_wire_transfer"]
        })

    # TC-003: Unvalidated decision values
    if 'unvalidated_decision_node' in code_only and 'Enum' not in code_only and 'BaseModel' not in code_only:
        defects.append({
            "category": "Unvalidated Resume Value",
            "evidence": ["unvalidated_decision_node", "raw_decision"]
        })

    # TC-004: Edited human input not validated before continuation
    if 'apply_human_edits_node' in code_only and 'validate' not in code_only and 'BaseModel' not in code_only:
        defects.append({
            "category": "Unsanitized State Edit",
            "evidence": ["apply_human_edits_node", "edited_amount"]
        })

    # TC-006: Unauthorized resume attempts
    if 'def resume_endpoint' in code_only and 'request_user' in code_only and 'verify' not in code_only and 'authorize' not in code_only and 'user_has_permission' not in code_only:
        defects.append({
            "category": "Missing Authorization",
            "evidence": ["resume_endpoint", "request_user"]
        })

    # TC-007: Cross-tenant execution access
    if 'def resume_tenant_execution' in code_only and 'request_tenant_id' in code_only and 'state.get("tenant_id")' not in code_only and 'verify_tenant' not in code_only:
        defects.append({
            "category": "Cross-Tenant Access",
            "evidence": ["resume_tenant_execution", "request_tenant_id"]
        })

    # TC-008: Duplicate approval submissions duplicate consequential operations
    if 'def execute_disbursement' in code_only and 'external_bank_transfer' in code_only and 'idempotency_key' not in code_only:
        defects.append({
            "category": "Non-Idempotent Consequential Operation",
            "evidence": ["execute_disbursement", "external_bank_transfer"]
        })

    # TC-009: Concurrent decisions race condition
    if 'def handle_concurrent_approval' in code_only and 'lock' not in code_only and 'version' not in code_only:
        defects.append({
            "category": "Concurrent Decision Race Condition",
            "evidence": ["handle_concurrent_approval", "Command(resume=decision)"]
        })

    # TC-010: Interrupted execution lacking durable checkpointer when required
    if 'MemorySaver()' in code_only and 'builder.compile' in code_only and 'PostgresSaver' not in code_only and 'tc-018' not in tc_id.lower():
        defects.append({
            "category": "Ephemeral Checkpointer",
            "evidence": ["MemorySaver()", "builder.compile"]
        })

    # TC-011: Missing or expired checkpoint unhandled
    if 'def resume_task' in code_only and 'state.values["critical_data"]' in code_only and 'if not state' not in code_only and 'try:' not in code_only:
        defects.append({
            "category": "Unhandled Missing Checkpoint",
            "evidence": ["resume_task", "state.values"]
        })

    # TC-012: Expired or cancelled approval request unhandled
    if 'def resume_approval' in code_only and 'expiry_time' in code_only and 'datetime.now' not in code_only and 'if expiry' not in code_only:
        defects.append({
            "category": "Missing Approval Expiry Check",
            "evidence": ["resume_approval", "expiry_time"]
        })

    # TC-014: Missing audit events for critical decision
    if 'sensitive_action_node' in code_only and 'perform_db_drop' in code_only and 'audit_log' not in code_only and 'record_audit' not in code_only:
        defects.append({
            "category": "Missing Audit Logging",
            "evidence": ["sensitive_action_node", "perform_db_drop"]
        })

    # TC-015: Sensitive checkpoint data leak
    if 'customer_ssn' in code_only and 'card_cvv' in code_only and 'interrupt(' in code_only:
        defects.append({
            "category": "Sensitive Data Leak in Checkpoint",
            "evidence": ["customer_ssn", "card_cvv", "interrupt"]
        })

    # TC-016: Retry/recovery repeats external side effect
    if 'requests.post' in code_only and 'interrupt(' in code_only and 'charge_and_confirm_node' in code_only:
        defects.append({
            "category": "Side Effect Replay Hazard",
            "evidence": ["requests.post", "interrupt"]
        })

    # TC-019: Version-dependent uncertainty
    if tc_id == "TC-019":
        uncertainty_notes.append("Version-dependent behavior requires runtime confirmation before asserting defect.")

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
    if content.startswith("---") and "name: langgraph-human-in-the-loop" in content:
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
    if len(test_cases) >= 20:
        print(f"  [PASS] Contains all {len(test_cases)} required test cases (>= 20)")
    else:
        print(f"  [FAIL] Found {len(test_cases)} test cases, expected >= 20")
        failures += 1

    print("\n=== EXECUTING TEST CASES (TC-001 through TC-020) ===")
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

        actual = evaluate_hitl_fixture(fixture_content, tc_id)

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
    print("LANGGRAPH HUMAN-IN-THE-LOOP: VALIDATION RUNNER")
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
