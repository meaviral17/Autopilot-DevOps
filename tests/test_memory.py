"""
Tests for memory systems (Session and Long-Term Memory)
"""
import os
import sys
import tempfile
import json

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from project.memory.session_memory import SessionMemory
from project.memory.long_term_memory import LongTermMemory


class TestSessionMemory:
    """Test suite for SessionMemory."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.memory = SessionMemory(max_history=5)
    
    def test_add_message(self):
        """Test adding messages."""
        self.memory.add_message("user", "Hello")
        assert len(self.memory.history) == 1
        assert self.memory.history[0]["role"] == "user"
        assert self.memory.history[0]["content"] == "Hello"
    
    def test_get_history_string(self):
        """Test getting formatted history."""
        self.memory.add_message("user", "Hello")
        self.memory.add_message("assistant", "Hi there")
        
        history = self.memory.get_history_string()
        assert "Hello" in history
        assert "Hi there" in history
    
    def test_history_limit(self):
        """Test history limit enforcement."""
        for i in range(15):
            self.memory.add_message("user", f"Message {i}")
        
        # Should be limited to max_history * 2
        assert len(self.memory.history) <= 10
    
    def test_get_conversation_summary(self):
        """Test conversation summary."""
        self.memory.add_message("user", "Hello")
        summary = self.memory.get_conversation_summary()
        assert "1" in summary or "message" in summary.lower()
    
    def test_clear(self):
        """Test clearing memory."""
        self.memory.add_message("user", "Hello")
        self.memory.clear()
        assert len(self.memory.history) == 0
    
    def test_get_stats(self):
        """Test getting statistics."""
        self.memory.add_message("user", "Hello")
        self.memory.add_message("assistant", "Hi")
        
        stats = self.memory.get_stats()
        assert stats["total_messages"] == 2
        assert stats["user_messages"] == 1
        assert stats["assistant_messages"] == 1


class TestLongTermMemory:
    """Test suite for LongTermMemory."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.memory = LongTermMemory(storage_file=self.temp_file.name)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_update_preference(self):
        """Test updating preferences."""
        self.memory.update_preference("framework", "fastapi")
        assert self.memory.data["preferences"]["framework"] == "fastapi"
        
        # Verify persistence
        new_memory = LongTermMemory(storage_file=self.temp_file.name)
        assert new_memory.data["preferences"]["framework"] == "fastapi"
    
    def test_add_analyzed_repo(self):
        """Test adding analyzed repository."""
        analysis = {
            "timestamp": "2024-01-01",
            "avg_complexity": 5.0,
            "file_count": 10,
            "dependency_count": 5
        }
        self.memory.add_analyzed_repo("test/repo", analysis)
        assert "test/repo" in self.memory.data["analyzed_repos"]
    
    def test_migration_preferences(self):
        """Test migration preferences."""
        self.memory.set_migration_preference("flask", "fastapi")
        result = self.memory.get_migration_preference("flask")
        assert result == "fastapi"
    
    def test_get_preferences_string(self):
        """Test getting preferences as string."""
        self.memory.update_preference("framework", "fastapi")
        prefs = self.memory.get_preferences_string()
        assert "fastapi" in prefs or "framework" in prefs
    
    def test_clear(self):
        """Test clearing memory."""
        self.memory.update_preference("test", "value")
        self.memory.clear()
        assert len(self.memory.data["preferences"]) == 0


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

