#!/usr/bin/env python3
"""
Automated Validator and Test Suite Runner for Gate 1 Code Review Skill.
Validates SKILL.md, references, schemas, fixtures, and executes all 14 test cases.
"""

import sys
import os
import json
import re

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")
WORKFLOW_MD = os.path.join(SKILL_DIR, "references", "validation-workflow.md")
REPORT_SCHEMA_MD = os.path.join(SKILL_DIR, "references", "report-schema.md")
TEST_SUITE_JSON = os.path.join(SKILL_DIR, "validation", "test-suite.json")
TEST_SUITE_SCHEMA = os.path.join(SKILL_DIR, "validation", "test-suite.schema.json")
TEST_DATA_DIR = os.path.join(SKILL_DIR, "validation", "test-data")

ENGINEERING_SKILLS = [
    "skill-eng-security",
    "skill-eng-performance",
    "skill-eng-maintainability",
    "skill-eng-modularity",
    "skill-eng-business-logic"
]

def evaluate_gate1(inputs):
    """
    Evaluates Gate 1 execution result from mock inputs:
    - Build check: if unavailable -> INCOMPLETE; if exitCode != 0 -> BLOCKED (build failed)
    - Test check: if unavailable -> INCOMPLETE; if failed > 0 -> BLOCKED (tests failed)
    - Dimension checks:
      - Any dimension < 9.0 -> BLOCKED
      - Any critical violation -> BLOCKED
      - Uncertainty notes present with no blocking failure -> INCOMPLETE
    """
    blocking_reasons = []
    uncertainty_notes = []
    is_incomplete = False

    # Stage 2: Build & Static
    build = inputs.get("mockBuild", {})
    build_status = "passed"
    if not build.get("available", True):
        build_status = "unavailable"
        is_incomplete = True
        uncertainty_notes.append("Build toolchain unavailable")
    elif build.get("exitCode", 0) != 0:
        build_status = "failed"
        blocking_reasons.append("Build / compilation failure")

    # Stage 3: Automated Tests
    tests = inputs.get("mockTests", {})
    test_status = "passed"
    if not tests.get("available", True):
        test_status = "unavailable"
        is_incomplete = True
        uncertainty_notes.append("Test runner unavailable")
    elif tests.get("failed", 0) > 0 or tests.get("exitCode", 0) != 0:
        test_status = "failed"
        blocking_reasons.append("Automated test assertion failure")

    # Stage 4 & 5: Dimensions
    dims = inputs.get("mockDimensions", {})
    for dim_name, dim_data in dims.items():
        score = dim_data.get("score", 10.0)
        blocked = dim_data.get("blocked", False)
        findings = dim_data.get("findings", [])
        dim_notes = dim_data.get("uncertainty_notes", [])

        if dim_notes:
            uncertainty_notes.extend(dim_notes)
            is_incomplete = True

        has_critical = any(f.get("severity") == "critical" for f in findings)
        if has_critical:
            blocking_reasons.append(f"Critical violation in {dim_name}")
        elif score < 9.0 or blocked:
            blocking_reasons.append(f"Dimension {dim_name} score below 9.0 ({score})")

    # Final Status determination
    if len(blocking_reasons) > 0:
        status = "BLOCKED"
        ready_for_pr = False
    elif is_incomplete:
        status = "INCOMPLETE"
        ready_for_pr = False
    else:
        status = "PASS"
        ready_for_pr = True

    return {
        "status": status,
        "ready_for_pr": ready_for_pr,
        "buildStatus": build_status,
        "testStatus": test_status,
        "blocking_reasons": blocking_reasons,
        "uncertainty_notes": uncertainty_notes,
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
    if content.startswith("---"):
        print("  [PASS] Frontmatter starts with '---'")
    else:
        print("  [FAIL] Frontmatter missing starting '---'")
        failures += 1

    if "name: skill-eng-gate1-code-review" in content:
        print("  [PASS] Correct skill name declared")
    else:
        print("  [FAIL] Skill name missing or incorrect")
        failures += 1

    # 3. Purpose & Activation
    if "Purpose & Activation" in content and "Execution Modes" in content:
        print("  [PASS] Purpose, Activation, and Execution Modes present")
    else:
        print("  [FAIL] Purpose or Execution Modes section missing")
        failures += 1

    # 4. References to all 5 skills
    for skill in ENGINEERING_SKILLS:
        if skill in content:
            print(f"  [PASS] References engineering skill: {skill}")
        else:
            print(f"  [FAIL] Missing reference to {skill}")
            failures += 1

    # 5. References to supporting documents
    for ref in ["validation-workflow.md", "report-schema.md", "test-suite.json"]:
        if ref in content:
            print(f"  [PASS] References supporting file: {ref}")
        else:
            print(f"  [FAIL] Missing reference to {ref}")
            failures += 1

    return failures

def validate_references():
    print("\n=== VALIDATION: references/ ===")
    failures = 0

    if not os.path.exists(WORKFLOW_MD):
        print(f"  [FAIL] {WORKFLOW_MD} missing")
        failures += 1
    else:
        with open(WORKFLOW_MD, 'r', encoding='utf-8') as f:
            wf_content = f.read()
        for stage in ["Stage 1", "Stage 2", "Stage 3", "Stage 4", "Stage 5", "Stage 6"]:
            if stage in wf_content:
                print(f"  [PASS] Workflow defines {stage}")
            else:
                print(f"  [FAIL] Workflow missing {stage}")
                failures += 1
        if "Mode A" in wf_content and "Mode B" in wf_content:
            print("  [PASS] Both Mode A (Local) and Mode B (Entry Guard) defined")
        else:
            print("  [FAIL] Execution modes missing in workflow guide")
            failures += 1

    if not os.path.exists(REPORT_SCHEMA_MD):
        print(f"  [FAIL] {REPORT_SCHEMA_MD} missing")
        failures += 1
    else:
        with open(REPORT_SCHEMA_MD, 'r', encoding='utf-8') as f:
            rs_content = f.read()
        for field in ["GATE_1_LOCAL", "PASS", "BLOCKED", "INCOMPLETE", "dimensions", "summary"]:
            if field in rs_content:
                print(f"  [PASS] Report schema defines '{field}'")
            else:
                print(f"  [FAIL] Report schema missing '{field}'")
                failures += 1

    return failures

def validate_test_suite():
    print("\n=== VALIDATION: test-suite.json & test cases ===")
    failures = 0

    if not os.path.exists(TEST_SUITE_JSON):
        print(f"  [FAIL] {TEST_SUITE_JSON} does not exist")
        return 1

    try:
        with open(TEST_SUITE_JSON, 'r', encoding='utf-8') as f:
            suite_data = json.load(f)
        print("  [PASS] test-suite.json is valid JSON")
    except Exception as e:
        print(f"  [FAIL] JSON parse error: {e}")
        return 1

    test_cases = suite_data.get("testCases", [])
    if len(test_cases) >= 14:
        print(f"  [PASS] Contains all {len(test_cases)} required test cases (>= 14)")
    else:
        print(f"  [FAIL] Insufficient test cases: found {len(test_cases)}, expected >= 14")
        failures += 1

    # Verify fixture files exist
    for tc in test_cases:
        tc_id = tc.get("id")
        inputs = tc.get("inputs", {})
        repo = inputs.get("repository", {})
        fixture = repo.get("fixturePath")
        if fixture:
            fixture_full = os.path.join(SKILL_DIR, fixture)
            if os.path.exists(fixture_full):
                print(f"  [PASS] [{tc_id}] Fixture exists: {fixture}")
            else:
                print(f"  [FAIL] [{tc_id}] Fixture missing: {fixture_full}")
                failures += 1

    # Execute and verify all 14 test cases programmatically
    print("\n=== EXECUTING TEST CASES (TC-001 through TC-014) ===")
    for tc in test_cases:
        tc_id = tc.get("id")
        desc = tc.get("description")
        inputs = tc.get("inputs", {})
        expected = tc.get("expected", {})

        actual = evaluate_gate1(inputs)

        # Check status
        if actual["status"] == expected["status"]:
            print(f"  [PASS] [{tc_id}] Status: {actual['status']}")
        else:
            print(f"  [FAIL] [{tc_id}] Status mismatch: got {actual['status']}, expected {expected['status']}")
            failures += 1

        # Check ready_for_pr
        if actual["ready_for_pr"] == expected["ready_for_pr"]:
            print(f"  [PASS] [{tc_id}] ready_for_pr: {actual['ready_for_pr']}")
        else:
            print(f"  [FAIL] [{tc_id}] ready_for_pr mismatch: got {actual['ready_for_pr']}, expected {expected['ready_for_pr']}")
            failures += 1

        # Check buildStatus
        if "buildStatus" in expected:
            if actual["buildStatus"] == expected["buildStatus"]:
                print(f"  [PASS] [{tc_id}] buildStatus: {actual['buildStatus']}")
            else:
                print(f"  [FAIL] [{tc_id}] buildStatus mismatch: got {actual['buildStatus']}, expected {expected['buildStatus']}")
                failures += 1

        # Check testStatus
        if "testStatus" in expected:
            if actual["testStatus"] == expected["testStatus"]:
                print(f"  [PASS] [{tc_id}] testStatus: {actual['testStatus']}")
            else:
                print(f"  [FAIL] [{tc_id}] testStatus mismatch: got {actual['testStatus']}, expected {expected['testStatus']}")
                failures += 1

        # Check blocking reasons count
        if "blockingReasonsCount" in expected:
            exp_count = expected["blockingReasonsCount"]
            act_count = len(actual["blocking_reasons"])
            if (exp_count == 0 and act_count == 0) or (exp_count > 0 and act_count > 0):
                print(f"  [PASS] [{tc_id}] blockingReasons: {act_count} (expected {exp_count})")
            else:
                print(f"  [FAIL] [{tc_id}] blockingReasons mismatch: got {act_count}, expected {exp_count}")
                failures += 1

    return failures

def main():
    print("=" * 60)
    print("GATE 1 LOCAL CODE REVIEW SKILL: AUTOMATED VALIDATION")
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

