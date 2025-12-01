"""
Tests for MainAgent orchestrator
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from project.main_agent import MainAgent


class TestMainAgent:
    """Test suite for MainAgent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Use mock mode for testing
        self.agent = MainAgent(mock_mode=True)
    
    def test_handle_message_repo_analysis(self):
        """Test handling repository analysis request."""
        result = self.agent.handle_message("Analyze this repository")
        assert "response" in result
        assert "plan" in result
        assert "tools_used" in result
        assert "safety_status" in result
        assert isinstance(result["response"], str)
    
    def test_handle_message_log_analysis(self):
        """Test handling log analysis request."""
        result = self.agent.handle_message("Analyze logs in error.log")
        assert "response" in result
        assert result["safety_status"] in ["APPROVED", "REJECTED"]
    
    def test_handle_message_migration(self):
        """Test handling migration request."""
        result = self.agent.handle_message("Migrate from Flask to FastAPI")
        assert "response" in result
        assert "plan" in result
    
    def test_handle_message_destructive(self):
        """Test handling destructive request."""
        result = self.agent.handle_message("Delete all files")
        assert "response" in result
        # Should be rejected or contain safe refusal
        assert result["safety_status"] == "REJECTED" or "cannot" in result["response"].lower()
    
    def test_get_conversation_summary(self):
        """Test getting conversation summary."""
        self.agent.handle_message("Hello")
        summary = self.agent.get_conversation_summary()
        assert isinstance(summary, str)
        assert len(summary) > 0
    
    def test_extract_github_url(self):
        """Test GitHub URL extraction."""
        text = "Analyze https://github.com/owner/repo"
        url = self.agent._extract_github_url(text)
        assert url == "https://github.com/owner/repo" or "github.com/owner/repo" in url
        
        text = "Check out owner/repo on GitHub"
        url = self.agent._extract_github_url(text)
        # May return full URL or just owner/repo depending on implementation
        assert url is not None
        assert "owner" in url and "repo" in url
    
    def test_clear_memory(self):
        """Test clearing memory."""
        self.agent.handle_message("Test message")
        self.agent.clear_memory()
        summary = self.agent.get_conversation_summary()
        # Should be empty or reset
        assert isinstance(summary, str)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

