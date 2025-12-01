"""
Tests for configuration management (project/config.py)
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from project.config import Config


class TestConfig:
    """Test suite for Config class."""
    
    def test_gemini_api_keys(self):
        """Test getting Gemini API keys."""
        keys = Config.GEMINI_API_KEYS()
        assert isinstance(keys, list)
        # In test environment, might be empty or have test keys
    
    def test_rotate_gemini_key(self):
        """Test rotating Gemini API keys."""
        key = Config.rotate_gemini_key()
        assert isinstance(key, str)
        # Should return a key or empty string
    
    def test_max_retries(self):
        """Test getting max retries."""
        retries = Config.max_retries()
        assert isinstance(retries, int)
        assert retries > 0
    
    def test_model_name(self):
        """Test model name configuration."""
        assert hasattr(Config, "MODEL_NAME")
        assert isinstance(Config.MODEL_NAME, str)
    
    def test_temperature(self):
        """Test temperature configuration."""
        assert hasattr(Config, "TEMPERATURE")
        assert isinstance(Config.TEMPERATURE, (int, float))
    
    def test_max_output_tokens(self):
        """Test max output tokens configuration."""
        assert hasattr(Config, "MAX_OUTPUT_TOKENS")
        assert isinstance(Config.MAX_OUTPUT_TOKENS, int)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

