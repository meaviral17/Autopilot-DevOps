"""
Tests for GitHub integration tools (project/tools/github_tools.py)
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from project.tools.github_tools import GitHubTools


class TestGitHubTools:
    """Test suite for GitHubTools class."""
    
    def test_parse_github_url_full(self):
        """Test parsing full GitHub URLs."""
        url = "https://github.com/owner/repo"
        result = GitHubTools.parse_github_url(url)
        assert result is not None
        assert result["owner"] == "owner"
        assert result["repo"] == "repo"
        assert result["full_name"] == "owner/repo"
    
    def test_parse_github_url_with_git(self):
        """Test parsing GitHub URL with .git extension."""
        url = "https://github.com/owner/repo.git"
        result = GitHubTools.parse_github_url(url)
        assert result is not None
        assert result["repo"] == "repo"
    
    def test_parse_github_url_ssh(self):
        """Test parsing SSH GitHub URLs."""
        url = "git@github.com:owner/repo.git"
        result = GitHubTools.parse_github_url(url)
        assert result is not None
        assert result["owner"] == "owner"
        assert result["repo"] == "repo"
    
    def test_parse_github_url_short(self):
        """Test parsing short format (owner/repo)."""
        url = "owner/repo"
        result = GitHubTools.parse_github_url(url)
        assert result is not None
        assert result["owner"] == "owner"
        assert result["repo"] == "repo"
    
    def test_parse_github_url_invalid(self):
        """Test parsing invalid URL."""
        url = "not-a-valid-url"
        result = GitHubTools.parse_github_url(url)
        assert result is None
    
    def test_list_cached_repositories(self):
        """Test listing cached repositories."""
        result = GitHubTools.list_cached_repositories()
        assert "repositories" in result
        assert "count" in result
        assert isinstance(result["repositories"], list)
        assert isinstance(result["count"], int)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

