"""
GitHub Integration Tools for cloning and managing repositories.
Supports both public and private repositories with authentication.
"""
import os
import re
import shutil
import tempfile
from typing import Dict, Optional, Tuple
from pathlib import Path
import subprocess


class GitHubTools:
    """Tools for GitHub repository operations."""
    
    # Cache directory for cloned repositories
    CACHE_DIR = os.path.join(tempfile.gettempdir(), "autopilot_repos")
    
    @staticmethod
    def _ensure_cache_dir():
        """Ensure the cache directory exists."""
        os.makedirs(GitHubTools.CACHE_DIR, exist_ok=True)
    
    @staticmethod
    def parse_github_url(url: str) -> Optional[Dict[str, str]]:
        """Parse GitHub URL to extract owner and repo name.
        
        Supports formats:
        - https://github.com/owner/repo
        - https://github.com/owner/repo.git
        - git@github.com:owner/repo.git
        - owner/repo
        
        Args:
            url: GitHub repository URL or owner/repo format
            
        Returns:
            Dict with 'owner', 'repo', 'full_name', 'url' or None if invalid
        """
        # Handle owner/repo format
        if '/' in url and 'github.com' not in url and '@' not in url:
            parts = url.split('/')
            if len(parts) == 2:
                return {
                    "owner": parts[0],
                    "repo": parts[1].replace('.git', ''),
                    "full_name": f"{parts[0]}/{parts[1].replace('.git', '')}",
                    "url": f"https://github.com/{parts[0]}/{parts[1].replace('.git', '')}"
                }
        
        # Handle full URLs
        patterns = [
            r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$',
            r'git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner = match.group(1)
                repo = match.group(2).replace('.git', '')
                return {
                    "owner": owner,
                    "repo": repo,
                    "full_name": f"{owner}/{repo}",
                    "url": f"https://github.com/{owner}/{repo}"
                }
        
        return None
    
    @staticmethod
    def clone_repository(repo_url: str, github_token: Optional[str] = None, 
                        branch: Optional[str] = None) -> Dict:
        """Clone a GitHub repository to a temporary directory.
        
        Args:
            repo_url: GitHub repository URL or owner/repo format
            github_token: Optional GitHub personal access token for private repos
            branch: Optional branch name (defaults to default branch)
            
        Returns:
            Dict with 'success', 'local_path', 'error', 'repo_info'
        """
        GitHubTools._ensure_cache_dir()
        
        # Parse URL
        repo_info = GitHubTools.parse_github_url(repo_url)
        if not repo_info:
            return {
                "success": False,
                "local_path": None,
                "error": f"Invalid GitHub URL format: {repo_url}",
                "repo_info": None
            }
        
        # Determine local path
        repo_name = repo_info["full_name"].replace('/', '_')
        local_path = os.path.join(GitHubTools.CACHE_DIR, repo_name)
        
        # Check if already cloned
        if os.path.exists(local_path) and os.path.isdir(local_path):
            # Check if it's a valid git repo
            if os.path.exists(os.path.join(local_path, '.git')):
                return {
                    "success": True,
                    "local_path": local_path,
                    "error": None,
                    "repo_info": repo_info,
                    "cached": True
                }
            else:
                # Remove invalid directory
                try:
                    shutil.rmtree(local_path)
                except Exception:
                    pass
        
        # Build clone URL
        if github_token:
            # Use token for authentication
            clone_url = f"https://{github_token}@github.com/{repo_info['full_name']}.git"
        else:
            # Public repo
            clone_url = f"https://github.com/{repo_info['full_name']}.git"
        
        # Clone repository
        try:
            os.makedirs(local_path, exist_ok=True)
            
            clone_cmd = ["git", "clone", "--depth", "1"]
            if branch:
                clone_cmd.extend(["-b", branch])
            clone_cmd.extend([clone_url, local_path])
            
            result = subprocess.run(
                clone_cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode != 0:
                # Clean up on failure
                try:
                    shutil.rmtree(local_path)
                except Exception:
                    pass
                
                error_msg = result.stderr or result.stdout or "Unknown git error"
                # Don't expose token in error message
                if github_token and github_token in error_msg:
                    error_msg = error_msg.replace(github_token, "***")
                
                return {
                    "success": False,
                    "local_path": None,
                    "error": f"Failed to clone repository: {error_msg}",
                    "repo_info": repo_info
                }
            
            return {
                "success": True,
                "local_path": local_path,
                "error": None,
                "repo_info": repo_info,
                "cached": False
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "local_path": None,
                "error": "Repository clone timed out (repository may be too large)",
                "repo_info": repo_info
            }
        except Exception as e:
            return {
                "success": False,
                "local_path": None,
                "error": f"Error cloning repository: {str(e)}",
                "repo_info": repo_info
            }
    
    @staticmethod
    def update_repository(local_path: str, github_token: Optional[str] = None) -> Dict:
        """Update an existing cloned repository (git pull).
        
        Args:
            local_path: Path to the cloned repository
            github_token: Optional GitHub token for private repos
            
        Returns:
            Dict with 'success', 'error'
        """
        if not os.path.exists(local_path) or not os.path.exists(os.path.join(local_path, '.git')):
            return {
                "success": False,
                "error": "Repository not found or not a valid git repository"
            }
        
        try:
            result = subprocess.run(
                ["git", "pull"],
                cwd=local_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr or result.stdout or "Unknown git error"
                }
            
            return {
                "success": True,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error updating repository: {str(e)}"
            }
    
    @staticmethod
    def get_repository_info(repo_url: str, github_token: Optional[str] = None) -> Dict:
        """Get information about a GitHub repository without cloning.
        
        Args:
            repo_url: GitHub repository URL or owner/repo format
            github_token: Optional GitHub token for private repos
            
        Returns:
            Dict with repository metadata
        """
        import requests
        
        repo_info = GitHubTools.parse_github_url(repo_url)
        if not repo_info:
            return {
                "success": False,
                "error": f"Invalid GitHub URL format: {repo_url}"
            }
        
        # Use GitHub API
        api_url = f"https://api.github.com/repos/{repo_info['full_name']}"
        headers = {}
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        
        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "name": data.get("name"),
                    "full_name": data.get("full_name"),
                    "description": data.get("description"),
                    "language": data.get("language"),
                    "stars": data.get("stargazers_count", 0),
                    "forks": data.get("forks_count", 0),
                    "is_private": data.get("private", False),
                    "default_branch": data.get("default_branch", "main"),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "error": None
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "error": "Repository not found (may be private or not exist)"
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "error": "Authentication failed. Please check your GitHub token."
                }
            else:
                return {
                    "success": False,
                    "error": f"GitHub API error: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error fetching repository info: {str(e)}"
            }
    
    @staticmethod
    def cleanup_repository(local_path: str) -> Dict:
        """Remove a cloned repository from cache.
        
        Args:
            local_path: Path to the repository to remove
            
        Returns:
            Dict with 'success', 'error'
        """
        try:
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
                return {
                    "success": True,
                    "error": None
                }
            return {
                "success": True,
                "error": None,
                "message": "Repository already removed"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error removing repository: {str(e)}"
            }
    
    @staticmethod
    def list_cached_repositories() -> Dict:
        """List all cached repositories.
        
        Returns:
            Dict with 'repositories' list
        """
        GitHubTools._ensure_cache_dir()
        
        repos = []
        if os.path.exists(GitHubTools.CACHE_DIR):
            for item in os.listdir(GitHubTools.CACHE_DIR):
                item_path = os.path.join(GitHubTools.CACHE_DIR, item)
                if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, '.git')):
                    repos.append({
                        "name": item,
                        "path": item_path,
                        "full_name": item.replace('_', '/')
                    })
        
        return {
            "repositories": repos,
            "count": len(repos)
        }

