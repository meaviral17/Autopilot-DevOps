"""
Tests for DevOps tools (project/tools/tools.py)
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from project.tools.tools import Tools


class TestTools:
    """Test suite for Tools class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.py")
        
        # Create a test Python file
        with open(self.test_file, 'w') as f:
            f.write("""
import os
import sys
from typing import List, Dict

def hello_world():
    print("Hello, World!")
    return "Hello"

def complex_function(x: int, y: int) -> int:
    if x > 0:
        if y > 0:
            return x + y
        else:
            return x - y
    else:
        return 0

class TestClass:
    def method1(self):
        pass
    
    def method2(self):
        if True:
            return 1
        return 0
""")
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_read_file(self):
        """Test file reading."""
        result = Tools.read_file(self.test_file)
        assert result["exists"] == True
        assert "hello_world" in result["content"]
        assert result["lines"] > 0
        assert result["size"] > 0
    
    def test_read_file_nonexistent(self):
        """Test reading non-existent file."""
        result = Tools.read_file("nonexistent_file.py")
        assert result["exists"] == False
        assert result["error"] is not None
    
    def test_read_directory_tree(self):
        """Test directory tree reading."""
        result = Tools.read_directory_tree(self.test_dir)
        assert "tree" in result
        assert result["file_count"] > 0
        assert result["root"] == self.test_dir
    
    def test_extract_imports(self):
        """Test import extraction."""
        result = Tools.extract_imports(self.test_file)
        assert "imports" in result
        assert "from_imports" in result
        assert "os" in result["imports"] or any(i["module"] == "os" for i in result["from_imports"])
    
    def test_get_dependency_graph(self):
        """Test dependency graph generation."""
        result = Tools.get_dependency_graph(self.test_dir)
        assert "nodes" in result
        assert "edges" in result
        assert isinstance(result["nodes"], list)
        assert isinstance(result["edges"], list)
    
    def test_compute_complexity(self):
        """Test complexity calculation."""
        result = Tools.compute_complexity(self.test_file)
        assert "complexity" in result
        assert "functions" in result
        assert "classes" in result
        assert result["complexity"] > 0
        assert len(result["functions"]) > 0
    
    def test_detect_dead_code(self):
        """Test dead code detection."""
        result = Tools.detect_dead_code(self.test_dir)
        assert "unused_functions" in result
        assert "unused_imports" in result
        assert isinstance(result["unused_functions"], list)
        assert isinstance(result["unused_imports"], list)
    
    def test_detect_duplicate_code(self):
        """Test duplicate code detection."""
        # Create two similar files
        file1 = os.path.join(self.test_dir, "file1.py")
        file2 = os.path.join(self.test_dir, "file2.py")
        
        with open(file1, 'w') as f:
            f.write("def same_function():\n    return 1\n    return 2\n")
        with open(file2, 'w') as f:
            f.write("def same_function():\n    return 1\n    return 2\n")
        
        result = Tools.detect_duplicate_code(self.test_dir)
        assert "duplicates" in result
        assert "total_duplicates" in result
        assert isinstance(result["duplicates"], list)
    
    def test_list_outdated_libraries(self):
        """Test outdated library detection."""
        # Create a requirements.txt
        req_file = os.path.join(self.test_dir, "requirements.txt")
        with open(req_file, 'w') as f:
            f.write("flask==2.0.0\nrequests>=2.25.0\n")
        
        result = Tools.list_outdated_libraries(req_file)
        assert "packages" in result
        assert "deprecated" in result
        assert isinstance(result["packages"], list)
    
    def test_parse_logs(self):
        """Test log parsing."""
        log_file = os.path.join(self.test_dir, "test.log")
        with open(log_file, 'w') as f:
            f.write("2024-01-01 10:00:00 ERROR: Test error\n")
            f.write("2024-01-01 10:01:00 WARNING: Test warning\n")
            f.write("2024-01-01 10:02:00 INFO: Test info\n")
        
        result = Tools.parse_logs(log_file)
        assert "entries" in result
        assert "errors" in result
        assert "warnings" in result
        assert len(result["errors"]) > 0
        assert len(result["warnings"]) > 0
    
    def test_cluster_errors(self):
        """Test error clustering."""
        log_data = {
            "errors": [
                {"content": "ValueError: Invalid input"},
                {"content": "ValueError: Invalid input"},
                {"content": "KeyError: Missing key"}
            ]
        }
        result = Tools.cluster_errors(log_data)
        assert "clusters" in result
        assert "top_errors" in result
        assert result["total_errors"] == 3
    
    def test_detect_anomalies(self):
        """Test anomaly detection."""
        log_data = {
            "errors": [
                {"timestamp": "2024-01-01 10:00:00"},
                {"timestamp": "2024-01-01 10:00:00"},
                {"timestamp": "2024-01-01 10:01:00"}
            ],
            "warnings": []
        }
        result = Tools.detect_anomalies(log_data)
        assert "anomalies" in result
        assert "spikes" in result
        assert isinstance(result["anomalies"], list)
    
    def test_generate_markdown_docs(self):
        """Test markdown documentation generation."""
        repo_map = {
            "tree": {"src": {"main.py": {"type": "file"}}},
            "nodes": ["src/main.py"]
        }
        result = Tools.generate_markdown_docs(repo_map)
        assert "content" in result
        assert "sections" in result
        assert len(result["content"]) > 0
    
    def test_generate_migration_plan(self):
        """Test migration plan generation."""
        result = Tools.generate_migration_plan("flask", "fastapi")
        assert "plan" in result
        assert "steps" in result
        assert "breaking_changes" in result
        assert len(result["steps"]) > 0
    
    def test_generate_postmortem(self):
        """Test postmortem generation."""
        log_data = {
            "errors": [
                {"content": "Error 1", "timestamp": "2024-01-01 10:00:00"},
                {"content": "Error 2", "timestamp": "2024-01-01 10:01:00"}
            ],
            "warnings": [],
            "clusters": {
                "top_errors": [
                    {"message": "Error 1", "count": 2}
                ],
                "unique_patterns": 1
            }
        }
        result = Tools.generate_postmortem(log_data, "Test incident")
        assert "postmortem" in result
        assert "sections" in result
        assert "recommendations" in result
        assert len(result["postmortem"]) > 0


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

