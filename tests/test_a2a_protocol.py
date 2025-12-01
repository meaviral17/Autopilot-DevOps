"""
Tests for A2A Protocol (Agent-to-Agent communication)
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from project.core.a2a_protocol import PlannerOutput, WorkerOutput, EvaluatorOutput


class TestA2AProtocol:
    """Test suite for A2A Protocol dataclasses."""
    
    def test_planner_output(self):
        """Test PlannerOutput dataclass."""
        output = PlannerOutput(
            emotion="neutral",
            risk_level="LOW",
            distress_score=3,
            action="repo_analysis",
            instruction="Analyze repository",
            technique_suggestion="none",
            needs_validation=True,
            save_preference=None
        )
        
        assert output.emotion == "neutral"
        assert output.risk_level == "LOW"
        assert output.action == "repo_analysis"
        
        # Test to_dict
        result_dict = output.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict["action"] == "repo_analysis"
    
    def test_worker_output(self):
        """Test WorkerOutput dataclass."""
        output = WorkerOutput(
            draft_response="Analysis complete",
            tools_used=["read_file", "get_dependency_graph"],
            technique_applied=None
        )
        
        assert output.draft_response == "Analysis complete"
        assert len(output.tools_used) == 2
        
        # Test to_dict
        result_dict = output.to_dict()
        assert isinstance(result_dict, dict)
        assert "draft_response" in result_dict
        assert "tools_used" in result_dict
    
    def test_evaluator_output(self):
        """Test EvaluatorOutput dataclass."""
        output = EvaluatorOutput(
            status="APPROVED",
            feedback="Response is safe",
            final_response="Analysis complete"
        )
        
        assert output.status == "APPROVED"
        assert output.feedback == "Response is safe"
        
        # Test to_dict
        result_dict = output.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict["status"] == "APPROVED"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

