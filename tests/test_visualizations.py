"""
Tests for visualization tools (project/tools/visualizations.py)
"""
import os
import sys
import tempfile

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from project.tools.visualizations import Visualizations
from PIL import Image


class TestVisualizations:
    """Test suite for Visualizations class."""
    
    def test_plot_dependency_graph(self):
        """Test dependency graph plotting."""
        dependency_data = {
            "nodes": ["file1.py", "file2.py", "file3.py"],
            "edges": [
                {"from": "file1.py", "to": "file2.py"},
                {"from": "file2.py", "to": "file3.py"}
            ]
        }
        
        result = Visualizations.plot_dependency_graph(dependency_data)
        assert isinstance(result, Image.Image)
        assert result.size[0] > 0
        assert result.size[1] > 0
    
    def test_plot_dependency_graph_empty(self):
        """Test dependency graph with empty data."""
        dependency_data = {
            "nodes": [],
            "edges": []
        }
        
        result = Visualizations.plot_dependency_graph(dependency_data)
        assert isinstance(result, Image.Image)
    
    def test_plot_complexity_heatmap(self):
        """Test complexity heatmap plotting."""
        complexity_data = [
            {"file": "file1.py", "complexity": {"avg_complexity": 5.0, "function_count": 3}},
            {"file": "file2.py", "complexity": {"avg_complexity": 8.0, "function_count": 5}}
        ]
        
        result = Visualizations.plot_complexity_heatmap(complexity_data)
        assert isinstance(result, Image.Image)
        assert result.size[0] > 0
        assert result.size[1] > 0
    
    def test_plot_complexity_heatmap_empty(self):
        """Test complexity heatmap with empty data."""
        result = Visualizations.plot_complexity_heatmap([])
        assert isinstance(result, Image.Image)
    
    def test_plot_error_timeline(self):
        """Test error timeline plotting."""
        log_data = {
            "errors": [
                {"timestamp": "2024-01-01 10:00:00", "content": "Error 1"},
                {"timestamp": "2024-01-01 11:00:00", "content": "Error 2"}
            ],
            "warnings": [
                {"timestamp": "2024-01-01 10:30:00", "content": "Warning 1"}
            ]
        }
        
        result = Visualizations.plot_error_timeline(log_data)
        assert isinstance(result, Image.Image)
        assert result.size[0] > 0
        assert result.size[1] > 0
    
    def test_plot_error_timeline_empty(self):
        """Test error timeline with no timestamped data."""
        log_data = {
            "errors": [{"content": "Error without timestamp"}],
            "warnings": []
        }
        
        result = Visualizations.plot_error_timeline(log_data)
        assert isinstance(result, Image.Image)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

