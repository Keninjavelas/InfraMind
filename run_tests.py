import json
import os
import sys
import time

# Add backend to path for imports
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "apps", "backend"))
)

from app.context_builder.builder import ContextBuilder  # noqa: E402

TESTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "tests"))


def run_regression_suite():
    print("=== Starting InfraMind Regression Suite ===")

    total_tests = 0
    passed_tests = 0
    failed_tests = []

    for root, dirs, files in os.walk(TESTS_DIR):
        if "expected.json" in files:
            total_tests += 1
            test_name = os.path.relpath(root, TESTS_DIR)
            expected_file = os.path.join(root, "expected.json")

            with open(expected_file, "r") as f:
                expected_data = json.load(f)
                expected_risks = expected_data.get("expected_risks", [])

            print(f"\n[ RUN      ] {test_name}")
            start_time = time.time()

            try:
                # Initialize parser for this specific directory
                builder = ContextBuilder(root)
                infra_summary = builder.build_context()

                actual_risks = infra_summary.security_risks
                actual_risk_signatures = [
                    (r.severity, r.category) for r in actual_risks
                ]
                expected_risk_signatures = [
                    (r["severity"], r["category"]) for r in expected_risks
                ]

                # Check expectations
                missing_risks = [
                    r
                    for r in expected_risk_signatures
                    if r not in actual_risk_signatures
                ]
                extra_risks = [
                    r
                    for r in actual_risk_signatures
                    if r not in expected_risk_signatures
                ]

                elapsed_time = time.time() - start_time

                if not missing_risks and not extra_risks:
                    print(f"[       OK ] {test_name} ({elapsed_time:.2f}s)")
                    passed_tests += 1
                else:
                    print(f"[  FAILED  ] {test_name} ({elapsed_time:.2f}s)")
                    if missing_risks:
                        print(f"             Missing expected risks: {missing_risks}")
                    if extra_risks:
                        print(f"             Unexpected risks found: {extra_risks}")
                    failed_tests.append(test_name)

            except Exception as e:
                elapsed_time = time.time() - start_time
                print(
                    f"[  FAILED  ] {test_name} ({elapsed_time:.2f}s) - Exception: {e}"
                )
                failed_tests.append(test_name)

    print("\n=== Regression Suite Summary ===")
    print(f"Total Tests: {total_tests}")
    print(f"Passed:      {passed_tests}")
    print(f"Failed:      {len(failed_tests)}")

    if failed_tests:
        print("\nFailed Tests:")
        for ft in failed_tests:
            print(f" - {ft}")
        exit(1)
    else:
        print("\nAll tests passed successfully! [OK]")
        exit(0)


if __name__ == "__main__":
    run_regression_suite()
