"""
Test Runner Script
Quick script to run all tests or specific test suites
"""

import subprocess
import sys


def run_tests(test_path=None, verbose=False, coverage=False):
    """Run pytest with specified options"""
    cmd = ["pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    if test_path:
        cmd.append(test_path)
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run API tests")
    parser.add_argument("test", nargs="?", help="Specific test file or path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-c", "--coverage", action="store_true", help="Run with coverage")
    parser.add_argument("--auth", action="store_true", help="Run only auth tests")
    parser.add_argument("--users", action="store_true", help="Run only user tests")
    parser.add_argument("--issues", action="store_true", help="Run only issue tests")
    parser.add_argument("--photos", action="store_true", help="Run only photo tests")
    
    args = parser.parse_args()
    
    # Determine test path
    test_path = args.test
    if args.auth:
        test_path = "tests/test_auth.py"
    elif args.users:
        test_path = "tests/test_users.py"
    elif args.issues:
        test_path = "tests/test_issues.py"
    elif args.photos:
        test_path = "tests/test_photos.py"
    
    sys.exit(run_tests(test_path, args.verbose, args.coverage))
