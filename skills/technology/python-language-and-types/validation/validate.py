#!/usr/bin/env python3
import os
import sys
import json
import py_compile

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
        print("  [FAIL] Frontmatter does not start with ---")
        failures += 1

    if "name: python-language-and-types" in content:
        print("  [PASS] name: python-language-and-types")
    else:
        print("  [FAIL] Missing 'name: python-language-and-types'")
        failures += 1

    if "description: >-" in content:
        print("  [PASS] Folded description (>-)")
    else:
        print("  [FAIL] Missing folded description (>-)")
        failures += 1

    required_refs = [
        "references/language-features.md",
        "references/type-system.md",
        "references/validation-workflow.md",
        "validation/test-suite.json"
    ]

    for ref in required_refs:
        if ref in content:
            print(f"  [PASS] Reference: {ref}")
        else:
            print(f"  [FAIL] Missing reference: {ref}")
            failures += 1

    return failures


def validate_references(base_dir):
    print("\n=== VALIDATION: references/ files ===")
    failures = 0
    ref_files = [
        "references/language-features.md",
        "references/type-system.md",
        "references/validation-workflow.md"
    ]

    for ref_rel in ref_files:
        full_path = os.path.join(base_dir, ref_rel)
        if os.path.exists(full_path):
            print(f"  [PASS] Reference file exists: {ref_rel}")
        else:
            print(f"  [FAIL] Reference file missing: {ref_rel}")
            failures += 1

    return failures


def validate_test_suite_json(test_suite_path, base_dir):
    print("\n=== VALIDATION: test-suite.json & test-data fixtures ===")
    failures = 0

    if not os.path.exists(test_suite_path):
        print(f"  [FAIL] {test_suite_path} does not exist")
        return 1

    try:
        with open(test_suite_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("  [PASS] Valid JSON in test-suite.json")
    except Exception as e:
        print(f"  [FAIL] Invalid JSON in {test_suite_path}: {e}")
        return 1

    test_cases = data.get("testCases", [])
    if len(test_cases) >= 10:
        print(f"  [PASS] testCases array present with {len(test_cases)} test cases")
    else:
        print(f"  [FAIL] testCases array has fewer than 10 cases: {len(test_cases)}")
        failures += 1

    for tc in test_cases:
        tc_id = tc.get("id")
        input_file = tc.get("inputFile")
        full_file_path = os.path.join(base_dir, input_file) if input_file else None

        if not full_file_path or not os.path.exists(full_file_path):
            print(f"  [FAIL] {tc_id}: Input file missing ({input_file})")
            failures += 1
            continue

        if input_file.endswith(".py"):
            try:
                py_compile.compile(full_file_path, doraise=True)
                print(f"  [PASS] {tc_id}: {os.path.basename(input_file)} compiles cleanly")
            except Exception as e:
                print(f"  [FAIL] {tc_id}: {os.path.basename(input_file)} syntax error: {e}")
                failures += 1

        with open(full_file_path, 'r', encoding='utf-8') as tf:
            file_content = tf.read()

        target_symbol = tc.get("targetSymbol")
        if target_symbol and target_symbol in file_content:
            print(f"  [PASS] {tc_id}: Target symbol '{target_symbol}' verified in {os.path.basename(input_file)}")
        elif target_symbol:
            print(f"  [FAIL] {tc_id}: Target symbol '{target_symbol}' missing in {os.path.basename(input_file)}")
            failures += 1

        safe_cp = tc.get("safeCounterpart", {})
        safe_symbol = safe_cp.get("targetSymbol")
        if safe_symbol and safe_symbol in file_content:
            print(f"  [PASS] {tc_id}: Safe counterpart '{safe_symbol}' verified")
        elif safe_symbol:
            print(f"  [FAIL] {tc_id}: Safe counterpart '{safe_symbol}' missing in {os.path.basename(input_file)}")
            failures += 1

    return failures


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skill_md = os.path.join(base_dir, "SKILL.md")
    test_suite_json = os.path.join(base_dir, "validation", "test-suite.json")

    total_failures = 0
    total_failures += validate_skill_md(skill_md)
    total_failures += validate_references(base_dir)
    total_failures += validate_test_suite_json(test_suite_json, base_dir)

    print("\n=== SUMMARY ===")
    print(f"Total failures: {total_failures}")
    if total_failures == 0:
        print("All validation checks passed successfully!")
        sys.exit(0)
    else:
        print("Validation failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()

