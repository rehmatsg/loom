#!/usr/bin/env python3
"""
Example of how to run tests and demonstrate the testing setup.
"""
import subprocess
import sys
import os


def main():
  """Demonstrate the testing setup."""
  print("🧪 Loom CLI Testing Setup Demo")
  print("=" * 50)

  # Check if we're in the right directory
  if not os.path.exists("tests/test_secrets.py"):
    print("❌ Test files not found. Make sure you're in the project root.")
    return

  print("✅ Test files found")
  print()

  # Show available test commands
  print("Available test commands:")
  print("1. Run all tests:")
  print("   python -m pytest tests/ -v")
  print()
  print("2. Run specific test class:")
  print("   python -m pytest tests/test_secrets.py::TestSecretsManager -v")
  print()
  print("3. Run specific test method:")
  print("   python -m pytest tests/test_secrets.py::TestSecretsManager::test_save_secret_success -v")
  print()
  print("4. Run with coverage:")
  print("   python -m pytest tests/ --cov=loom --cov-report=html")
  print()
  print("5. Run integration tests (requires keychain access):")
  print("   python -m pytest tests/ -m integration -v")
  print()
  print("6. Skip integration tests:")
  print("   python -m pytest tests/ -m 'not integration' -v")
  print()

  # Try to run a simple test
  print("Running a simple test to verify setup...")
  try:
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/test_secrets.py::TestSecretsManager::test_init_default_service",
        "-v", "--tb=short"
    ], capture_output=True, text=True, timeout=30)

    if result.returncode == 0:
      print("✅ Test setup is working correctly!")
      print("Output:", result.stdout)
    else:
      print("❌ Test setup has issues:")
      print("Error:", result.stderr)

  except subprocess.TimeoutExpired:
    print("⏰ Test timed out")
  except Exception as e:
    print(f"❌ Error running test: {e}")

  print("\n" + "=" * 50)
  print("To install test dependencies:")
  print("uv sync --extra test")
  print()
  print("To run tests:")
  print("python run_tests.py")


if __name__ == "__main__":
  main()
