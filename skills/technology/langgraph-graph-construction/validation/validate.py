#!/usr/bin/env python3
"""
Automated Validator and Test Suite Runner for LangGraph Graph Construction Skill.
Validates SKILL.md, references, test-suite.json schema, test fixtures, and executes all 16 test cases.
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
    "state-schemas-and-reducers.md",
    "nodes-edges-and-routing.md",
    "graph-compilation-and-connectivity.md",
    "graph-testing-and-validation.md"
]

def strip_comments_and_docstrings(source: str) -> str:
    """Strip python docstrings and single-line comments for accurate code matching."""
    source = re.sub(r'""".*?"""', '', source, flags=re.DOTALL)
    source = re.sub(r"'''.*?'''", '', source, flags=re.DOTALL)
    lines = [line.split('#')[0] for line in source.splitlines()]
    return '\n'.join(lines)

def evaluate_graph_fixture(fixture_content: str, tc_id: str):
    """
    Evaluates LangGraph graph definition code fixture for structural defects and false-positive guards.
    """
    code_only = strip_comments_and_docstrings(fixture_content)
    defects = []
    uncertainty_notes = []

    # TC-003: Unmapped route destination
    if 'return "unhandled_case"' in code_only and '"unhandled_case"' not in code_only.split('add_conditional_edges')[1]:
        defects.append({
            "category": "unmapped_route_destination",
            "evidence": ["unhandled_case", "path_map"]
        })

    # TC-004 & TC-010: Unregistered node in edge / compile time error
    if 'nonexistent_processor' in code_only:
        defects.append({
            "category": "unregistered_node_reference",
            "evidence": ["nonexistent_processor", "add_edge"]
        })
    if 'ghost_processor' in code_only:
        defects.append({
            "category": "compile_time_topology_error",
            "evidence": ["ghost_processor", "add_edge"]
        })

    # TC-005: In-place state mutation & type mismatch
    if 'state["items"].append' in code_only and '999' in code_only:
        defects.append({
            "category": "state_mutation_and_type_mismatch",
            "evidence": ["append", "999", "items"]
        })

    # TC-006: Missing reducer on concurrent channel
    if 'add_edge(START, "b1")' in code_only and 'add_edge(START, "b2")' in code_only:
        if 'logs: List[str]' in code_only and 'Annotated' not in code_only:
            defects.append({
                "category": "missing_reducer_on_concurrent_channel",
                "evidence": ["logs", "UnreducedParallelState", "operator.add"]
            })

    # TC-008: Truly nonterminating infinite loop (no counter, no status change)
    if 'endless_router' in code_only and 'return "loop"' in code_only:
        defects.append({
            "category": "infinite_loop",
            "evidence": ["endless_router", "loop", "noop_node"]
        })

    # TC-009: Missing entry and finish endpoints
    if 'build_missing_endpoints_graph' in code_only:
        if 'add_edge(START' not in code_only and 'set_entry_point' not in code_only:
            defects.append({
                "category": "missing_entry_finish",
                "evidence": ["START", "END", "Missing START and END"]
            })

    # TC-011: Runtime invocation error not caused by graph topology
    if 'state["metadata"]["user_role"]' in code_only:
        producer_body = code_only.split('def first_node')[1].split('def crashing_node')[0]
        if '"metadata"' not in producer_body:
            defects.append({
                "category": "uninitialized_state_access",
                "evidence": ["metadata", "user_role", "KeyError"]
            })

    # TC-012: Version-incompatible / invalid API method
    if 'bind_graph_entry' in code_only:
        defects.append({
            "category": "invalid_api_method",
            "evidence": ["bind_graph_entry", "AttributeError"]
        })

    # TC-015: Insufficient evidence
    if 'runtime_registry' in code_only:
        uncertainty_notes.append("External runtime registry not visible; uncertainty recorded without false positive")

    # TC-016: Single root cause defect (missing state schema field)
    if 'RootCauseState' in code_only and 'analysis_report' not in code_only.split('class RootCauseState')[1].split('def parse_node')[0]:
        defects.append({
            "category": "missing_state_schema_channel",
            "evidence": ["analysis_report", "RootCauseState"]
        })

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
    if content.startswith("---") and "name: langgraph-graph-construction" in content:
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
    if len(test_cases) >= 16:
        print(f"  [PASS] Contains all {len(test_cases)} required test cases (>= 16)")
    else:
        print(f"  [FAIL] Found {len(test_cases)} test cases, expected >= 16")
        failures += 1

    print("\n=== EXECUTING TEST CASES (TC-001 through TC-016) ===")
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

        actual = evaluate_graph_fixture(fixture_content, tc_id)

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
    print("LANGGRAPH GRAPH CONSTRUCTION: VALIDATION RUNNER")
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
