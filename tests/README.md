# AutoPilot DevOps - Test Suite

This directory contains comprehensive tests for all components of the AutoPilot DevOps system.

## Test Structure

```
tests/
├── __init__.py
├── test_tools.py              # Tests for DevOps tools
├── test_github_tools.py       # Tests for GitHub integration
├── test_visualizations.py     # Tests for visualization tools
├── test_agents.py             # Tests for Planner, Worker, Evaluator
├── test_memory.py             # Tests for Session and Long-Term Memory
├── test_main_agent.py         # Tests for MainAgent orchestrator
├── test_config.py             # Tests for configuration
├── test_integration.py        # Integration tests for full pipeline
├── run_all_tests.py           # Test runner script
└── README.md                  # This file
```

## Running Tests

### Run All Tests
```bash
python tests/run_all_tests.py
```

### Run Specific Test File
```bash
pytest tests/test_tools.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=project --cov-report=html
```

### Run Individual Test Class
```bash
pytest tests/test_agents.py::TestPlanner -v
```

## Test Coverage

### Tools (`test_tools.py`)
- ✅ File reading
- ✅ Directory tree traversal
- ✅ Import extraction
- ✅ Dependency graph generation
- ✅ Complexity calculation
- ✅ Dead code detection
- ✅ Duplicate code detection
- ✅ Outdated library detection
- ✅ Log parsing
- ✅ Error clustering
- ✅ Anomaly detection
- ✅ Markdown documentation generation
- ✅ Migration plan generation
- ✅ Postmortem generation

### GitHub Tools (`test_github_tools.py`)
- ✅ URL parsing (various formats)
- ✅ Repository caching
- ✅ Invalid URL handling

### Visualizations (`test_visualizations.py`)
- ✅ Dependency graph plotting
- ✅ Complexity heatmap generation
- ✅ Error timeline plotting
- ✅ Empty data handling

### Agents (`test_agents.py`)
- ✅ Planner: Request analysis and routing
- ✅ Planner: Destructive request detection
- ✅ Worker: Repository analysis
- ✅ Worker: Incident analysis
- ✅ Worker: Migration handling
- ✅ Worker: Boundary enforcement
- ✅ Evaluator: Safe response approval
- ✅ Evaluator: Destructive command rejection
- ✅ Evaluator: Execution command detection

### Memory (`test_memory.py`)
- ✅ Session memory: Message storage
- ✅ Session memory: History formatting
- ✅ Session memory: History limits
- ✅ Session memory: Statistics
- ✅ Long-term memory: Preference storage
- ✅ Long-term memory: Repository analysis history
- ✅ Long-term memory: Migration preferences
- ✅ Long-term memory: Persistence

### Main Agent (`test_main_agent.py`)
- ✅ Repository analysis requests
- ✅ Log analysis requests
- ✅ Migration requests
- ✅ Destructive request handling
- ✅ Conversation summary
- ✅ GitHub URL extraction
- ✅ Memory management

### Integration (`test_integration.py`)
- ✅ Full pipeline: Repository analysis
- ✅ Full pipeline: Log analysis
- ✅ Full pipeline: Migration planning
- ✅ Component initialization
- ✅ Memory persistence
- ✅ Safety boundary enforcement

## Test Modes

Tests use **mock mode** by default to avoid requiring API keys:
- Agents use mock responses
- No actual Gemini API calls
- Fast execution
- No external dependencies

## Adding New Tests

1. Create test file: `tests/test_<component>.py`
2. Import the component to test
3. Use pytest fixtures for setup/teardown
4. Follow naming convention: `test_<functionality>`
5. Run tests to verify

## Example Test

```python
def test_my_feature():
    """Test my new feature."""
    # Setup
    component = MyComponent()
    
    # Execute
    result = component.do_something()
    
    # Assert
    assert result is not None
    assert result["status"] == "success"
```

## Continuous Integration

Tests can be integrated into CI/CD pipelines:
```bash
pytest tests/ --junitxml=test-results.xml
```

