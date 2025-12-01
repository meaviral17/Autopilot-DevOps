# AutoPilot DevOps - Complete Project Documentation

## Executive Summary

**AutoPilot DevOps** is a production-ready, multi-agent system for automated code intelligence, log analysis, and DevOps automation. Built for the **Kaggle × Google Agents Intensive 2025 Capstone**, this system transforms complex codebases into actionable insights through intelligent analysis, visualization, and automation recommendations.

### Core Value Proposition

- **🔍 Intelligent Code Analysis**: Deep repository understanding with dependency mapping, complexity analysis, and dead code detection
- **📊 Visual Intelligence**: Interactive visualizations for dependencies, complexity heatmaps, and error timelines
- **🛡️ Safety-First Architecture**: Triple-layer safety system ensuring read-only operations and secure analysis
- **🤖 Multi-Agent Intelligence**: Specialized agents (Planner, Worker, Evaluator) working in coordination
- **💾 Persistent Memory**: Remembers user preferences and analysis history across sessions
- **📈 Real-Time Observability**: Live metrics, charts, and comprehensive logging

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features Guide & Use Cases](#features-guide--use-cases)
3. [System Architecture](#system-architecture)
4. [Core Components](#core-components)
5. [Agent System](#agent-system)
6. [Tools & Utilities](#tools--utilities)
7. [Visualization System](#visualization-system)
8. [Memory Systems](#memory-systems)
9. [Safety & Security](#safety--security)
10. [User Interface](#user-interface)
11. [GitHub Integration](#github-integration)
12. [Deployment](#deployment)
13. [Testing](#testing)
14. [Technology Stack](#technology-stack)
15. [API Reference](#api-reference)
16. [Performance & Scalability](#performance--scalability)
17. [Future Roadmap](#future-roadmap)

---

## Project Overview

### Project Transformation

AutoPilot DevOps was transformed from a mental health companion system to a comprehensive DevOps intelligence platform, demonstrating the flexibility and power of multi-agent architecture. The system maintains the same robust safety architecture while applying it to code analysis and DevOps automation.

### Key Achievements

- ✅ **20+ Analysis Tools**: Comprehensive code intelligence capabilities
- ✅ **3 Visualization Types**: Dependency graphs, complexity heatmaps, error timelines
- ✅ **72 Test Cases**: 100% component coverage with comprehensive test suite
- ✅ **11 Dashboard Tabs**: Complete observability and analysis interface
- ✅ **GitHub Integration**: Public and private repository analysis
- ✅ **Dark Mode UI**: Modern Material Design interface with Vercel-like aesthetics
- ✅ **Production Deployment**: Live on Hugging Face Spaces

### Competition Compliance

**Kaggle × Google Agents Intensive 2025 Capstone Requirements**:

- ✅ **Multi-Agent System**: 3 specialized agents (Planner, Worker, Evaluator)
- ✅ **Typed A2A Protocol**: Structured communication via dataclasses
- ✅ **Tools**: 20+ code intelligence tools
- ✅ **Session Memory**: Last 8 turns maintained
- ✅ **Long-Term Memory**: Persistent JSON storage
- ✅ **Observability**: Live logs, charts, and metrics
- ✅ **Dedicated Evaluator Agent**: Final safety guardrail
- ✅ **Context Engineering**: System prompts for each agent
- ✅ **Gemini 2.0 Flash**: Primary AI model
- ✅ **Public Deployment**: Hugging Face Spaces ready

---

## Features Guide & Use Cases

This section provides a comprehensive guide to all features of AutoPilot DevOps, including practical use cases and sample prompts to help you get the most out of the system.

### 🎯 Quick Start

**Basic Repository Analysis:**
```
Analyze this repository: https://github.com/user/repo
```

**Local Repository Analysis:**
```
Analyze the current repository and provide a comprehensive overview
```

---

### 📊 Feature Categories

#### 1. Repository Intelligence & Code Analysis

**Features:**
- Complete repository structure analysis
- Dependency graph visualization
- Code complexity metrics
- Dead code detection
- Duplicate code detection
- Architecture documentation

**Use Cases:**
- Understanding a new codebase
- Identifying technical debt
- Preparing for code reviews
- Onboarding new team members
- Refactoring planning

**Sample Prompts:**

**Comprehensive Repository Analysis:**
```
Perform a complete analysis of this repository:
- Generate dependency graph
- Analyze code complexity
- Detect dead code
- Find duplicate code blocks
- Create architecture overview
```

**Quick Overview:**
```
Give me a quick overview of this repository's structure and main components
```

**Dependency Analysis:**
```
Analyze all dependencies in this repository and show me the dependency graph
```

**Complexity Analysis:**
```
Identify the most complex files in this repository and show a complexity heatmap
```

**Dead Code Detection:**
```
Find all unused functions and imports in this codebase
```

**Duplicate Code Detection:**
```
Detect duplicate code blocks across all files in this repository
```

**Architecture Documentation:**
```
Generate comprehensive architecture documentation for this repository
```

---

#### 2. Code Quality & Refactoring

**Features:**
- Complexity-based refactoring suggestions
- Code quality metrics
- Maintainability analysis
- Refactoring recommendations

**Use Cases:**
- Improving code maintainability
- Reducing technical debt
- Preparing code for production
- Code quality audits

**Sample Prompts:**

**Refactoring Suggestions:**
```
Analyze code complexity and suggest refactoring improvements for high-complexity files
```

**Code Quality Report:**
```
Generate a code quality report with metrics and improvement suggestions
```

**Maintainability Analysis:**
```
Analyze the maintainability of this codebase and identify areas for improvement
```

**Targeted Refactoring:**
```
Suggest refactoring improvements for app.py and project/main_agent.py
```

**Complexity-Based Refactoring:**
```
Find the top 10 most complex files and provide specific refactoring suggestions for each
```

---

#### 3. Incident Analysis & Postmortem

**Features:**
- Log file parsing and analysis
- Error clustering and pattern detection
- Anomaly detection
- Error timeline visualization
- Automated postmortem generation

**Use Cases:**
- Debugging production issues
- Incident investigation
- Root cause analysis
- Performance monitoring
- Error pattern identification

**Sample Prompts:**

**Log Analysis:**
```
Analyze the logs in autopilot_devops.log and identify common errors
```

**Error Timeline:**
```
Generate an error timeline visualization for the last 24 hours from the logs
```

**Incident Investigation:**
```
Investigate the incident in the logs and generate a postmortem report
```

**Error Clustering:**
```
Cluster similar errors from the log files and identify patterns
```

**Anomaly Detection:**
```
Detect anomalies in the log data and highlight unusual patterns
```

**Root Cause Analysis:**
```
Analyze the logs to find the root cause of the recent errors
```

**Postmortem Generation:**
```
Generate a complete postmortem report for the incident in the logs
```

**Multiple Log Files:**
```
Analyze all log files in the logs/ directory and provide a comprehensive error analysis
```

---

#### 4. Migration Planning

**Features:**
- Framework migration strategies
- Dependency analysis for migrations
- Breaking changes identification
- Step-by-step migration plans
- Compatibility assessment

**Use Cases:**
- Framework upgrades (e.g., Flask → FastAPI)
- Python version migrations (2.x → 3.x)
- Library updates
- Architecture migrations
- Technology stack changes

**Sample Prompts:**

**Framework Migration:**
```
Generate a migration plan from Flask to FastAPI for this repository
```

**Python Version Migration:**
```
Create a migration plan to upgrade from Python 2.7 to Python 3.11
```

**Dependency Migration:**
```
Plan the migration from requests library to httpx
```

**Breaking Changes Analysis:**
```
Identify all breaking changes for migrating from Django 3.2 to Django 4.2
```

**Step-by-Step Migration:**
```
Provide a detailed step-by-step migration plan from SQLAlchemy 1.4 to 2.0
```

**Compatibility Check:**
```
Check compatibility of this codebase with Python 3.12 and identify required changes
```

---

#### 5. GitHub Repository Analysis

**Features:**
- Public repository analysis
- Private repository analysis (with token)
- Automatic repository cloning
- Remote repository intelligence

**Use Cases:**
- Analyzing open-source projects
- Code review preparation
- Security audits
- Dependency analysis of external projects
- Learning from other codebases

**Sample Prompts:**

**Public Repository:**
```
Analyze this GitHub repository: https://github.com/tensorflow/tensorflow
```

**Private Repository:**
```
Analyze my private repository: https://github.com/username/private-repo
(Note: Provide GitHub token in the UI)
```

**Repository Overview:**
```
Give me an overview of this repository: https://github.com/user/repo
```

**Specific Analysis:**
```
Analyze the dependencies and complexity of https://github.com/user/repo
```

**Repository Comparison:**
```
Compare the architecture of these two repositories:
- https://github.com/user/repo1
- https://github.com/user/repo2
```

---

#### 6. Visualization & Dashboards

**Features:**
- Interactive dependency graphs
- Complexity heatmaps
- Error timeline charts
- Real-time metrics dashboard
- Code health monitoring

**Use Cases:**
- Visual code understanding
- Presentation preparation
- Team communication
- Technical documentation
- Performance monitoring

**Sample Prompts:**

**Dependency Graph:**
```
Generate a dependency graph visualization for this repository
```

**Complexity Heatmap:**
```
Create a complexity heatmap showing the most complex modules
```

**Error Timeline:**
```
Show me an error timeline visualization for the last week
```

**Full Visualization Suite:**
```
Generate all visualizations: dependency graph, complexity heatmap, and error timeline
```

**Metrics Dashboard:**
```
Show me the code health metrics and complexity trends
```

---

### 🎨 Advanced Use Cases

#### Use Case 1: Pre-Code Review Analysis

**Scenario:** Before submitting a PR, analyze your code for issues.

**Prompt:**
```
Before I submit this PR, analyze the repository for:
1. Dead code that should be removed
2. Duplicate code that can be refactored
3. High complexity areas that need attention
4. Missing documentation
```

#### Use Case 2: Technical Debt Assessment

**Scenario:** Assess technical debt in a legacy codebase.

**Prompt:**
```
Perform a comprehensive technical debt assessment:
- Identify all dead code
- Find duplicate code blocks
- List files with complexity > 10
- Generate refactoring suggestions
- Create a prioritized action plan
```

#### Use Case 3: Incident Response

**Scenario:** Production incident requires quick analysis.

**Prompt:**
```
URGENT: Analyze the production logs and:
1. Identify the root cause
2. Generate error timeline
3. Cluster similar errors
4. Create postmortem report
5. Suggest preventive measures
```

#### Use Case 4: Migration Planning

**Scenario:** Planning a major framework upgrade.

**Prompt:**
```
I need to migrate from Flask to FastAPI. Please:
1. Analyze current Flask dependencies
2. Identify breaking changes
3. Create step-by-step migration plan
4. List all files that need modification
5. Provide code examples for migration
```

#### Use Case 5: Onboarding New Developer

**Scenario:** Help a new team member understand the codebase.

**Prompt:**
```
I'm new to this codebase. Please provide:
1. Architecture overview
2. Dependency graph
3. Main entry points
4. Most complex files to understand first
5. Key design patterns used
```

#### Use Case 6: Security Audit Preparation

**Scenario:** Prepare for a security audit.

**Prompt:**
```
Prepare this repository for a security audit:
- Analyze all dependencies for vulnerabilities
- Identify potentially unsafe code patterns
- Check for hardcoded secrets
- Review file permissions
- Generate security report
```

#### Use Case 7: Performance Optimization

**Scenario:** Identify performance bottlenecks.

**Prompt:**
```
Analyze this repository for performance issues:
- Identify high complexity functions
- Find potential bottlenecks
- Suggest optimization opportunities
- Generate performance improvement plan
```

---

### 💡 Best Practices & Tips

#### 1. **Be Specific**
❌ "Analyze the code"  
✅ "Analyze the repository structure, dependencies, and complexity metrics"

#### 2. **Use Multiple Features**
❌ "Check for dead code"  
✅ "Perform complete analysis: dead code, duplicates, complexity, and refactoring suggestions"

#### 3. **Specify Target Files**
❌ "Refactor the code"  
✅ "Suggest refactoring improvements for app.py and project/main_agent.py"

#### 4. **Request Visualizations**
❌ "Show dependencies"  
✅ "Generate dependency graph visualization and complexity heatmap"

#### 5. **Combine Related Tasks**
❌ "Analyze logs" then "Generate postmortem"  
✅ "Analyze logs and generate a complete postmortem report with error timeline"

#### 6. **Use GitHub URLs**
✅ "Analyze https://github.com/user/repo and generate dependency graph"

#### 7. **Request Comprehensive Reports**
✅ "Perform a complete repository analysis with all visualizations and reports"

---

### 📋 Feature Checklist

Use this checklist to ensure you're utilizing all features:

**Repository Analysis:**
- [ ] Dependency graph generated
- [ ] Complexity heatmap created
- [ ] Dead code detected
- [ ] Duplicate code found
- [ ] Architecture documented

**Code Quality:**
- [ ] Refactoring suggestions received
- [ ] Code quality metrics reviewed
- [ ] Maintainability assessed

**Incident Analysis:**
- [ ] Logs parsed and analyzed
- [ ] Error timeline generated
- [ ] Postmortem created
- [ ] Anomalies detected

**Migration Planning:**
- [ ] Migration plan generated
- [ ] Breaking changes identified
- [ ] Step-by-step guide created

**Visualizations:**
- [ ] Dependency graph viewed
- [ ] Complexity heatmap reviewed
- [ ] Error timeline analyzed
- [ ] Metrics dashboard checked

---

### 🚀 Quick Reference: Common Prompts

**Repository Overview:**
```
Analyze this repository and provide a comprehensive overview
```

**Full Analysis:**
```
Perform a complete analysis: dependencies, complexity, dead code, duplicates, and visualizations
```

**Refactoring:**
```
Suggest refactoring improvements for high-complexity files
```

**Incident:**
```
Analyze logs and generate postmortem with error timeline
```

**Migration:**
```
Create migration plan from [source] to [target]
```

**GitHub:**
```
Analyze https://github.com/user/repo
```

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface (Gradio)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Chat UI    │  │  Analytics   │  │    Logs      │      │
│  │              │  │  Dashboard   │  │   Panel      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Main Agent (Orchestrator)                 │
│              Coordinates Multi-Agent Pipeline               │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Planner     │──▶│   Worker    │──▶│  Evaluator  │
│   Agent       │   │   Agent     │   │   Agent     │
│               │   │             │   │             │
│ • Task Route  │   │ • Execute   │   │ • Validate  │
│ • Risk Detect │   │ • Analyze   │   │ • Safety    │
│ • Plan Create │   │ • Generate  │   │ • Approve   │
└──────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
        ┌───────────────────────────────────┐
        │      Tools & Visualizations        │
        │  • Code Analysis Tools (14)       │
        │  • GitHub Integration (6)         │
        │  • Visualizations (3)             │
        └───────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Session    │   │  Long-Term   │   │  Observability│
│   Memory     │   │   Memory     │   │   System      │
└──────────────┘   └──────────────┘   └──────────────┘
```

### Multi-Agent Pipeline Flow

```
User Input
    ↓
[GitHub URL Detection] → Clone Repository (if needed)
    ↓
[Session Memory] ← Add user message
    ↓
[Long-Term Memory] ← Retrieve preferences
    ↓
[PLANNER AGENT]
    ├─ Task Classification
    ├─ Destructive Operation Detection
    ├─ Tool Selection
    ├─ Complexity Assessment
    └─ Plan Generation
    ↓
[WORKER AGENT]
    ├─ Tool Execution
    ├─ Code Analysis
    ├─ Visualization Generation
    ├─ Report Creation
    └─ Response Draft
    ↓
[EVALUATOR AGENT]
    ├─ Safety Validation
    ├─ Read-Only Verification
    ├─ Destructive Command Check
    └─ Final Approval
    ↓
[UI Update]
    ├─ Chat Response
    ├─ Visualizations
    ├─ Dashboard Metrics
    └─ Logs
    ↓
User Response
```

### Data Flow

1. **Input Processing**: User message → GitHub URL extraction → Repository cloning (if needed)
2. **Context Assembly**: Session history + Long-term preferences → Planner context
3. **Planning**: Planner analyzes request → Creates execution plan
4. **Execution**: Worker executes tools → Generates analysis → Creates visualizations
5. **Validation**: Evaluator checks safety → Approves or rejects
6. **Output**: Response + Visualizations + Metrics → UI update

---

## Core Components

### 1. Main Entry Point: `app.py`

**Purpose**: Gradio-based web interface with Material Design dark mode styling.

**Key Functionalities**:
- **State Management**: Per-user session state (complexity history, metrics, analysis count)
- **Real-Time Visualization**: 
  - Matplotlib charts for complexity trends
  - Dependency graph visualizations
  - Complexity heatmaps
  - Error timeline plots
- **Dashboard Tabs**: 11 comprehensive tabs for different analysis views
- **GitHub Integration**: URL input and token management
- **Auto-Reload Support**: Development mode with file watching

**Key Functions**:
- `get_empty_state()`: Initializes new user session state
- `generate_plot()`: Creates complexity trend visualization (dark mode)
- `generate_stats_html()`: Generates code health metrics HTML
- `response_generator()`: Main message processing generator function
- `get_live_logs()`: Reads and displays system logs
- `_format_dead_code_display()`: Formats dead code analysis
- `_format_migration_display()`: Formats migration plans
- `_format_refactor_display()`: Formats refactoring suggestions
- `_format_duplicate_display()`: Formats duplicate code detection
- `_format_postmortem_display()`: Formats postmortem reports

**UI Components**:
- **Chat Interface**: Material Design chatbot with example prompts
- **11 Dashboard Tabs**:
  1. 📊 Analytics (Metrics + Complexity Trend)
  2. 🔗 Dependencies (Dependency Graph)
  3. 🔥 Hotspots (Complexity Heatmap)
  4. 🧹 Dead Code (Unused Code Report)
  5. 👯 Duplicates (Duplicate Code Detection)
  6. 🔄 Migration (Migration Plans)
  7. ♻️ Refactoring (Refactoring Suggestions)
  8. 📈 Timeline (Error Timeline)
  9. 💀 Postmortem (Incident Postmortem)
  10. 📋 Logs (System Logs)
  11. ⚙️ Settings (Configuration)
- **Repository Config**: GitHub URL and token input
- **Dark Mode**: Complete dark theme with Material Design principles

---

### 2. Main Orchestrator: `project/main_agent.py`

**Purpose**: Coordinates the multi-agent pipeline and manages conversation flow.

**Key Functionalities**:
- **Agent Initialization**: Creates Planner, Worker, Evaluator, and memory systems
- **Pipeline Orchestration**: Executes the three-stage agent workflow
- **Memory Management**: Integrates both session and long-term memory
- **GitHub Integration**: Handles repository cloning and URL extraction
- **Visualization Extraction**: Collects and formats visualization data
- **Error Handling**: Graceful fallback on pipeline failures

**Main Method**:
- `handle_message(user_input: str, repo_url: Optional[str] = None) -> Dict`: Processes user message through full pipeline

**Pipeline Flow**:
1. Extract GitHub URL from input (if present)
2. Clone repository (if needed)
3. Update session memory with user input
4. Retrieve long-term memory context
5. **Planner** analyzes input and creates plan
6. **Worker** executes plan and generates response + visualizations
7. **Evaluator** validates safety
8. Update session memory with response
9. Extract visualization data and reports
10. Return compiled results

**Return Structure**:
```python
{
    "response": str,                      # Final safe response
    "plan": Dict,                        # Planner output
    "tools_used": List[str],             # Tools invoked
    "safety_status": str,                # APPROVED/REJECTED
    "conversation_stats": Dict,          # Memory statistics
    "logs": str,                         # System logs
    "visualizations": Dict,              # Visualization images
    "dead_code_report": Dict,            # Dead code analysis
    "migration_plan_report": Dict,       # Migration plans
    "refactor_suggestions_report": List, # Refactoring suggestions
    "duplicate_code_report": Dict,       # Duplicate code detection
    "postmortem_report": Dict            # Postmortem reports
}
```

---

## Agent System

### 3.1 Planner Agent (`project/agents/planner.py`)

**Purpose**: Analyzes user requests, routes tasks, and creates execution plans.

**Key Functionalities**:
- **Task Classification**: Identifies task type (repo_analysis, incident_analysis, migration, refactoring, documentation, architecture)
- **Destructive Operation Detection**: Pre-checks for dangerous operations (file deletion, system modification, execution commands)
- **Tool Selection**: Determines which tools are needed for the task
- **Complexity Assessment**: Evaluates task complexity (LOW/MEDIUM/HIGH)
- **Risk Assessment**: Assigns risk levels based on operation type
- **Target Path Detection**: Identifies files/directories to analyze

**Key Methods**:
- `plan(user_input: str, history_str: str, memory_str: str = "") -> Dict`: Main planning function
- `_check_destructive_request(text: str) -> bool`: Detects destructive operations

**Output Structure** (PlannerOutput):
```python
{
    "emotion": str,                    # Detected emotion (legacy)
    "risk_level": "LOW|MEDIUM|HIGH",   # Risk assessment
    "distress_score": int,             # Legacy field
    "action": str,                     # Action type
    "instruction": str,                # Instructions for Worker
    "technique_suggestion": str,       # Legacy field
    "needs_validation": bool,          # Whether Evaluator should check
    "save_preference": Dict | None,    # Legacy field
    "task_type": str,                  # Task classification
    "complexity": str,                  # Complexity level
    "tools_needed": List[str],         # Required tools
    "target_paths": List[str]          # Files/directories to analyze
}
```

**Task Types**:
- `repo_analysis`: General repository analysis
- `incident_analysis`: Log file analysis
- `migration`: Framework migration planning
- `refactoring`: Code refactoring suggestions
- `documentation`: Documentation generation
- `architecture`: Architecture overview

**Safety Features**:
- Hard rule: Destructive operations → immediate boundary enforcement
- Read-only verification: Ensures all operations are safe
- Tool validation: Verifies tool selection is appropriate

---

### 3.2 Worker Agent (`project/agents/worker.py`)

**Purpose**: Executes plans and generates analysis responses with visualizations.

**Key Functionalities**:
- **Tool Execution**: Calls appropriate tools based on plan
- **Code Analysis**: Performs comprehensive code analysis
- **Visualization Generation**: Creates dependency graphs, heatmaps, timelines
- **Report Generation**: Formats analysis results
- **Response Drafting**: Creates detailed response text
- **Data Extraction**: Stores analysis results for UI display

**Key Methods**:
- `work(planner_output: Dict) -> Dict`: Executes plan and generates response

**Handler Methods**:
- `_handle_repo_analysis()`: Repository analysis handler
- `_handle_incident_analysis()`: Log analysis handler
- `_handle_migration()`: Migration planning handler
- `_handle_refactor()`: Refactoring suggestions handler
- `_handle_documentation()`: Documentation generation handler
- `_handle_architecture()`: Architecture overview handler

**Output Structure** (WorkerOutput):
```python
{
    "draft_response": str,        # Generated response text
    "tools_used": List[str],      # Tools invoked
    "_last_analysis_results": Dict # Analysis data for UI
}
```

**Analysis Results Structure**:
```python
{
    "visualizations": {
        "dependency_graph_image": PIL.Image,
        "complexity_heatmap": PIL.Image,
        "timeline_image": PIL.Image
    },
    "dead_code": Dict,
    "migration_plan": Dict,
    "refactor_suggestions": List,
    "duplicates": Dict,
    "postmortem": Dict
}
```

**Tool Integration**:
- Calls `Tools` class methods for code analysis
- Calls `Visualizations` class methods for graph generation
- Calls `GitHubTools` for repository management
- Stores results in `_last_analysis_results` for UI extraction

---

### 3.3 Evaluator Agent (`project/agents/evaluator.py`)

**Purpose**: Final safety guardrail that validates responses before delivery.

**Key Functionalities**:
- **Regex Safety Checks**: Hard rules for banned phrases (rm -rf, DELETE, DROP TABLE, etc.)
- **LLM Contextual Check**: Smart evaluation using Gemini to detect subtle violations
- **Destructive Command Detection**: Blocks file deletion, system modification, execution commands
- **Read-Only Verification**: Ensures all operations are read-only
- **Fallback Responses**: Provides safe refusal messages when violations detected

**Key Methods**:
- `evaluate(worker_output: Dict, user_input: str) -> Dict`: Validates response safety
- `_contains_destructive_commands(text: str) -> bool`: Detects destructive operations
- `_contains_execution_commands(text: str) -> bool`: Detects execution commands
- `_contains_unsafe_diffs(text: str) -> bool`: Detects unsafe code modifications

**Output Structure** (EvaluatorOutput):
```python
{
    "status": "APPROVED|REJECTED",  # Safety verdict
    "feedback": str,                 # Reason for rejection (if any)
    "final_response": str           # Approved response or sanitized refusal
}
```

**Safety Filters**:
- **Banned Operations**: File deletion, database operations, system modifications, execution commands, Kubernetes destructive operations
- **Exception Handling**: Allows safe refusals ("I cannot delete files")
- **Dual Validation**: Regex + LLM check for comprehensive coverage

---

## Tools & Utilities

### Code Intelligence Tools (`project/tools/tools.py`)

**Purpose**: Comprehensive static analysis and code intelligence capabilities.

#### 1. File Operations

**`read_file(file_path: str) -> Dict`**
- Reads file with metadata
- Returns: `{exists, content, size, lines, error}`

**`read_directory_tree(root_path: str = ".", max_depth: int = 5) -> Dict`**
- Recursively reads directory structure
- Returns: `{tree, file_count, root}`

#### 2. Code Analysis

**`extract_imports(file_path: str) -> Dict`**
- Extracts Python imports using AST
- Returns: `{imports, from_imports, errors}`

**`get_dependency_graph(root_path: str = ".", file_extensions: List[str] = None) -> Dict`**
- Builds dependency graph between files
- Returns: `{nodes, edges, node_count, edge_count}`

**`compute_complexity(file_path: str) -> Dict`**
- Calculates cyclomatic complexity
- Returns: `{complexity, functions, classes, avg_complexity, function_count, class_count}`

#### 3. Code Quality

**`detect_dead_code(root_path: str = ".") -> Dict`**
- Detects potentially unused functions and imports
- Returns: `{unused_functions, unused_imports, unused_classes, total_functions, total_imports}`

**`detect_duplicate_code(root_path: str = ".", min_lines: int = 5) -> Dict`**
- Detects duplicate code blocks across files
- Returns: `{duplicates, total_duplicates, files_analyzed, files_with_duplicates}`

#### 4. Dependency Management

**`list_outdated_libraries(requirements_file: str = "requirements.txt") -> Dict`**
- Analyzes requirements.txt for deprecated packages
- Returns: `{packages, deprecated, suggestions, total_packages}`

#### 5. Log Analysis

**`parse_logs(log_file: str, max_lines: int = 1000) -> Dict`**
- Parses log files and extracts structured information
- Returns: `{entries, errors, warnings, info, timestamps, total_lines, error_count, warning_count}`

**`cluster_errors(log_data: Dict) -> Dict`**
- Clusters similar errors from log data
- Returns: `{clusters, patterns, top_errors, total_errors, unique_patterns}`

**`detect_anomalies(log_data: Dict, time_window: int = 60) -> Dict`**
- Detects anomalies and spikes in logs
- Returns: `{anomalies, spikes, unusual_patterns, total_anomalies}`

#### 6. Documentation & Migration

**`generate_markdown_docs(repo_map: Dict, output_path: Optional[str] = None) -> Dict`**
- Generates Markdown documentation from repository structure
- Returns: `{content, sections, length}`

**`generate_migration_plan(source_framework: str, target_framework: str, file_path: Optional[str] = None) -> Dict`**
- Generates migration plan between frameworks
- Returns: `{plan, steps, breaking_changes, compatibility, estimated_effort}`

**`generate_postmortem(error_clusters: Dict, incident_summary: Optional[str] = None) -> Dict`**
- Generates structured postmortem from log analysis
- Returns: `{postmortem, sections, recommendations, error_count, warning_count}`

---

### GitHub Integration Tools (`project/tools/github_tools.py`)

**Purpose**: GitHub repository management and analysis.

#### 1. Repository Management

**`parse_github_url(url: str) -> Optional[Dict[str, str]]`**
- Parses GitHub URLs in multiple formats
- Returns: `{owner, repo, full_name, url}`

**`clone_repository(repo_url: str, github_token: Optional[str] = None, branch: Optional[str] = None) -> Dict`**
- Clones GitHub repository to cache
- Returns: `{success, local_path, error, repo_info, cached}`

**`update_repository(local_path: str, github_token: Optional[str] = None) -> Dict`**
- Updates cloned repository (git pull)
- Returns: `{success, error}`

**`cleanup_repository(local_path: str) -> Dict`**
- Removes cloned repository from cache
- Returns: `{success, error}`

#### 2. Repository Information

**`get_repository_info(repo_url: str, github_token: Optional[str] = None) -> Dict`**
- Gets repository metadata via GitHub API
- Returns: `{success, name, full_name, description, language, stars, forks, is_private, default_branch, created_at, updated_at, error}`

**`list_cached_repositories() -> Dict`**
- Lists all cached repositories
- Returns: `{repositories, count}`

---

## Visualization System

### Visualization Tools (`project/tools/visualizations.py`)

**Purpose**: Generate visual representations of code analysis data.

#### 1. Dependency Graph Visualization

**`plot_dependency_graph(dependency_data: Dict, max_nodes: int = 50) -> Image.Image`**
- Creates visual dependency graph using networkx
- Uses hierarchical layout for clarity
- Color-codes nodes by module type
- Returns: PIL Image

**Features**:
- Node size based on dependency count
- Edge thickness based on relationship strength
- Module grouping for large codebases
- Interactive-style layout

#### 2. Complexity Heatmap

**`plot_complexity_heatmap(complexity_data: List[Dict], max_files: int = 20) -> Image.Image`**
- Creates heatmap showing complexity across files
- Uses seaborn for statistical visualization
- Color gradient from green (low) to red (high)
- Returns: PIL Image

**Features**:
- File-level complexity aggregation
- Function-level detail view
- Color-coded severity levels
- Sorted by complexity for easy identification

#### 3. Error Timeline

**`plot_error_timeline(log_data: Dict, time_window_hours: int = 24) -> Image.Image`**
- Creates timeline plot of errors and warnings
- Uses matplotlib for time-series visualization
- Separate lines for errors and warnings
- Returns: PIL Image

**Features**:
- Time-series plotting
- Error/warning separation
- Spike detection visualization
- Trend analysis

---

## Memory Systems

### Session Memory (`project/memory/session_memory.py`)

**Purpose**: Short-term conversation history (last 8 turns).

**Key Functionalities**:
- **Message Storage**: Stores user and assistant messages with timestamps
- **History Limiting**: Maintains last N exchanges (default: 8 turns)
- **Context Formatting**: Formats history for LLM context injection
- **Statistics**: Tracks message counts and conversation stats

**Key Methods**:
- `add_message(role: str, content: str)`: Add message to history
- `get_history_string(last_n: int = 5) -> str`: Get formatted history for LLM
- `get_conversation_summary() -> str`: Brief summary
- `get_stats() -> Dict`: Conversation statistics
- `clear()`: Reset history

**Storage**: In-memory list (cleared on session end)

---

### Long-Term Memory (`project/memory/long_term_memory.py`)

**Purpose**: Persistent user preferences and analysis history.

**Key Functionalities**:
- **Preference Storage**: Saves user preferences (e.g., preferred frameworks, analysis depth)
- **Analysis History**: Stores summaries of analyzed repositories
- **Migration Preferences**: Remembers framework migration preferences
- **JSON Persistence**: Stores data in `devops_preferences.json`

**Key Methods**:
- `update_preference(key: str, value: str)`: Save a preference
- `add_analyzed_repo(repo_path: str, analysis_summary: Dict)`: Store repo analysis
- `get_migration_preference(source_framework: str) -> str`: Get migration preference
- `set_migration_preference(source_framework: str, target_framework: str)`: Set migration preference
- `get_preferences_string() -> str`: Format for LLM context
- `clear()`: Wipe all memory

**Storage Structure**:
```json
{
    "preferences": {
        "preferred_framework": "FastAPI",
        "analysis_depth": "detailed"
    },
    "migration_preferences": {
        "Flask": "FastAPI",
        "Django": "FastAPI"
    },
    "analyzed_repos": [
        {
            "path": "repo_path",
            "summary": {...},
            "timestamp": "..."
        }
    ]
}
```

---

## Safety & Security

### Triple-Layer Safety System

#### Layer 1: Planner Safety (Pre-check)
- **Destructive Operation Detection**: Hard-coded pattern matching for dangerous operations
- **Read-Only Verification**: Ensures all operations are read-only
- **Route Unsafe Requests**: Routes unsafe requests to boundary enforcement

#### Layer 2: Worker Safety (Read-Only)
- **Strict Read-Only Operations**: No file writing, deletion, or modification
- **Text-Based Suggestions Only**: All code changes are suggestions, not executions
- **No Shell Command Execution**: No subprocess, os.system, or eval calls

#### Layer 3: Evaluator Safety (Final Guardrail)
- **Regex-Based Banned Phrase Detection**: Hard rules for dangerous commands
- **LLM-Based Contextual Safety Check**: Smart detection of subtle violations
- **Sanitized Fallback Responses**: Safe refusal messages when violations detected

### Banned Operations

The system automatically blocks:
- **File Operations**: `rm -rf`, `delete`, `unlink`, file deletion commands
- **Database Operations**: `DROP TABLE`, `TRUNCATE`, `DELETE FROM`
- **System Modifications**: `sudo`, `systemctl`, `chmod 777`, permission changes
- **Execution Commands**: `subprocess`, `os.system`, `eval`, `exec`
- **Kubernetes Operations**: `kubectl delete`, destructive k8s commands

### Allowed Operations

- ✅ Read-only file access
- ✅ Code analysis and static analysis
- ✅ Documentation generation (Markdown)
- ✅ Text-based code suggestions (diffs)
- ✅ Log parsing and analysis
- ✅ Dependency graph generation
- ✅ Complexity calculations
- ✅ Visualization generation

---

## User Interface

### Design Philosophy

- **Material Design**: Google's Material Design principles
- **Vercel Aesthetics**: Clean, modern, professional look
- **Dark Mode**: Complete dark theme for reduced eye strain
- **Responsive**: Mobile-friendly layout
- **Accessible**: High contrast, readable fonts

### UI Components

#### 1. Header
- Project title and description
- Navigation buttons (Docs, GitHub)
- Status indicators

#### 2. Chat Interface
- Material Design chatbot
- Example prompts for quick start
- Real-time response streaming
- Message history

#### 3. Repository Configuration
- GitHub URL input
- Token input (for private repos)
- Repository status display

#### 4. Dashboard Tabs (11 Tabs)

**📊 Analytics**
- Code Health Metrics (4 cards)
- Complexity Trend Chart

**🔗 Dependencies**
- Dependency Graph Visualization
- Module relationship display

**🔥 Hotspots**
- Complexity Heatmap
- High-complexity module identification

**🧹 Dead Code**
- Unused functions list
- Unused imports list
- Summary statistics

**👯 Duplicates**
- Duplicate code blocks
- Similarity scores
- File pairs

**🔄 Migration**
- Migration plans
- Breaking changes
- Step-by-step guides

**♻️ Refactoring**
- Refactoring suggestions
- File-by-file recommendations
- Complexity improvements

**📈 Timeline**
- Error timeline visualization
- Warning timeline
- Temporal analysis

**💀 Postmortem**
- Incident postmortem reports
- Root cause analysis
- Recommendations

**📋 Logs**
- System logs display
- Agent monologue
- Real-time updates

**⚙️ Settings**
- Configuration options
- GitHub integration settings

### Color Scheme (Dark Mode)

- **Background**: `#0a0a0a` (Very dark)
- **Surface**: `#1a1a1a` (Dark grey)
- **Surface Variant**: `#2a2a2a` (Lighter dark grey)
- **Text Primary**: `#e5e5e5` (Light grey)
- **Text Secondary**: `#a0a0a0` (Medium grey)
- **Primary**: `#3291ff` (Blue)
- **Border**: `#333333` (Dark grey)

---

## GitHub Integration

### Features

- **Public Repository Analysis**: Analyze any public GitHub repository
- **Private Repository Support**: Analyze private repos with GitHub token
- **Automatic Cloning**: Clones repositories to local cache
- **Repository Caching**: Caches cloned repos for faster subsequent analysis
- **Branch Selection**: Supports specific branch analysis
- **Repository Metadata**: Fetches repository information via GitHub API

### Workflow

1. User provides GitHub URL (full URL or owner/repo format)
2. System extracts and normalizes URL
3. Checks if repository is already cached
4. Clones repository (if needed) with optional token
5. Analyzes cloned repository
6. Caches repository for future use

### URL Formats Supported

- Full URL: `https://github.com/owner/repo`
- Short form: `owner/repo`
- With branch: `owner/repo@branch`
- With path: `owner/repo/path/to/file`

---

## Deployment

### Hugging Face Spaces

**Configuration**:
- SDK: Gradio
- Python Version: 3.10+
- Auto-detects `SPACE_ID` environment variable
- Runs on port 7860

**Environment Variables**:
- `GEMINI_API_KEYS`: Comma-separated API keys
- `MODEL_NAME`: `gemini-2.0-flash-exp`
- `TEMPERATURE`: `0.1`
- `MAX_OUTPUT_TOKENS`: `2048`
- `GITHUB_TOKEN`: Optional, for private repos

**Deployment Steps**:
1. Create Space on Hugging Face
2. Push code via Git
3. Set environment variables
4. Wait for build (2-5 minutes)
5. App is live!

### Local Development

**Standard Mode**:
```bash
python app.py
```

**Development Mode (Auto-Reload)**:
```bash
python dev.py
```

**Server**: `127.0.0.1:7860`

---

## Testing

### Test Suite Overview

- **72 Test Cases**: Comprehensive coverage
- **100% Component Coverage**: All major components tested
- **Integration Tests**: End-to-end pipeline testing
- **Mock Mode**: Testing without API keys

