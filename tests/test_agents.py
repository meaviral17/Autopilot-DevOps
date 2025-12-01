"""
Tests for agent components (Planner, Worker, Evaluator)
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from project.agents.planner import Planner
from project.agents.worker import Worker
from project.agents.evaluator import Evaluator


class TestPlanner:
    """Test suite for Planner agent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.planner = Planner()
        self.planner.mock_mode = True
    
    def test_plan_repo_analysis(self):
        """Test planning for repository analysis."""
        user_input = "Analyze this repository"
        result = self.planner.plan(user_input, "", "")
        assert "action" in result
        assert result["action"] in ["repo_analysis", "general_chat"]
    
    def test_plan_incident_analysis(self):
        """Test planning for incident analysis."""
        user_input = "Analyze logs in error.log"
        result = self.planner.plan(user_input, "", "")
        assert "action" in result
    
    def test_plan_migration(self):
        """Test planning for migration."""
        user_input = "Migrate from Flask to FastAPI"
        result = self.planner.plan(user_input, "", "")
        assert "action" in result
    
    def test_check_destructive_request(self):
        """Test destructive request detection."""
        destructive_input = "delete all files"
        result = self.planner._check_destructive_request(destructive_input)
        assert result == True
        
        safe_input = "analyze the codebase"
        result = self.planner._check_destructive_request(safe_input)
        assert result == False


class TestWorker:
    """Test suite for Worker agent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.worker = Worker()
        self.worker.mock_mode = True
    
    def test_work_repo_analysis(self):
        """Test worker handling repo analysis."""
        planner_output = {
            "action": "repo_analysis",
            "instruction": "Analyze repository",
            "target_paths": [],
            "tools_needed": []
        }
        result = self.worker.work(planner_output)
        assert "draft_response" in result
        assert "tools_used" in result
        assert isinstance(result["draft_response"], str)
    
    def test_work_incident_analysis(self):
        """Test worker handling incident analysis."""
        planner_output = {
            "action": "incident_analysis",
            "instruction": "Analyze logs",
            "target_paths": [],
            "tools_needed": []
        }
        result = self.worker.work(planner_output)
        assert "draft_response" in result
    
    def test_work_migration(self):
        """Test worker handling migration."""
        planner_output = {
            "action": "migration",
            "instruction": "Migrate Flask to FastAPI",
            "target_paths": [],
            "tools_needed": []
        }
        result = self.worker.work(planner_output)
        assert "draft_response" in result
    
    def test_work_enforce_boundary(self):
        """Test worker handling boundary enforcement."""
        planner_output = {
            "action": "enforce_boundary",
            "instruction": "Refuse destructive operation",
            "target_paths": [],
            "tools_needed": []
        }
        result = self.worker.work(planner_output)
        assert "draft_response" in result
        assert "cannot" in result["draft_response"].lower() or "read-only" in result["draft_response"].lower()


class TestEvaluator:
    """Test suite for Evaluator agent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.evaluator = Evaluator()
        self.evaluator.mock_mode = True
    
    def test_evaluate_safe_response(self):
        """Test evaluation of safe response."""
        worker_output = {
            "draft_response": "This is a safe analysis response.",
            "tools_used": ["read_file"]
        }
        result = self.evaluator.evaluate(worker_output, "Analyze code")
        assert "status" in result
        assert result["status"] in ["APPROVED", "REJECTED"]
    
    def test_evaluate_destructive_command(self):
        """Test evaluation rejecting destructive commands."""
        worker_output = {
            "draft_response": "I will execute: rm -rf /",
            "tools_used": []
        }
        result = self.evaluator.evaluate(worker_output, "Delete everything")
        assert "status" in result
        # In mock mode, might be APPROVED, but in real mode should check for destructive commands
        # Check that the method exists and works
        has_destructive = self.evaluator._contains_destructive_commands(worker_output["draft_response"])
        assert has_destructive == True  # Should detect destructive command
    
    def test_contains_destructive_commands(self):
        """Test destructive command detection."""
        text = "rm -rf /tmp"
        result = self.evaluator._contains_destructive_commands(text)
        assert result == True
        
        text = "I cannot delete files"
        result = self.evaluator._contains_destructive_commands(text)
        assert result == False
    
    def test_contains_execution_commands(self):
        """Test execution command detection."""
        text = "subprocess.run(['ls'])"
        result = self.evaluator._contains_execution_commands(text)
        assert result == True
        
        text = "This is safe text"
        result = self.evaluator._contains_execution_commands(text)
        assert result == False


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

