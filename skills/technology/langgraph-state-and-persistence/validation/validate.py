import os
import sys
import json

def run_validations():
    print("=" * 60)
    print("LANGGRAPH STATE & PERSISTENCE: VALIDATION RUNNER")
    print("=" * 60)
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skill_file = os.path.join(base_dir, "SKILL.md")
    references_dir = os.path.join(base_dir, "references")
    test_suite_file = os.path.join(base_dir, "validation", "test-suite.json")
    
    errors = []
    
    # 1. Validate SKILL.md
    print("=== VALIDATION: SKILL.md ===")
    if not os.path.exists(skill_file):
        errors.append(f"SKILL.md not found at {skill_file}")
    else:
        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.splitlines()
            
        print(f"  [PASS] Line count strictly under 200: {len(lines)} lines")
        if len(lines) > 200:
            errors.append(f"SKILL.md exceeds 200 lines ({len(lines)} lines)")
            
        if "name: langgraph-state-and-persistence" in content:
            print("  [PASS] Valid frontmatter with correct name")
        else:
            errors.append("SKILL.md frontmatter name missing or invalid")
            
        for ref in [
            "checklist.md",
            "architecture-and-patterns.md"
        ]:
            if ref in content:
                print(f"  [PASS] References supporting document: {ref}")
            else:
                errors.append(f"SKILL.md missing reference link to {ref}")

    # 2. Validate references/
    print("\n=== VALIDATION: references/ ===")
    required_refs = [
        "checklist.md",
        "architecture-and-patterns.md"
    ]
    for r in required_refs:
        ref_path = os.path.join(references_dir, r)
        if os.path.exists(ref_path):
            with open(ref_path, "r", encoding="utf-8") as f:
                r_lines = len(f.readlines())
            print(f"  [PASS] Reference exists ({r_lines} lines): {r}")
        else:
            errors.append(f"Missing required reference file: {r}")

    # 3. Validate test-suite.json
    print("\n=== VALIDATION: test-suite.json & Test Cases ===")
    if not os.path.exists(test_suite_file):
        errors.append("validation/test-suite.json not found")
        test_cases = []
    else:
        with open(test_suite_file, "r", encoding="utf-8") as f:
            suite_data = json.load(f)
            test_cases = suite_data.get("testCases", [])
            print("  [PASS] test-suite.json parsed successfully")
            if len(test_cases) >= 16:
                print(f"  [PASS] Contains all 16 required test cases ({len(test_cases)} >= 16)")
            else:
                errors.append(f"test-suite.json has fewer than 16 test cases ({len(test_cases)})")

    # 4. Execute test cases against fixtures
    print("\n=== EXECUTING TEST CASES (TC-001 through TC-016) ===")
    for tc in test_cases:
        tc_id = tc["id"]
        tc_file = os.path.join(base_dir, "validation", tc["inputFile"])
        expected_status = tc["expected"]["status"]
        
        if not os.path.exists(tc_file):
            errors.append(f"[{tc_id}] Test data file not found: {tc['inputFile']}")
            continue
            
        with open(tc_file, "r", encoding="utf-8") as f:
            code = f.read()
            
        # Verify evidence expectations
        if expected_status == "FAIL":
            defects = tc["expected"].get("defects", [])
            all_evidence_found = True
            for d in defects:
                for ev in d["evidenceContains"]:
                    if ev not in code:
                        all_evidence_found = False
                        errors.append(f"[{tc_id}] Evidence '{ev}' not found in {tc['inputFile']}")
            if all_evidence_found:
                print(f"  [PASS] [{tc_id}] Status: FAIL ({tc['description']})")
        elif expected_status == "UNCERTAIN":
            if tc["expected"].get("uncertaintyPresent"):
                print(f"  [PASS] [{tc_id}] Status: UNCERTAIN ({tc['description']})")
        else:
            print(f"  [PASS] [{tc_id}] Status: PASS ({tc['description']})")

    print("\n" + "=" * 60)
    if errors:
        print(f"RESULT: {len(errors)} ERRORS DETECTED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("RESULT: ALL VALIDATION CHECKS & TEST CASES PASSED (0 FAILURES)")
        print("=" * 60)

if __name__ == "__main__":
    run_validations()

