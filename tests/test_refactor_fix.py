"""Quick test to verify refactor_suggestions_report is generated."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from project.main_agent import MainAgent

agent = MainAgent()

# Test 1: Refactor action with empty target_paths
print("Test 1: Refactor action (should auto-detect top complex files)")
result = agent.handle_message("Suggest refactoring improvements")
refactor = result.get("refactor_suggestions_report", [])
print(f"  refactor_suggestions_report: {len(refactor)} suggestions")
if refactor:
    print(f"  ✓ SUCCESS: Found {len(refactor)} refactoring suggestions")
    for i, item in enumerate(refactor[:3], 1):
        print(f"    {i}. {item.get('file', 'unknown')}: {len(item.get('suggestions', []))} suggestions")
else:
    print(f"  ✗ FAILED: No refactoring suggestions found")

# Test 2: Repo analysis (should also generate refactoring suggestions)
print("\nTest 2: Repo analysis (should include refactoring suggestions)")
result = agent.handle_message("Analyze this repository completely")
refactor = result.get("refactor_suggestions_report", [])
print(f"  refactor_suggestions_report: {len(refactor)} suggestions")
if refactor:
    print(f"  ✓ SUCCESS: Found {len(refactor)} refactoring suggestions")
else:
    print(f"  ⚠ WARNING: No refactoring suggestions (may be empty)")

print("\n" + "="*60)
print("Summary:")
print("="*60)
print(f"All 5 reports should be present in result_dict:")
reports = {
    "dead_code_report": result.get("dead_code_report", {}),
    "migration_plan_report": result.get("migration_plan_report", {}),
    "refactor_suggestions_report": result.get("refactor_suggestions_report", []),
    "duplicate_code_report": result.get("duplicate_code_report", {}),
    "postmortem_report": result.get("postmortem_report", {})
}

for name, data in reports.items():
    if data:
        if isinstance(data, dict):
            print(f"  ✓ {name}: present (dict with {len(data)} keys)")
        elif isinstance(data, list):
            print(f"  ✓ {name}: present (list with {len(data)} items)")
        else:
            print(f"  ✓ {name}: present ({type(data).__name__})")
    else:
        print(f"  ⚠ {name}: empty or missing")

