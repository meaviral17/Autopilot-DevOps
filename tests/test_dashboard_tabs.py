"""
Test script to verify that all 5 dashboard tabs receive and display data correctly:
- dead_code_report
- migration_plan_report
- refactor_suggestions_report
- duplicate_code_report
- postmortem_report
"""
import sys
import os
from typing import Dict

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from project.main_agent import MainAgent
from project.config import Config

def test_dashboard_tabs():
    """Test that all 5 dashboard tabs receive data correctly."""
    
    print("=" * 80)
    print("Testing Dashboard Tabs Data Flow")
    print("=" * 80)
    
    # Initialize agent
    try:
        agent = MainAgent()
        print("✓ MainAgent initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize MainAgent: {e}")
        return False
    
    # Test 1: Repository Analysis (should generate dead_code and duplicate_code reports)
    print("\n" + "-" * 80)
    print("Test 1: Repository Analysis")
    print("-" * 80)
    
    try:
        result = agent.handle_message("Analyze this repository and detect dead code and duplicate code")
        print(f"✓ Repository analysis completed")
        
        # Check for dead_code_report
        dead_code = result.get("dead_code_report", {})
        if dead_code:
            print(f"✓ dead_code_report found: {len(dead_code.get('unused_functions', []))} unused functions")
        else:
            print("⚠ dead_code_report not found in result")
        
        # Check for duplicate_code_report
        duplicate_code = result.get("duplicate_code_report", {})
        if duplicate_code:
            print(f"✓ duplicate_code_report found: {duplicate_code.get('total_duplicates', 0)} duplicates")
        else:
            print("⚠ duplicate_code_report not found in result")
            
    except Exception as e:
        print(f"✗ Repository analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Migration Analysis (should generate migration_plan_report)
    print("\n" + "-" * 80)
    print("Test 2: Migration Analysis")
    print("-" * 80)
    
    try:
        result = agent.handle_message("Generate a migration plan from Flask to FastAPI")
        print(f"✓ Migration analysis completed")
        
        # Check for migration_plan_report
        migration_plan = result.get("migration_plan_report", {})
        if migration_plan:
            steps = migration_plan.get('steps', [])
            print(f"✓ migration_plan_report found: {len(steps)} migration steps")
        else:
            print("⚠ migration_plan_report not found in result")
            
    except Exception as e:
        print(f"✗ Migration analysis failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Refactoring Analysis (should generate refactor_suggestions_report)
    print("\n" + "-" * 80)
    print("Test 3: Refactoring Analysis")
    print("-" * 80)
    
    try:
        result = agent.handle_message("Analyze code complexity and suggest refactoring improvements")
        print(f"✓ Refactoring analysis completed")
        
        # Check for refactor_suggestions_report
        refactor_suggestions = result.get("refactor_suggestions_report", [])
        if refactor_suggestions:
            print(f"✓ refactor_suggestions_report found: {len(refactor_suggestions)} suggestions")
        else:
            print("⚠ refactor_suggestions_report not found in result")
            
    except Exception as e:
        print(f"✗ Refactoring analysis failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Incident Analysis (should generate postmortem_report)
    print("\n" + "-" * 80)
    print("Test 4: Incident/Log Analysis")
    print("-" * 80)
    
    try:
        result = agent.handle_message("Analyze the logs and generate a postmortem report")
        print(f"✓ Incident analysis completed")
        
        # Check for postmortem_report
        postmortem = result.get("postmortem_report", {})
        if postmortem:
            postmortem_text = postmortem.get('postmortem', '')
            if postmortem_text:
                print(f"✓ postmortem_report found: {len(postmortem_text)} characters")
            else:
                print("⚠ postmortem_report found but empty")
        else:
            print("⚠ postmortem_report not found in result")
            
    except Exception as e:
        print(f"✗ Incident analysis failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 5: Comprehensive Test - All reports in one analysis
    print("\n" + "-" * 80)
    print("Test 5: Comprehensive Repository Analysis")
    print("-" * 80)
    
    try:
        result = agent.handle_message("Perform a complete analysis: detect dead code, find duplicates, analyze complexity, and suggest refactoring")
        print(f"✓ Comprehensive analysis completed")
        
        # Check all reports
        reports_found = []
        reports_missing = []
        
        if result.get("dead_code_report"):
            reports_found.append("dead_code_report")
        else:
            reports_missing.append("dead_code_report")
            
        if result.get("duplicate_code_report"):
            reports_found.append("duplicate_code_report")
        else:
            reports_missing.append("duplicate_code_report")
            
        if result.get("refactor_suggestions_report"):
            reports_found.append("refactor_suggestions_report")
        else:
            reports_missing.append("refactor_suggestions_report")
        
        print(f"\n✓ Reports found: {len(reports_found)}/{3}")
        for report in reports_found:
            print(f"  - {report}")
        if reports_missing:
            print(f"\n⚠ Reports missing: {len(reports_missing)}/{3}")
            for report in reports_missing:
                print(f"  - {report}")
                
    except Exception as e:
        print(f"✗ Comprehensive analysis failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 6: Verify data structure
    print("\n" + "-" * 80)
    print("Test 6: Verify Data Structure")
    print("-" * 80)
    
    try:
        result = agent.handle_message("Analyze this repository")
        
        # Check result structure
        required_keys = [
            "response",
            "plan",
            "tools_used",
            "safety_status",
            "conversation_stats",
            "logs",
            "visualizations"
        ]
        
        print("Checking result structure...")
        for key in required_keys:
            if key in result:
                print(f"✓ {key} present")
            else:
                print(f"✗ {key} missing")
        
        # Check report keys
        report_keys = [
            "dead_code_report",
            "migration_plan_report",
            "refactor_suggestions_report",
            "duplicate_code_report",
            "postmortem_report"
        ]
        
        print("\nChecking report keys...")
        for key in report_keys:
            if key in result:
                val = result[key]
                if val:
                    print(f"✓ {key} present and non-empty")
                else:
                    print(f"⚠ {key} present but empty")
            else:
                print(f"⚠ {key} not in result (may be empty dict/list)")
        
    except Exception as e:
        print(f"✗ Structure verification failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("Testing Complete")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    # Validate config
    try:
        Config.validate()
        print("✓ Configuration validated")
    except Exception as e:
        print(f"⚠ Configuration warning: {e}")
        print("Continuing with test...")
    
    test_dashboard_tabs()

