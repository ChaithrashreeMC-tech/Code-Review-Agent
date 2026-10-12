#!/usr/bin/env python3
"""
Validation script for skill-eng-security.
Checks structure, line limits, frontmatter, rule definitions, checklists, scoring guides,
test suite integrity, test data files, and cross-file rule consistency.
"""

import sys
import os
import json
import re

# Rule IDs to check
SEC_RULES = [f"SEC{i:02d}" for i in range(1, 13)]

def validate_skill_md(skill_path):
    print("=== VALIDATION: SKILL.md ===")
    failures = 0

    if not os.path.exists(skill_path):
        print(f"  [FAIL] {skill_path} does not exist")
        return 1

    with open(skill_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    line_count = len(lines)
    if line_count < 200:
        print(f"  [PASS] SKILL.md strictly under 200 lines: {line_count} lines")
    else:
        print(f"  [FAIL] SKILL.md exceeds 200 lines: {line_count} lines")
        failures += 1

    content = "".join(lines)

    if content.startswith("---"):
        print("  [PASS] Frontmatter starts with ---")
    else:
        print("  [FAIL] Frontmatter missing starting ---")
        failures += 1

    if "name: skill-eng-security" in content:
        print("  [PASS] name: skill-eng-security")
    else:
        print("  [FAIL] name: skill-eng-security missing")
        failures += 1

    if "description: >-" in content:
        print("  [PASS] Folded description (>-)")
    else:
        print("  [FAIL] Folded description (>-) missing")
        failures += 1

    if "Activate when" in content:
        print("  [PASS] Activation clause")
    else:
        print("  [FAIL] Activation clause missing")
        failures += 1

    # Check prohibited frontmatter keys
    for prohibited in ["license:", "compatibility:", "metadata:"]:
        if prohibited in content:
            print(f"  [FAIL] Prohibited frontmatter key found: {prohibited}")
            failures += 1
        else:
            print(f"  [PASS] No prohibited: {prohibited[:-1]}")

    # Check reference links
    for ref in ["checklist.md", "scoring-guide.md", "test-suite.json"]:
        if ref in content:
            print(f"  [PASS] Reference: {ref}")
        else:
            print(f"  [FAIL] Reference missing: {ref}")
            failures += 1

    # Check description length
    desc_match = re.search(r"description: >-\n(.*?)(?=\n\w+:|\n---)", content, re.DOTALL)
    if desc_match:
        desc_text = desc_match.group(1).strip()
        if len(desc_text) <= 1024:
            print(f"  [PASS] Description <= 1024 chars: {len(desc_text)} chars")
        else:
            print(f"  [FAIL] Description exceeds 1024 chars: {len(desc_text)} chars")
            failures += 1

    # Check for all SEC rules in SKILL.md
    all_rules_present = True
    for rule in SEC_RULES:
        if rule not in content:
            print(f"  [FAIL] Rule missing in SKILL.md: {rule}")
            failures += 1
            all_rules_present = False

    if all_rules_present:
        print("  [PASS] All 12 rule IDs in SKILL.md")

    if "| ID | Rule | Objective |" in content:
        print("  [PASS] Compact table format present")
    else:
        print("  [FAIL] Compact table format missing")
        failures += 1

    return failures


def validate_checklist_md(checklist_path):
    print("\n=== VALIDATION: references/checklist.md ===")
    failures = 0

    if not os.path.exists(checklist_path):
        print(f"  [FAIL] {checklist_path} does not exist")
        return 1

    with open(checklist_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for rule in SEC_RULES:
        if rule in content:
            print(f"  [PASS] {rule} covered in checklist.md")
        else:
            print(f"  [FAIL] {rule} missing in checklist.md")
            failures += 1

    per_rule_fields = [
        "Objective & Scope",
        "Detection Criteria",
        "Evidence Requirements",
        "False-Positive Guidance",
        "Severity Guidance",
        "Remediation Guidance"
    ]

    for field in per_rule_fields:
        count = content.count(field)
        if count >= 12:
            print(f"  [PASS] Checklist field '{field}' appears 12 times: Found {count}")
        else:
            print(f"  [FAIL] Checklist field '{field}' appears fewer than 12 times: Found {count}")
            failures += 1

    if "Technology Adaptation" in content:
        print("  [PASS] Consolidated 'Technology Adaptation' section present")
    else:
        print("  [FAIL] 'Technology Adaptation' section missing")
        failures += 1

    return failures


def validate_scoring_guide_md(scoring_path):
    print("\n=== VALIDATION: references/scoring-guide.md ===")
    failures = 0

    if not os.path.exists(scoring_path):
        print(f"  [FAIL] {scoring_path} does not exist")
        return 1

    with open(scoring_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for rule in SEC_RULES:
        if rule in content:
            print(f"  [PASS] {rule} referenced in scoring-guide.md")
        else:
            print(f"  [FAIL] {rule} missing in scoring-guide.md")
            failures += 1

    required_phrases = [
        "Severity Classification",
        "Score Calculation",
        "Scorecard Aggregator",
        "Blocking"
    ]

    for phrase in required_phrases:
        if phrase in content:
            print(f"  [PASS] Required section/concept present: '{phrase}'")
        else:
            print(f"  [FAIL] Missing section/concept: '{phrase}'")
            failures += 1

    if "90" in content or "9/10" in content:
        print("  [PASS] Standardized blocking threshold present (90/100 or 9/10)")
    else:
        print("  [FAIL] Standardized blocking threshold missing (90/100 or 9/10)")
        failures += 1

    if "critical" in content.lower() and "block" in content.lower():
        print("  [PASS] Critical violation override defined in scoring guide")
    else:
        print("  [FAIL] Critical violation override missing in scoring guide")
        failures += 1

    return failures


def validate_test_suite_json(test_suite_path, base_dir):
    print("\n=== VALIDATION: test-suite.json ===")
    failures = 0

    if not os.path.exists(test_suite_path):
        print(f"  [FAIL] {test_suite_path} does not exist")
        return 1

    try:
        with open(test_suite_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("  [PASS] Valid JSON")
    except Exception as e:
        print(f"  [FAIL] Invalid JSON in {test_suite_path}: {e}")
        return 1

    test_cases = data.get("testCases", [])
    if test_cases:
        print(f"  [PASS] testCases array present: {len(test_cases)} test cases")
    else:
        print("  [FAIL] testCases array missing or empty")
        failures += 1

    # Check all SEC rules are covered
    covered_rules = set()
    violation_rules = set()
    for tc in test_cases:
        rids = tc.get("ruleIds", [])
        for rid in rids:
            covered_rules.add(rid)
        if tc.get("expected", {}).get("findingsPresent") is True:
            for rid in rids:
                violation_rules.add(rid)

    missing_coverage = set(SEC_RULES) - covered_rules
    if not missing_coverage:
        print("  [PASS] All 12 SEC rules covered in testCases")
    else:
        print(f"  [FAIL] Missing rule coverage: {missing_coverage}")
        failures += 1

    missing_violations = set(SEC_RULES) - violation_rules
    if not missing_violations:
        print("  [PASS] All 12 SEC rules have violation test cases")
    else:
        print(f"  [FAIL] Missing violation test cases for: {missing_violations}")
        failures += 1

    # Check test-data file existence, target functions, evidence, and scoreImpacts
    print("\n=== VALIDATION: test-data files and test case integrity ===")
    for tc in test_cases:
        tc_id = tc.get("id")
        input_file = tc.get("inputFile")
        full_file_path = os.path.join(base_dir, input_file) if input_file else None

        if not full_file_path or not os.path.exists(full_file_path):
            print(f"  [FAIL] {tc_id}: Input file missing ({input_file})")
            failures += 1
            continue

        with open(full_file_path, 'r', encoding='utf-8') as tf:
            file_content = tf.read()

        # Check target function / class presence
        target_fn = tc.get("targetFunction")
        if target_fn and target_fn in file_content:
            print(f"  [PASS] {tc_id}: Target function/symbol '{target_fn}' verified in {os.path.basename(input_file)}")
        elif target_fn:
            print(f"  [FAIL] {tc_id}: Target function/symbol '{target_fn}' missing in {os.path.basename(input_file)}")
            failures += 1

        # Check safe counterpart
        safe_cp = tc.get("safeCounterpart", {})
        safe_fn = safe_cp.get("targetFunction")
        if safe_fn and safe_fn in file_content:
            print(f"  [PASS] {tc_id}: Safe counterpart '{safe_fn}' verified")
        elif safe_fn:
            print(f"  [FAIL] {tc_id}: Safe counterpart '{safe_fn}' missing in {os.path.basename(input_file)}")
            failures += 1

        # Check findings evidence and scoreImpact
        expected = tc.get("expected", {})
        if expected.get("findingsPresent"):
            for finding in expected.get("findings", []):
                rule_id = finding.get("ruleId")
                score_impact = finding.get("scoreImpact")

                # Verify scoreImpact is on 0-10 scale (-2.5 <= scoreImpact <= -0.1)
                if isinstance(score_impact, (int, float)) and -2.5 <= score_impact <= -0.1:
                    print(f"  [PASS] {tc_id} ({rule_id}): scoreImpact {score_impact} on direct 0-10 scale")
                else:
                    print(f"  [FAIL] {tc_id} ({rule_id}): scoreImpact {score_impact} invalid for 0-10 scale")
                    failures += 1

                # Verify evidence contains strings exist in test file
                for ev in finding.get("evidenceContains", []):
                    if ev in file_content:
                        print(f"  [PASS] {tc_id} ({rule_id}): Evidence string '{ev}' present in test data")
                    else:
                        print(f"  [FAIL] {tc_id} ({rule_id}): Evidence string '{ev}' missing in test data")
                        failures += 1

    return failures


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skill_md = os.path.join(base_dir, "SKILL.md")
    checklist_md = os.path.join(base_dir, "references", "checklist.md")
    scoring_guide_md = os.path.join(base_dir, "references", "scoring-guide.md")
    test_suite_json = os.path.join(base_dir, "validation", "test-suite.json")

    total_failures = 0
    total_failures += validate_skill_md(skill_md)
    total_failures += validate_checklist_md(checklist_md)
    total_failures += validate_scoring_guide_md(scoring_guide_md)
    total_failures += validate_test_suite_json(test_suite_json, base_dir)

    print("\n=== SUMMARY ===")
    print(f"Total failures: {total_failures}")
    if total_failures == 0:
        print("All validation checks passed.")
        sys.exit(0)
    else:
        print("Validation failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()

