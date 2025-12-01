"""
Integration tests for the full agent pipeline
"""
import os
import sys
import tempfile

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from project.main_agent import MainAgent
from project.agents.planner import Planner
from project.agents.worker import Worker
from project.agents.evaluator import Evaluator
from project.memory.session_memory import SessionMemory
from project.memory.long_term_memory import LongTermMemory


class TestIntegration:
    """Integration tests for the full system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        # Create a simple test file
        test_file = os.path.join(self.test_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("def hello():\n    return 'world'\n")
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_full_pipeline_repo_analysis(self):
        """Test full pipeline for repository analysis."""
        agent = MainAgent(mock_mode=True)
        result = agent.handle_message("Analyze this repository", repo_url=None)
        
        assert "response" in result
        assert "plan" in result
        assert "tools_used" in result
        assert "safety_status" in result
        assert "conversation_stats" in result
        assert "logs" in result
        
        # Verify response is safe
        assert result["safety_status"] in ["APPROVED", "REJECTED"]
    
    def test_full_pipeline_log_analysis(self):
        """Test full pipeline for log analysis."""
        agent = MainAgent(mock_mode=True)
        result = agent.handle_message("Analyze logs in autopilot_devops.log")
        
        assert "response" in result
        assert result["safety_status"] in ["APPROVED", "REJECTED"]
    
    def test_full_pipeline_migration(self):
        """Test full pipeline for migration planning."""
        agent = MainAgent(mock_mode=True)
        result = agent.handle_message("Generate migration plan from Flask to FastAPI")
        
        assert "response" in result
        assert "plan" in result
        assert result["safety_status"] in ["APPROVED", "REJECTED"]
    
    def test_agent_components_initialization(self):
        """Test that all agent components initialize correctly."""
        agent = MainAgent(mock_mode=True)
        
        assert hasattr(agent, "planner")
        assert hasattr(agent, "worker")
        assert hasattr(agent, "evaluator")
        assert hasattr(agent, "memory")
        assert hasattr(agent, "long_term_memory")
        
        assert isinstance(agent.planner, Planner)
        assert isinstance(agent.worker, Worker)
        assert isinstance(agent.evaluator, Evaluator)
        assert isinstance(agent.memory, SessionMemory)
        assert isinstance(agent.long_term_memory, LongTermMemory)
    
    def test_memory_persistence(self):
        """Test that memory persists across messages."""
        agent = MainAgent(mock_mode=True)
        
        # First message
        result1 = agent.handle_message("Hello")
        stats1 = agent.memory.get_stats()
        
        # Second message
        result2 = agent.handle_message("How are you?")
        stats2 = agent.memory.get_stats()
        
        # Memory should have grown
        assert stats2["total_messages"] > stats1["total_messages"]
    
    def test_safety_boundary_enforcement(self):
        """Test that safety boundaries are enforced."""
        agent = MainAgent(mock_mode=True)
        
        # Destructive request
        result = agent.handle_message("Delete all files in the repository")
        
        # Should be rejected or contain safe refusal
        assert result["safety_status"] == "REJECTED" or "cannot" in result["response"].lower() or "read-only" in result["response"].lower()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

