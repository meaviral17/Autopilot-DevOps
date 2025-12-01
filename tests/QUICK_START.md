# Quick Test Guide

## Run All Tests
```bash
python tests/run_all_tests.py
```

## Run with Coverage Report
```bash
python tests/run_with_coverage.py
```

## Run Specific Test File
```bash
pytest tests/test_tools.py -v
```

## Run Specific Test
```bash
pytest tests/test_agents.py::TestPlanner::test_plan_repo_analysis -v
```

## Test Results
✅ **72/72 tests passing** (100% pass rate)

## Test Files

| File | Tests | Description |
|------|-------|-------------|
| `test_tools.py` | 15 | DevOps tools (file reading, complexity, dead code, etc.) |
| `test_github_tools.py` | 6 | GitHub integration (URL parsing, caching) |
| `test_visualizations.py` | 6 | Visualization tools (graphs, heatmaps, timelines) |
| `test_agents.py` | 10 | Agent components (Planner, Worker, Evaluator) |
| `test_memory.py` | 11 | Memory systems (Session, Long-Term) |
| `test_main_agent.py` | 7 | Main orchestrator |
| `test_integration.py` | 6 | Full pipeline integration |
| `test_a2a_protocol.py` | 3 | A2A protocol dataclasses |
| `test_config.py` | 6 | Configuration management |
| **Total** | **72** | **All components tested** |

## Test Features

- ✅ **Mock Mode**: No API keys required
- ✅ **Fast Execution**: ~4-6 seconds
- ✅ **Comprehensive**: All major components covered
- ✅ **CI/CD Ready**: Can be integrated into pipelines

