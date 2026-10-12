import json
import re
import sys
import os

BASE = r"c:\Users\costrategix\Code-Review-Agent\skills\engineering\skill-eng-maintainability"
SKILL_MD = os.path.join(BASE, "SKILL.md")
SUITE_JSON = os.path.join(BASE, "validation", "test-suite.json")
SCHEMA_JSON = os.path.join(BASE, "validation", "test-suite.schema.json")
CHECKLIST = os.path.join(BASE, "references", "checklist.md")
SCORING = os.path.join(BASE, "references", "scoring-guide.md")
TEST_DATA = os.path.join(BASE, "validation", "test-data")

ALL_RULES = [f"MAINT{str(i).zfill(2)}" for i in range(1, 15)]
RULE_NAMES = {
    "MAINT01": "Code Duplication",
    "MAINT02": "Complexity and Readability",
    "MAINT03": "Naming and Intent Clarity",
    "MAINT04": "Function and Method Responsibility",
    "MAINT05": "Coupling and Dependency Management",
    "MAINT06": "Cohesion and Module Boundaries",
    "MAINT07": "Error Handling Clarity",
    "MAINT08": "Configuration and Magic Values",
    "MAINT09": "Testability and Test Structure",
    "MAINT10": "Abstraction and Design Consistency",
    "MAINT11": "Dead and Obsolete Code",
    "MAINT12": "Documentation and Contract Clarity",
    "MAINT13": "Change Safety and Locality",
    "MAINT14": "Technology-Specific Maintainability",
}

failures = []

def check(label, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {label}" + (f": {detail}" if detail else ""))
    if not passed:
        failures.append(f"{label}: {detail}")

print("\n=== VALIDATION: SKILL.md ===")
with open(SKILL_MD, encoding="utf-8") as f:
    skill = f.read()
    skill_lines = skill.splitlines()

# Line count check (< 200 lines, target 120-170)
line_count = len(skill_lines)
check("SKILL.md strictly under 200 lines", line_count < 200, f"{line_count} lines")
check("SKILL.md in target range (120-170 lines)", 120 <= line_count <= 170, f"{line_count} lines")

check("Frontmatter starts with ---", skill.startswith("---"))
check("name: skill-eng-maintainability", "name: skill-eng-maintainability" in skill)
check("Folded description (>-)", "description: >-" in skill)
check("Activation clause", "Activate when" in skill)
check("No prohibited: license", "license:" not in skill)
check("No prohibited: compatibility", "compatibility:" not in skill)
check("No prohibited: metadata", not re.search(r"^metadata:", skill, re.MULTILINE))
check("Reference: checklist.md", "references/checklist.md" in skill)
check("Reference: scoring-guide.md", "references/scoring-guide.md" in skill)
check("Reference: test-suite.json", "validation/test-suite.json" in skill)

# Description length
desc_match = re.search(r"description: >-\n([\s\S]*?)(?=\n\w|\n---)", skill)
if desc_match:
    desc = " ".join(desc_match.group(1).split())
    check("Description <= 1024 chars", len(desc) <= 1024, f"{len(desc)} chars")
else:
    check("Description parseable", False, "Could not extract description block")

# Purpose & Activation section check
check("Purpose & Activation present", "## 1. Purpose & Activation" in skill)
check("Technology Context present", "## 2. Technology Context" in skill)

# All 14 rule IDs and names
missing_rules = [r for r in ALL_RULES if r not in skill]
check("All 14 rule IDs in SKILL.md", not missing_rules, f"Missing: {missing_rules}" if missing_rules else "")
for rid, name in RULE_NAMES.items():
    check(f"{rid} rule name present", name in skill)

# Compact rule table
check("Compact table format present", "| ID | Rule | Objective |" in skill)

print("\n=== VALIDATION: references/checklist.md ===")
with open(CHECKLIST, encoding="utf-8") as f:
    checklist = f.read()

for rid in ALL_RULES:
    check(f"{rid} covered in checklist.md", rid in checklist)

# Required detailed fields in checklist.md
REQUIRED_CHECKLIST_FIELDS = [
    "Purpose",
    "Detect",
    "Evidence",
    "Avoid",
    "Remediation",
    "Severity",
]
for field in REQUIRED_CHECKLIST_FIELDS:
    count = checklist.count(f"**{field}:**")
    check(f"Checklist field '{field}' appears 14 times", count >= 14, f"Found {count}")

# Disambiguation / Boundary notes
BOUNDARIES = [
    ("MAINT01 vs. MAINT10", "MAINT01 vs. MAINT10" in checklist),
    ("MAINT04 vs. MAINT06", "MAINT04 vs. MAINT06" in checklist),
    ("MAINT05 vs. MAINT13", "MAINT05 vs. MAINT13" in checklist),
    ("MAINT07 vs. MAINT12", "MAINT07 vs. MAINT12" in checklist),
]
for b_name, b_present in BOUNDARIES:
    check(f"Boundary documented: {b_name}", b_present)

print("\n=== VALIDATION: references/scoring-guide.md ===")
with open(SCORING, encoding="utf-8") as f:
    scoring = f.read()

for rid in ALL_RULES:
    check(f"{rid} referenced in scoring-guide.md", rid in scoring)
check("Severity levels defined", all(s in scoring for s in ["critical", "high", "medium", "low"]))
check("Score calculation formula", "deduction" in scoring and "multiplier" in scoring.lower())
check("Scorecard Aggregator integration", "Scorecard Aggregator" in scoring)
check("Blocking threshold defined", "60" in scoring)

print("\n=== VALIDATION: test-suite.json ===")
with open(SUITE_JSON, encoding="utf-8") as f:
    suite = json.load(f)

check("Valid JSON", True)
tc_count = len(suite["testCases"])
check("testCases array present", tc_count > 0, f"{tc_count} test cases")

# Schema file exists
check("Local schema exists: test-suite.schema.json", os.path.exists(SCHEMA_JSON))
check("Schema reference points to local schema", suite.get("$schema") == "./test-suite.schema.json")

# All rules covered
covered_rules = set()
for tc in suite["testCases"]:
    for rid in tc.get("ruleIds", []):
        covered_rules.add(rid)
missing = set(ALL_RULES) - covered_rules
check("All 14 rules referenced in testCases", not missing, f"Missing: {missing}" if missing else "")

# Violation tests for each rule
violation_rules = set()
for tc in suite["testCases"]:
    if tc["expected"].get("findingsPresent") == True:
        for rid in tc.get("ruleIds", []):
            violation_rules.add(rid)
missing_viol = set(ALL_RULES) - violation_rules
check("Each rule has at least one violation test", not missing_viol, f"Missing: {missing_viol}" if missing_viol else "")

# Safe cases
safe_count = sum(1 for tc in suite["testCases"] if tc["expected"].get("findingsPresent") == False)
safe_count += sum(1 for tc in suite["testCases"] if tc.get("safeCounterpart", {}).get("expected", {}).get("findingsPresent") == False)
safe_count += sum(1 for tc in suite["testCases"] if tc.get("notApplicableCase", {}).get("expected", {}).get("findingsPresent") == False)
check("Safe/negative cases present", safe_count >= 5, f"{safe_count} cases")

# Stable IDs
tc_ids = [tc["id"] for tc in suite["testCases"]]
check("Stable TC IDs (TC-NNN pattern)", all(re.match(r"TC-\d+", tid) for tid in tc_ids))

print("\n=== VALIDATION: test-data files exist ===")
expected_files = [
    "TC-001-duplication.py",
    "TC-002-complexity.py",
    "TC-003-naming.py",
    "TC-004-function-responsibility.py",
    "TC-005-coupling.py",
    "TC-006-cohesion.py",
    "TC-007-error-handling.py",
    "TC-008-configuration.py",
    "TC-009-testability.py",
    "TC-010-abstraction.py",
    "TC-011-dead-code.py",
    "TC-012-documentation.py",
    "TC-013-safe-code.py",
    "TC-014-dotnet-maintainability.cs",
    "TC-015-react-maintainability.tsx",
    "TC-016-sql-maintainability.sql",
]
for fname in expected_files:
    fpath = os.path.join(TEST_DATA, fname)
    check(f"File exists: {fname}", os.path.exists(fpath))

print("\n=== VALIDATION: Cross-file rule name consistency ===")
for rid, name in RULE_NAMES.items():
    in_skill = name in skill
    in_checklist = rid in checklist
    in_scoring = rid in scoring
    check(f"{rid} consistent across all 3 files", in_skill and in_checklist and in_scoring)

print(f"\n=== SUMMARY ===")
print(f"Total failures: {len(failures)}")
if failures:
    print("Failed checks:")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("All validation checks passed.")

