#!/usr/bin/env python3
"""
PyOBD Test Runner

Convenient script to run PyOBD tests with various options.
"""

import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print results"""
    print(f"\n{'='*70}")
    print(f"  {description}")
    print(f"{'='*70}\n")
    
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode != 0:
        print(f"\n❌ {description} FAILED")
        return False
    else:
        print(f"\n✅ {description} PASSED")
        return True


def main():
    """Main test runner"""
    
    # Change to project root
    project_root = Path(__file__).parent
    
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                    PyOBD Test Suite Runner                         ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    
    if len(sys.argv) > 1:
        # Run specific test category
        category = sys.argv[1]
        
        if category == "quick":
            print("Running quick test suite (decoders + utils)...")
            run_command("pytest -m 'decoders or utils' -v", "Quick Tests")
        
        elif category == "decoders":
            print("Running decoder tests...")
            run_command("pytest -m decoders -v", "Decoder Tests")
        
        elif category == "utils":
            print("Running utility tests...")
            run_command("pytest -m utils -v", "Utility Tests")
        
        elif category == "commands":
            print("Running command tests...")
            run_command("pytest -m commands -v", "Command Tests")
        
        elif category == "connection":
            print("Running connection tests...")
            run_command("pytest -m connection -v", "Connection Tests")
        
        elif category == "protocols":
            print("Running protocol tests...")
            run_command("pytest -m protocols -v", "Protocol Tests")
        
        elif category == "coverage":
            print("Running tests with coverage report...")
            run_command("pytest --cov=. --cov-report=html --cov-report=term", 
                       "Coverage Tests")
            print("\n📊 Coverage report generated in htmlcov/index.html")
        
        elif category == "parallel":
            print("Running tests in parallel...")
            run_command("pytest -n auto", "Parallel Tests")
        
        elif category == "legacy":
            print("Running legacy codebase tests...")
            run_command("pytest tests/legacy/ -v", "Legacy Tests")
        
        elif category == "new":
            print("Running new codebase tests...")
            run_command("pytest tests/new/ -v", "New Codebase Tests")
        
        else:
            print(f"❌ Unknown test category: {category}")
            print_usage()
            return 1
    
    else:
        # Run all tests
        print("Running complete test suite...")
        
        results = []
        
        # Run each test category
        results.append(run_command("pytest -m decoders -v", "Decoder Tests"))
        results.append(run_command("pytest -m utils -v", "Utility Tests"))
        results.append(run_command("pytest -m commands -v", "Command Tests"))
        results.append(run_command("pytest -m connection -v", "Connection Tests"))
        results.append(run_command("pytest -m protocols -v", "Protocol Tests"))
        
        # Summary
        print(f"\n{'='*70}")
        print(f"  TEST SUMMARY")
        print(f"{'='*70}\n")
        
        passed = sum(results)
        total = len(results)
        
        print(f"Passed: {passed}/{total}")
        
        if all(results):
            print("\n✅ ALL TESTS PASSED!")
            return 0
        else:
            print("\n❌ SOME TESTS FAILED")
            return 1
    
    return 0


def print_usage():
    """Print usage information"""
    print("""
Usage: python run_tests.py [category]

Categories:
  (none)      - Run all tests
  quick       - Run quick tests (decoders + utils)
  decoders    - Run decoder tests only
  utils       - Run utility tests only
  commands    - Run command tests only
  connection  - Run connection tests only
  protocols   - Run protocol tests only
  coverage    - Run tests with coverage report
  parallel    - Run tests in parallel
  legacy      - Run legacy codebase tests only
  new         - Run new codebase tests only

Examples:
  python run_tests.py                # Run all tests
  python run_tests.py quick          # Run quick tests
  python run_tests.py coverage       # Generate coverage report
  python run_tests.py decoders       # Test decoders only
""")


if __name__ == "__main__":
    sys.exit(main())
