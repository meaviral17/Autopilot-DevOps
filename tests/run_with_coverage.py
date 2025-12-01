"""
Test runner with coverage report
"""
import sys
import os
import subprocess

def main():
    """Run tests with coverage."""
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(tests_dir)
    
    os.chdir(project_root)
    
    print("=" * 60)
    print("AutoPilot DevOps - Test Suite with Coverage")
    print("=" * 60)
    print()
    
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest", 
                tests_dir, 
                "--cov=project",
                "--cov-report=html",
                "--cov-report=term",
                "-v"
            ],
            cwd=project_root,
            check=False
        )
        
        print()
        print("=" * 60)
        print("Coverage report generated in htmlcov/index.html")
        print("=" * 60)
        
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("ERROR: pytest or pytest-cov not found.")
        print("Install with: pip install pytest pytest-cov")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

