#!/usr/bin/env python3
"""
Test runner script for Loom CLI tests.
"""
import subprocess
import sys
import os

def run_tests():
    """Run the test suite."""
    print("🧪 Running Loom CLI Tests")
    print("=" * 50)
    
    # Check if pytest is available
    try:
        import pytest
        print("✓ pytest is available")
    except ImportError:
        print("❌ pytest not found. Install with: uv sync --extra test")
        return False
    
    # Run tests with pytest
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v", 
        "--tb=short",
        "--disable-warnings"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest command not found")
        return False

def run_specific_test(test_name):
    """Run a specific test."""
    cmd = [
        sys.executable, "-m", "pytest", 
        f"tests/test_secrets.py::{test_name}",
        "-v"
    ]
    
    print(f"Running specific test: {test_name}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Test {test_name} passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Test {test_name} failed with exit code {e.returncode}")
        return False

def main():
    """Main test runner function."""
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        # Run all tests
        success = run_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
