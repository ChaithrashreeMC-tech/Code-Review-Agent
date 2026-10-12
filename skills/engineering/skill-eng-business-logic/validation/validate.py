#!/usr/bin/env python3
"""
Validation script for skill-eng-business-logic.
Checks structure, line limits, frontmatter, rule definitions, checklists, scoring guides,
test suite integrity, test data files, and cross-file rule consistency.
"""

import sys
import os
import json
import re

# Rule IDs to check
BIZ_RULES = [f"BIZ{i:02d}" for i in range(1, 11)]

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

    if "name: skill-eng-business-logic" in content:
        print("  [PASS] name: skill-eng-business-logic")
    else:
        print("  [FAIL] name: skill-eng-business-logic missing")
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

    # Check for all BIZ rules in SKILL.md
    all_rules_present = True
    for rule in BIZ_RULES:
        if rule not in content:
            print(f"  [FAIL] Rule missing in SKILL.md: {rule}")
            failures += 1
            all_rules_present = False

    if all_rules_present:
        print(f"  [PASS] All {len(BIZ_RULES)} rule IDs in SKILL.md")

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

    for rule in BIZ_RULES:
        if rule in content:
            print(f"  [PASS] {rule} covered in checklist.md")
        else:
            print(f"  [FAIL] {rule} missing in checklist.md")
            failures += 1

    per_rule_fields = [
        "Purpose:",
        "Detect:",
        "Evidence:",
        "Avoid:",
        "Remediation:",
        "Severity:"
    ]

    for field in per_rule_fields:
        count = content.count(field)
        if count >= len(BIZ_RULES):
            print(f"  [PASS] Checklist field '{field}' appears >= {len(BIZ_RULES)} times: Found {count}")
        else:
            print(f"  [FAIL] Checklist field '{field}' appears fewer than {len(BIZ_RULES)} times: Found {count}")
            failures += 1

    if "Specification Discovery & Uncertainty Protocol" in content or "Disambiguation & Boundary Rules" in content:
        print("  [PASS] Guidance / boundary section present")
    else:
        print("  [FAIL] Guidance / boundary section missing")
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

    for rule in BIZ_RULES:
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
    if len(test_cases) >= 14:
        print(f"  [PASS] testCases array present with all 14 required cases: {len(test_cases)} test cases")
    else:
        print(f"  [FAIL] testCases array missing or fewer than 14 test cases: {len(test_cases)}")
        failures += 1

    # Check test-data file existence
    print("\n=== VALIDATION: test-data files exist ===")
    referenced_files = set()
    for tc in test_cases:
        input_file = tc.get("inputFile")
        if input_file:
            referenced_files.add(input_file)

    for file_rel in sorted(referenced_files):
        full_file_path = os.path.join(base_dir, file_rel)
        if os.path.exists(full_file_path):
            print(f"  [PASS] File exists: {os.path.basename(file_rel)}")
        else:
            print(f"  [FAIL] File missing: {file_rel}")
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

