"""
Test runner script - runs all tests in the tests directory
"""
import sys
import os
import subprocess

def main():
    """Run all tests."""
    # Get the tests directory
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(tests_dir)
    
    # Change to project root
    os.chdir(project_root)
    
    print("=" * 60)
    print("AutoPilot DevOps - Test Suite")
    print("=" * 60)
    print(f"Project Root: {project_root}")
    print(f"Tests Directory: {tests_dir}")
    print("=" * 60)
    print()
    
    # Run pytest
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", tests_dir, "-v", "--tb=short"],
            cwd=project_root,
            check=False
        )
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("ERROR: pytest not found. Install with: pip install pytest")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

