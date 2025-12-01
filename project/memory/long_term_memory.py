"""
Long-Term Memory Module: Persists repository analysis preferences and DevOps settings.
"""
import json
import os
from typing import Dict, Any

class LongTermMemory:
    def __init__(self, storage_file: str = "devops_preferences.json"):
        self.storage_file = storage_file
        self._load_memory()

    def _load_memory(self):
        """Load memory from JSON file or initialize empty."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {"preferences": {}, "analyzed_repos": {}, "migration_preferences": {}}
        else:
            self.data = {"preferences": {}, "analyzed_repos": {}, "migration_preferences": {}}

    def _save_memory(self):
        """Persist memory to disk."""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving long-term memory: {e}")

    def update_preference(self, key: str, value: str):
        """Save a user preference (e.g., 'preferred_framework': 'fastapi')."""
        self.data["preferences"][key] = value
        self._save_memory()
    
    def add_analyzed_repo(self, repo_path: str, analysis_summary: Dict):
        """Store analysis results for a repository."""
        self.data["analyzed_repos"][repo_path] = {
            "last_analyzed": analysis_summary.get("timestamp", ""),
            "complexity": analysis_summary.get("avg_complexity", 0),
            "file_count": analysis_summary.get("file_count", 0),
            "dependencies": analysis_summary.get("dependency_count", 0)
        }
        self._save_memory()
    
    def get_migration_preference(self, source_framework: str) -> str:
        """Get preferred target framework for migration."""
        return self.data["migration_preferences"].get(source_framework, "fastapi")
    
    def set_migration_preference(self, source_framework: str, target_framework: str):
        """Set preferred target framework for migration."""
        self.data["migration_preferences"][source_framework] = target_framework
        self._save_memory()

    def get_preferences_string(self) -> str:
        """Format preferences for LLM context."""
        if not self.data["preferences"] and not self.data["analyzed_repos"]:
            return "No known user preferences or repository history."
        
        parts = []
        
        if self.data["preferences"]:
            parts.append("KNOWN USER PREFERENCES:")
            parts.append("\n".join(f"- {k}: {v}" for k, v in self.data["preferences"].items()))
        
        if self.data["analyzed_repos"]:
            parts.append("\nPREVIOUSLY ANALYZED REPOSITORIES:")
            for repo, info in list(self.data["analyzed_repos"].items())[:5]:  # Last 5
                parts.append(f"- {repo}: {info.get('file_count', 0)} files, complexity {info.get('complexity', 0)}")
        
        if self.data["migration_preferences"]:
            parts.append("\nMIGRATION PREFERENCES:")
            parts.append("\n".join(f"- {k} → {v}" for k, v in self.data["migration_preferences"].items()))
        
        return "\n".join(parts)

    def clear(self):
        """Wipe memory (useful for demo/testing)."""
        self.data = {"preferences": {}, "analyzed_repos": {}, "migration_preferences": {}}
        self._save_memory()
