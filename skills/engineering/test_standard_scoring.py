#!/usr/bin/env python3
"""
Comprehensive Validation Tests for Standardized Scoring & Blocking Policy.
Tests cross-dimension consistency, rubric mathematics, aggregation logic,
critical override behavior, schema integrity, and document compliance.
"""

import sys
import os
import json
import re

ENGINEERING_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS = [
    "skill-eng-business-logic",
    "skill-eng-maintainability",
    "skill-eng-modularity",
    "skill-eng-performance",
]

# Standard deduction weights (normalized 10-point scale)
BASE_DEDUCTIONS = {
    "critical": 6.0,
    "high": 4.0,
    "medium": 2.0,
    "low": 1.0,
}

CONFIDENCE_MULTIPLIERS = {
    "high": 1.00,
    "medium": 0.70,
    "low": 0.30,
}


def calculate_dimension_evaluation(findings, uncertainty_notes=None):
    """
    Standard scoring function implementing the unified rubric:
    - Base score: 10.0 (normalized)
    - Deductions: round(base_deduction * confidence_multiplier)
    - Score: max(0, 10 - sum(deductions))
    - Pass criteria: score >= 9.0 and no critical violations and (if score == 9.0, at most 1 minor finding)
    - Block criteria: score < 9.0 or any critical violation present
    """
    if uncertainty_notes is None:
        uncertainty_notes = []

    # Filter out low-confidence speculative concerns (they become uncertainty notes)
    confirmed_findings = [f for f in findings if f.get("confidence") != "low"]

    total_deductions = 0.0
    has_critical = False
    minor_count = 0
    high_or_medium_count = 0

    for finding in confirmed_findings:
        sev = finding.get("severity", "low")
        conf = finding.get("confidence", "high")
        status = finding.get("status", "open")

        if sev == "critical":
            has_critical = True
        elif sev == "low":
            minor_count += 1
        elif sev in ("high", "medium"):
            high_or_medium_count += 1

        base = BASE_DEDUCTIONS.get(sev, 1.0)
        multiplier = CONFIDENCE_MULTIPLIERS.get(conf, 1.00)
        deduction = round(base * multiplier)

        if status == "accepted":
            deduction = deduction * 0.5

        total_deductions += deduction

    score = max(0.0, 10.0 - total_deductions)

    # Merge blocking logic:
    # 1. Any score < 9.0 blocks
    # 2. Any critical violation blocks (regardless of score)
    # 3. Score == 9.0 passes only if minor_count <= 1 and high_or_medium_count == 0 and not has_critical
    is_blocked = False
    if score < 9.0:
        is_blocked = True
    elif has_critical:
        is_blocked = True
    elif score == 9.0 and (minor_count > 1 or high_or_medium_count > 0):
        is_blocked = True

    return {
        "score": score,
        "score_100": int(score * 10),
        "blocked": is_blocked,
        "passed": not is_blocked,
        "findings": confirmed_findings,
        "uncertainty_notes": uncertainty_notes,
    }


def aggregate_global_review(dimension_results):
    """
    Global Scorecard Aggregator:
    - Passes if and only if EVERY evaluated dimension passes (score >= 9.0 and not blocked).
    - If any dimension is blocked, the global review is blocked.
    """
    all_passed = True
    for dim_name, result in dimension_results.items():
        if result["blocked"] or not result["passed"] or result["score"] < 9.0:
            all_passed = False
            break

    return {
        "global_status": "passed" if all_passed else "blocked",
        "dimensions": dimension_results,
    }


def run_tests():
    failures = []
    test_count = 0

    def assert_true(test_name, condition, details=""):
        nonlocal test_count
        test_count += 1
        if condition:
            print(f"  [PASS] {test_name}")
        else:
            print(f"  [FAIL] {test_name}: {details}")
            failures.append(f"{test_name} - {details}")

    print("=== TEST SUITE 1: Rubric Mathematics & Scoring Formulas ===")

    # Test 1: Zero violations produce 10/10 and pass
    res_zero = calculate_dimension_evaluation([])
    assert_true(
        "Zero violations produce 10/10 and pass",
        res_zero["score"] == 10.0 and res_zero["passed"] and not res_zero["blocked"],
        f"Got score={res_zero['score']}, blocked={res_zero['blocked']}",
    )

    # Test 2: One permitted minor (low) violation produces 9/10 and passes
    res_one_low = calculate_dimension_evaluation([
        {"severity": "low", "confidence": "high", "ruleId": "MAINT03"}
    ])
    assert_true(
        "One permitted minor violation produces 9/10 and passes",
        res_one_low["score"] == 9.0 and res_one_low["passed"] and not res_one_low["blocked"],
        f"Got score={res_one_low['score']}, blocked={res_one_low['blocked']}",
    )

    # Test 3: More than one minor violation cannot receive 9/10 (scores <= 8/10 and blocks)
    res_two_low = calculate_dimension_evaluation([
        {"severity": "low", "confidence": "high", "ruleId": "MAINT03"},
        {"severity": "low", "confidence": "high", "ruleId": "MAINT08"},
    ])
    assert_true(
        "Two minor violations produce <= 8/10 and block",
        res_two_low["score"] <= 8.0 and res_two_low["blocked"],
        f"Got score={res_two_low['score']}, blocked={res_two_low['blocked']}",
    )

    # Test 4: Any dimension score below 9/10 blocks
    res_one_medium = calculate_dimension_evaluation([
        {"severity": "medium", "confidence": "high", "ruleId": "MOD04"}
    ])
    assert_true(
        "Medium violation produces 8/10 (< 9/10) and blocks",
        res_one_medium["score"] == 8.0 and res_one_medium["blocked"],
        f"Got score={res_one_medium['score']}, blocked={res_one_medium['blocked']}",
    )

    res_one_high = calculate_dimension_evaluation([
        {"severity": "high", "confidence": "high", "ruleId": "PERF02"}
    ])
    assert_true(
        "High violation produces 6/10 (< 9/10) and blocks",
        res_one_high["score"] == 6.0 and res_one_high["blocked"],
        f"Got score={res_one_high['score']}, blocked={res_one_high['blocked']}",
    )

    # Test 5: Critical violation blocks regardless of score (critical override)
    # Suppose a finding is critical with documented exception or special multiplier that yields 9/10
    res_crit = calculate_dimension_evaluation([
        {"severity": "critical", "confidence": "high", "ruleId": "BIZ03"}
    ])
    assert_true(
        "Critical violation blocks merge",
        res_crit["blocked"] and not res_crit["passed"],
        f"Got score={res_crit['score']}, blocked={res_crit['blocked']}",
    )

    # Test 6: Non-critical finding does not trigger critical override
    assert_true(
        "Single low finding does not trigger critical override",
        not res_one_low["blocked"],
        f"Got blocked={res_one_low['blocked']}",
    )

    # Test 7 (Task Requirement 7.1-7.10): Dedicated Native 0-10 Performance Tests
    # 7.1: Zero confirmed violations produce 10.0
    perf_zero = calculate_dimension_evaluation([])
    assert_true("PERF 10.0 on zero violations", perf_zero["score"] == 10.0 and not perf_zero["blocked"])

    # 7.2: One permitted minor finding can produce 9.0 and pass
    perf_one_low = calculate_dimension_evaluation([{"ruleId": "PERF13", "severity": "low", "confidence": "high"}])
    assert_true("PERF 9.0 pass on single minor finding", perf_one_low["score"] == 9.0 and not perf_one_low["blocked"])

    # 7.3: Multiple minor findings cannot pass at 9.0 (produce <= 8.0 and block)
    perf_multi_low = calculate_dimension_evaluation([
        {"ruleId": "PERF13", "severity": "low", "confidence": "high"},
        {"ruleId": "PERF08", "severity": "low", "confidence": "high"},
    ])
    assert_true("PERF multiple minor findings block (score <= 8.0)", perf_multi_low["score"] <= 8.0 and perf_multi_low["blocked"])

    # 7.4: Any score below 9.0 blocks
    perf_med = calculate_dimension_evaluation([{"ruleId": "PERF05", "severity": "medium", "confidence": "high"}])
    assert_true("PERF score below 9.0 blocks (8.0)", perf_med["score"] == 8.0 and perf_med["blocked"])

    # 7.5: Confirmed critical violation blocks even if score is manipulated/adjusted
    perf_crit = calculate_dimension_evaluation([{"ruleId": "PERF01", "severity": "critical", "confidence": "high"}])
    assert_true("PERF critical violation blocks merge unconditionally", perf_crit["blocked"])

    # 7.6: Low-confidence observations cause zero deductions
    perf_low_conf = calculate_dimension_evaluation([
        {"ruleId": "PERF04", "severity": "high", "confidence": "low"}
    ], uncertainty_notes=["Speculative caching concern"])
    assert_true("PERF low-confidence observation causes 0 deduction (10.0)", perf_low_conf["score"] == 10.0 and not perf_low_conf["blocked"])

    # 7.7: Score clamping: never exceeds 10.0 or falls below 0.0
    perf_heavy = calculate_dimension_evaluation([
        {"ruleId": "PERF01", "severity": "critical", "confidence": "high"},
        {"ruleId": "PERF02", "severity": "critical", "confidence": "high"},
        {"ruleId": "PERF03", "severity": "high", "confidence": "high"},
    ])
    assert_true("PERF score clamped at minimum 0.0", perf_heavy["score"] == 0.0 and perf_heavy["blocked"])

    # 7.8: Direct 0-10 deduction calculation (High = -4.0 directly)
    perf_high = calculate_dimension_evaluation([{"ruleId": "PERF02", "severity": "high", "confidence": "high"}])
    assert_true("PERF direct 0-10 deduction applied (10.0 - 4.0 = 6.0)", perf_high["score"] == 6.0 and perf_high["blocked"])

    print("\n=== TEST SUITE 2: Multi-Dimension Global Aggregation ===")

    # Test 7: Multiple dimensions all passing => global review passes
    dim_all_pass = {
        "maintainability": calculate_dimension_evaluation([]),
        "modularity": calculate_dimension_evaluation([{"severity": "low", "confidence": "high"}]),
        "performance": calculate_dimension_evaluation([]),
        "business_logic": calculate_dimension_evaluation([]),
    }
    agg_pass = aggregate_global_review(dim_all_pass)
    assert_true(
        "Global review passes when all dimensions pass (scores >= 9.0)",
        agg_pass["global_status"] == "passed",
        f"Got status={agg_pass['global_status']}",
    )

    # Test 8: Global review cannot pass when any dimension is blocked
    dim_one_fail = {
        "maintainability": calculate_dimension_evaluation([]),
        "modularity": calculate_dimension_evaluation([{"severity": "high", "confidence": "high"}]),
        "performance": calculate_dimension_evaluation([]),
        "business_logic": calculate_dimension_evaluation([]),
    }
    agg_fail = aggregate_global_review(dim_one_fail)
    assert_true(
        "Global review blocks when one dimension is blocked (e.g. modularity score=6.0)",
        agg_fail["global_status"] == "blocked",
        f"Got status={agg_fail['global_status']}",
    )

    print("\n=== TEST SUITE 3: Documentation & Consistency Audit Across All 4 Skills ===")

    for skill in SKILLS:
        skill_path = os.path.join(ENGINEERING_DIR, skill)
        skill_md = os.path.join(skill_path, "SKILL.md")
        scoring_md = os.path.join(skill_path, "references", "scoring-guide.md")
        test_suite_json = os.path.join(skill_path, "validation", "test-suite.json")

        # Check SKILL.md line limit
        with open(skill_md, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert_true(
                f"{skill} SKILL.md under 200 lines",
                len(lines) < 200,
                f"{len(lines)} lines",
            )
            content = "".join(lines)
            assert_true(
                f"{skill} SKILL.md references standard 9/10 blocking threshold",
                "9/10" in content,
                "Missing '9/10' in SKILL.md",
            )

        # Check scoring-guide.md
        with open(scoring_md, "r", encoding="utf-8") as f:
            s_content = f.read()
            s_lines = s_content.splitlines()
            assert_true(
                f"{skill} scoring-guide.md length between 60 and 130 lines",
                60 <= len(s_lines) <= 130,
                f"{len(s_lines)} lines",
            )
            assert_true(
                f"{skill} scoring-guide.md defines 10/10 Pass and 9/10 Pass with minor issues",
                "10/10" in s_content and "9/10" in s_content,
                "Missing standard rubric thresholds",
            )
            assert_true(
                f"{skill} scoring-guide.md defines Critical Override blocking",
                "Critical Override" in s_content or "critical" in s_content.lower(),
                "Missing critical override policy",
            )
            assert_true(
                f"{skill} scoring-guide.md includes Scorecard Aggregator Integration",
                "Scorecard Aggregator" in s_content,
                "Missing Scorecard Aggregator reference",
            )

        # Check test-suite.json valid
        with open(test_suite_json, "r", encoding="utf-8") as f:
            suite_data = json.load(f)
            assert_true(
                f"{skill} test-suite.json valid with testCases",
                "testCases" in suite_data and len(suite_data["testCases"]) > 0,
                f"Count={len(suite_data.get('testCases', []))}",
            )

    print(f"\n=== SUMMARY: {test_count} checks executed, {len(failures)} failures ===")
    if failures:
        print("Failures:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("All standard scoring and blocking policy tests PASSED successfully.")
        sys.exit(0)


if __name__ == "__main__":
    run_tests()

