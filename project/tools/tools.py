"""
DevOps Code Intelligence Tools for the Worker agent.
All tools return JSON-serializable data - NO shell command execution.
"""
import os
import re
import json
import ast
import warnings
from typing import Dict, List, Optional
from collections import defaultdict, Counter

# Suppress SyntaxWarnings from analyzed code (e.g., invalid escape sequences in test files)
warnings.filterwarnings('ignore', category=SyntaxWarning, module='ast')


class Tools:
    """DevOps and code intelligence tools for repository analysis."""
    
    @staticmethod
    def read_file(file_path: str) -> Dict:
        """Read a file and return its contents with metadata.
        
        Args:
            file_path: Path to the file (relative to repo root)
            
        Returns:
            Dict with 'content', 'exists', 'size', 'lines', 'error'
        """
        try:
            if not os.path.exists(file_path):
                return {
                    "exists": False,
                    "content": "",
                    "size": 0,
                    "lines": 0,
                    "error": f"File not found: {file_path}"
                }
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return {
                "exists": True,
                "content": content,
                "size": len(content),
                "lines": len(content.splitlines()),
                "error": None
            }
        except Exception as e:
            return {
                "exists": False,
                "content": "",
                "size": 0,
                "lines": 0,
                "error": str(e)
            }
    
    @staticmethod
    def read_directory_tree(root_path: str = ".", max_depth: int = 5) -> Dict:
        """Read directory tree structure.
        
        Args:
            root_path: Root directory path
            max_depth: Maximum depth to traverse
            
        Returns:
            Dict with 'tree' (nested structure) and 'file_count'
        """
        ignore_dirs = {'.git', '__pycache__', 'venv', 'node_modules', '.venv', 
                      'env', 'dist', 'build', '.pytest_cache', '.mypy_cache'}
        ignore_extensions = {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe'}
        
        def _traverse(path: str, depth: int) -> Dict:
            if depth > max_depth:
                return {}
            
            result = {}
            try:
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    
                    if os.path.isdir(item_path):
                        if item not in ignore_dirs:
                            result[item] = _traverse(item_path, depth + 1)
                    else:
                        if not any(item.endswith(ext) for ext in ignore_extensions):
                            result[item] = {"type": "file", "path": item_path}
            except PermissionError:
                pass
            
            return result
        
        tree = _traverse(root_path, 0)
        file_count = Tools._count_files(tree)
        
        return {
            "tree": tree,
            "file_count": file_count,
            "root": root_path
        }
    
    @staticmethod
    def _count_files(tree: Dict) -> int:
        """Count files in tree structure."""
        count = 0
        for key, value in tree.items():
            if isinstance(value, dict):
                if value.get("type") == "file":
                    count += 1
                else:
                    count += Tools._count_files(value)
        return count
    
    @staticmethod
    def extract_imports(file_path: str) -> Dict:
        """Extract imports from a Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Dict with 'imports', 'from_imports', 'errors'
        """
        result = {
            "imports": [],
            "from_imports": [],
            "errors": []
        }
        
        file_data = Tools.read_file(file_path)
        if not file_data["exists"]:
            result["errors"].append(f"File not found: {file_path}")
            return result
        
        content = file_data["content"]
        
        try:
            # Suppress SyntaxWarnings during parsing (from analyzed code, not our code)
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=SyntaxWarning)
                tree = ast.parse(content, filename=file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        result["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        result["from_imports"].append({
                            "module": module,
                            "name": alias.name,
                            "asname": alias.asname
                        })
        except SyntaxError as e:
            result["errors"].append(f"Syntax error: {str(e)}")
        except Exception as e:
            result["errors"].append(f"Parse error: {str(e)}")
        
        return result
    
    @staticmethod
    def get_dependency_graph(root_path: str = ".", file_extensions: List[str] = None) -> Dict:
        """Build dependency graph for Python files.
        
        Args:
            root_path: Root directory to analyze
            file_extensions: List of extensions to analyze (default: ['.py'])
            
        Returns:
            Dict with 'nodes' (files) and 'edges' (dependencies)
        """
        if file_extensions is None:
            file_extensions = ['.py']
        
        nodes = []
        edges = []
        file_map = {}
        
        # Find all Python files
        for root, dirs, files in os.walk(root_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'venv', 'node_modules'}]
            
            for file in files:
                if any(file.endswith(ext) for ext in file_extensions):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, root_path)
                    nodes.append(rel_path)
                    file_map[rel_path] = file_path
        
        # Extract dependencies
        for rel_path, full_path in file_map.items():
            imports = Tools.extract_imports(full_path)
            
            # Resolve imports to files
            for imp in imports["imports"] + [i["module"] for i in imports["from_imports"]]:
                if imp:
                    # Try to find matching file
                    for node in nodes:
                        imp_slash = imp.replace('.', '/')
                        imp_backslash = imp.replace('.', '\\')
                        if node.replace('/', '.').replace('\\', '.').replace('.py', '') == imp or \
                           node.endswith(f"/{imp_slash}.py") or \
                           node.endswith(f"\\{imp_backslash}.py"):
                            edges.append({
                                "from": rel_path,
                                "to": node,
                                "type": "import"
                            })
                            break
        
        return {
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges)
        }
    
    @staticmethod
    def compute_complexity(file_path: str) -> Dict:
        """Calculate cyclomatic complexity for a Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Dict with 'complexity', 'functions', 'classes', 'avg_complexity'
        """
        file_data = Tools.read_file(file_path)
        if not file_data["exists"]:
            return {
                "complexity": 0,
                "functions": [],
                "classes": [],
                "avg_complexity": 0,
                "error": "File not found"
            }
        
        content = file_data["content"]
        
        try:
            # Suppress SyntaxWarnings during parsing (from analyzed code, not our code)
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=SyntaxWarning)
                tree = ast.parse(content, filename=file_path)
            functions = []
            classes = []
            
            def _count_complexity(node) -> int:
                """Count decision points (if, for, while, except, etc.)."""
                complexity = 1  # Base complexity
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler,
                                         ast.With, ast.And, ast.Or, ast.Assert)):
                        complexity += 1
                return complexity
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_complexity = _count_complexity(node)
                    functions.append({
                        "name": node.name,
                        "complexity": func_complexity,
                        "lines": node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                    })
                elif isinstance(node, ast.ClassDef):
                    class_complexity = _count_complexity(node)
                    classes.append({
                        "name": node.name,
                        "complexity": class_complexity,
                        "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                    })
            
            total_complexity = sum(f["complexity"] for f in functions)
            avg_complexity = total_complexity / len(functions) if functions else 0
            
            return {
                "complexity": total_complexity,
                "functions": functions,
                "classes": classes,
                "avg_complexity": round(avg_complexity, 2),
                "function_count": len(functions),
                "class_count": len(classes)
            }
        except Exception as e:
            return {
                "complexity": 0,
                "functions": [],
                "classes": [],
                "avg_complexity": 0,
                "error": str(e)
            }
    
    @staticmethod
    def detect_dead_code(root_path: str = ".") -> Dict:
        """Detect potentially unused functions and imports.
        
        Args:
            root_path: Root directory to analyze
            
        Returns:
            Dict with 'unused_functions', 'unused_imports', 'unused_classes'
        """
        # This is a simplified version - full analysis would require execution tracing
        dependency_graph = Tools.get_dependency_graph(root_path)
        all_functions = []
        all_imports = []
        
        for node in dependency_graph["nodes"]:
            full_path = os.path.join(root_path, node)
            if os.path.exists(full_path):
                imports = Tools.extract_imports(full_path)
                complexity = Tools.compute_complexity(full_path)
                
                all_imports.extend(imports["imports"])
                all_functions.extend([f["name"] for f in complexity["functions"]])
        
        # Count usage
        import_usage = Counter(all_imports)
        function_usage = Counter(all_functions)
        
        unused_imports = [imp for imp, count in import_usage.items() if count == 1]
        unused_functions = [func for func, count in function_usage.items() if count == 1]
        
        return {
            "unused_functions": unused_functions[:20],  # Limit results
            "unused_imports": unused_imports[:20],
            "unused_classes": [],  # Would need more analysis
            "total_functions": len(all_functions),
            "total_imports": len(all_imports)
        }
    
    @staticmethod
    def list_outdated_libraries(requirements_file: str = "requirements.txt") -> Dict:
        """Analyze requirements.txt for outdated or deprecated packages.
        
        Args:
            requirements_file: Path to requirements.txt
            
        Returns:
            Dict with 'packages', 'deprecated', 'suggestions'
        """
        file_data = Tools.read_file(requirements_file)
        if not file_data["exists"]:
            return {
                "packages": [],
                "deprecated": [],
                "suggestions": [],
                "error": "Requirements file not found"
            }
        
        packages = []
        deprecated = []
        suggestions = []
        
        # Known deprecated packages mapping
        deprecated_map = {
            "flask": "Consider FastAPI for async support",
            "django": "Check Django version compatibility",
            "requests": "Consider httpx for async",
            "urllib2": "Use urllib3 or requests (Python 2 -> 3)"
        }
        
        for line in file_data["content"].splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                # Parse package name (handle ==, >=, <=, etc.)
                match = re.match(r'^([a-zA-Z0-9_-]+)', line)
                if match:
                    pkg_name = match.group(1).lower()
                    packages.append({
                        "name": pkg_name,
                        "spec": line
                    })
                    
                    if pkg_name in deprecated_map:
                        deprecated.append({
                            "package": pkg_name,
                            "reason": deprecated_map[pkg_name]
                        })
                        suggestions.append({
                            "package": pkg_name,
                            "suggestion": deprecated_map[pkg_name]
                        })
        
        return {
            "packages": packages,
            "deprecated": deprecated,
            "suggestions": suggestions,
            "total_packages": len(packages)
        }
    
    @staticmethod
    def parse_logs(log_file: str, max_lines: int = 1000) -> Dict:
        """Parse log file and extract structured information.
        
        Args:
            log_file: Path to log file
            max_lines: Maximum lines to read
            
        Returns:
            Dict with 'entries', 'errors', 'warnings', 'info', 'timestamps'
        """
        file_data = Tools.read_file(log_file)
        if not file_data["exists"]:
            return {
                "entries": [],
                "errors": [],
                "warnings": [],
                "info": [],
                "timestamps": [],
                "error": "Log file not found"
            }
        
        lines = file_data["content"].splitlines()[:max_lines]
        entries = []
        errors = []
        warnings = []
        info = []
        timestamps = []
        
        # Common log patterns
        error_pattern = re.compile(r'(ERROR|CRITICAL|FATAL|Exception|Traceback)', re.IGNORECASE)
        warning_pattern = re.compile(r'(WARNING|WARN)', re.IGNORECASE)
        timestamp_pattern = re.compile(r'(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2})|(\d{2}/\d{2}/\d{4}[\s]\d{2}:\d{2}:\d{2})')
        
        for i, line in enumerate(lines, 1):
            entry = {
                "line_number": i,
                "content": line,
                "level": "INFO"
            }
            
            if error_pattern.search(line):
                entry["level"] = "ERROR"
                errors.append(entry)
            elif warning_pattern.search(line):
                entry["level"] = "WARNING"
                warnings.append(entry)
            else:
                info.append(entry)
            
            # Extract timestamp
            ts_match = timestamp_pattern.search(line)
            if ts_match:
                entry["timestamp"] = ts_match.group(0)
                timestamps.append(entry["timestamp"])
            
            entries.append(entry)
        
        return {
            "entries": entries,
            "errors": errors,
            "warnings": warnings,
            "info": info,
            "timestamps": timestamps,
            "total_lines": len(entries),
            "error_count": len(errors),
            "warning_count": len(warnings)
        }
    
    @staticmethod
    def cluster_errors(log_data: Dict) -> Dict:
        """Cluster similar errors from log data.
        
        Args:
            log_data: Output from parse_logs()
            
        Returns:
            Dict with 'clusters', 'patterns', 'top_errors'
        """
        errors = log_data.get("errors", [])
        
        # Extract error patterns
        error_patterns = defaultdict(list)
        error_messages = []
        
        for error in errors:
            content = error.get("content", "")
            # Extract error type (e.g., "ValueError", "KeyError")
            pattern_match = re.search(r'(\w+Error|\w+Exception)', content)
            if pattern_match:
                error_type = pattern_match.group(1)
                error_patterns[error_type].append(error)
            else:
                # Use first 50 chars as pattern
                pattern = content[:50].strip()
                error_patterns[pattern].append(error)
            
            error_messages.append(content)
        
        # Find top errors
        error_counter = Counter([e.get("content", "")[:100] for e in errors])
        top_errors = [{"message": msg, "count": count} 
                      for msg, count in error_counter.most_common(10)]
        
        return {
            "clusters": {k: len(v) for k, v in error_patterns.items()},
            "patterns": dict(error_patterns),
            "top_errors": top_errors,
            "total_errors": len(errors),
            "unique_patterns": len(error_patterns)
        }
    
    @staticmethod
    def detect_anomalies(log_data: Dict, time_window: int = 60) -> Dict:
        """Detect anomalies in log patterns (spike detection, unusual patterns).
        
        Args:
            log_data: Output from parse_logs()
            time_window: Time window in seconds for anomaly detection
            
        Returns:
            Dict with 'anomalies', 'spikes', 'unusual_patterns'
        """
        errors = log_data.get("errors", [])
        warnings = log_data.get("warnings", [])
        
        # Simple spike detection: count errors per time window
        error_times = [e.get("timestamp", "") for e in errors if e.get("timestamp")]
        
        # Group by approximate time windows
        time_groups = defaultdict(int)
        for ts in error_times:
            # Simplified: use first 16 chars (YYYY-MM-DD HH:MM)
            time_key = ts[:16] if len(ts) >= 16 else ts
            time_groups[time_key] += 1
        
        # Find spikes (more than 2x average)
        if time_groups:
            avg_errors = sum(time_groups.values()) / len(time_groups)
            spikes = {k: v for k, v in time_groups.items() if v > avg_errors * 2}
        else:
            spikes = {}
        
        anomalies = []
        if spikes:
            anomalies.append({
                "type": "error_spike",
                "description": f"Detected {len(spikes)} error spikes",
                "details": spikes
            })
        
        return {
            "anomalies": anomalies,
            "spikes": spikes,
            "unusual_patterns": [],
            "total_anomalies": len(anomalies)
        }
    
    @staticmethod
    def generate_markdown_docs(repo_map: Dict, output_path: Optional[str] = None) -> Dict:
        """Generate Markdown documentation from repository structure.
        
        Args:
            repo_map: Repository structure (from read_directory_tree or dependency_graph)
            output_path: Optional path to save docs (not used, returns content only)
            
        Returns:
            Dict with 'content' (markdown string) and 'sections'
        """
        sections = []
        content = "# Repository Documentation\n\n"
        
        if "tree" in repo_map:
            content += "## Directory Structure\n\n```\n"
            content += Tools._format_tree_markdown(repo_map["tree"], 0)
            content += "```\n\n"
            sections.append("Directory Structure")
        
        if "nodes" in repo_map:
            content += "## Files\n\n"
            for node in repo_map["nodes"][:50]:  # Limit to 50 files
                content += f"- `{node}`\n"
            content += "\n"
            sections.append("Files")
        
        return {
            "content": content,
            "sections": sections,
            "length": len(content)
        }
    
    @staticmethod
    def _format_tree_markdown(tree: Dict, indent: int) -> str:
        """Format tree structure as markdown."""
        result = ""
        prefix = "  " * indent + "├── "
        
        for key, value in list(tree.items())[:20]:  # Limit depth
            if isinstance(value, dict):
                if value.get("type") == "file":
                    result += prefix + key + "\n"
                else:
                    result += prefix + key + "/\n"
                    result += Tools._format_tree_markdown(value, indent + 1)
        
        return result
    
    @staticmethod
    def generate_migration_plan(source_framework: str, target_framework: str, 
                               file_path: Optional[str] = None) -> Dict:
        """Generate migration plan between frameworks/languages.
        
        Args:
            source_framework: Source framework (e.g., "flask", "django")
            target_framework: Target framework (e.g., "fastapi", "express")
            file_path: Optional file to analyze
            
        Returns:
            Dict with 'plan', 'steps', 'breaking_changes', 'compatibility'
        """
        # Known migration patterns
        migration_patterns = {
            ("flask", "fastapi"): {
                "steps": [
                    "1. Replace Flask routes with FastAPI path decorators",
                    "2. Convert request.json to Pydantic models",
                    "3. Update dependency injection patterns",
                    "4. Migrate Flask-CORS to FastAPI CORS middleware",
                    "5. Update async/await patterns"
                ],
                "breaking_changes": [
                    "Synchronous routes need async conversion",
                    "Request object access changes",
                    "Middleware syntax differs"
                ],
                "compatibility": "High - similar patterns"
            },
            ("django", "fastapi"): {
                "steps": [
                    "1. Extract business logic from Django views",
                    "2. Create Pydantic models for serialization",
                    "3. Replace Django ORM with SQLAlchemy or similar",
                    "4. Migrate authentication to JWT/OAuth2",
                    "5. Convert Django templates to API responses"
                ],
                "breaking_changes": [
                    "ORM changes required",
                    "Template system removed",
                    "Admin panel needs separate solution"
                ],
                "compatibility": "Medium - significant refactoring"
            }
        }
        
        key = (source_framework.lower(), target_framework.lower())
        if key in migration_patterns:
            plan = migration_patterns[key]
        else:
            plan = {
                "steps": [
                    f"1. Analyze {source_framework} codebase",
                    f"2. Identify {target_framework} equivalents",
                    f"3. Create migration strategy",
                    "4. Test incrementally",
                    "5. Deploy gradually"
                ],
                "breaking_changes": ["Framework-specific changes required"],
                "compatibility": "Unknown - manual analysis needed"
            }
        
        return {
            "plan": f"Migration from {source_framework} to {target_framework}",
            "steps": plan["steps"],
            "breaking_changes": plan["breaking_changes"],
            "compatibility": plan["compatibility"],
            "estimated_effort": "Medium to High"
        }
    
    @staticmethod
    def detect_duplicate_code(root_path: str = ".", min_lines: int = 5) -> Dict:
        """Detect duplicate code blocks across files.
        
        Args:
            root_path: Root directory to analyze
            min_lines: Minimum number of lines to consider as duplicate
            
        Returns:
            Dict with 'duplicates', 'similarity_scores', 'total_duplicates'
        """
        duplicates = []
        file_contents = {}
        
        # Read all Python files
        for root, dirs, files in os.walk(root_path):
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'venv', 'node_modules'}]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.splitlines()
                            # Normalize: remove comments and blank lines for comparison
                            normalized = [line.strip() for line in lines 
                                        if line.strip() and not line.strip().startswith('#')]
                            file_contents[file_path] = normalized
                    except Exception:
                        continue
        
        # Compare files for duplicates
        file_list = list(file_contents.items())
        for i, (file1, content1) in enumerate(file_list):
            for j, (file2, content2) in enumerate(file_list[i+1:], i+1):
                # Find longest common subsequence
                common_lines = Tools._find_common_blocks(content1, content2, min_lines)
                if common_lines:
                    duplicates.append({
                        "file1": os.path.relpath(file1, root_path),
                        "file2": os.path.relpath(file2, root_path),
                        "common_blocks": common_lines,
                        "similarity": len(common_lines) / max(len(content1), len(content2), 1)
                    })
        
        return {
            "duplicates": duplicates[:20],  # Limit results
            "total_duplicates": len(duplicates),
            "files_analyzed": len(file_contents)
        }
    
    @staticmethod
    def _find_common_blocks(content1: List[str], content2: List[str], min_lines: int) -> List[Dict]:
        """Find common code blocks between two file contents."""
        common_blocks = []
        
        # Simple sliding window approach
        for i in range(len(content1) - min_lines + 1):
            block1 = content1[i:i+min_lines]
            
            for j in range(len(content2) - min_lines + 1):
                block2 = content2[j:j+min_lines]
                
                if block1 == block2:
                    # Extend block if possible
                    k = min_lines
                    while (i + k < len(content1) and j + k < len(content2) and 
                           content1[i + k] == content2[j + k]):
                        k += 1
                    
                    common_blocks.append({
                        "lines": k,
                        "content_preview": "\n".join(block1[:3])  # First 3 lines
                    })
                    break  # Found match, move on
        
        return common_blocks
    
    @staticmethod
    def generate_postmortem(log_data: Dict, incident_summary: Optional[str] = None) -> Dict:
        """Generate structured postmortem from log analysis.
        
        Args:
            log_data: Output from parse_logs() or cluster_errors()
            incident_summary: Optional human-readable incident summary
            
        Returns:
            Dict with 'postmortem' (markdown), 'sections', 'recommendations'
        """
        errors = log_data.get("errors", [])
        warnings = log_data.get("warnings", [])
        clusters = log_data.get("clusters", {}) if "clusters" in log_data else {}
        
        # Extract key information
        error_count = len(errors)
        warning_count = len(warnings)
        top_errors = clusters.get("top_errors", []) if clusters else []
        unique_patterns = clusters.get("unique_patterns", 0) if clusters else 0
        
        # Build postmortem sections
        sections = []
        
        # 1. Executive Summary
        sections.append("## Executive Summary")
        sections.append(f"- **Incident Duration**: Detected in log analysis")
        sections.append(f"- **Total Errors**: {error_count}")
        sections.append(f"- **Total Warnings**: {warning_count}")
        sections.append(f"- **Unique Error Patterns**: {unique_patterns}")
        if incident_summary:
            sections.append(f"- **Summary**: {incident_summary}")
        sections.append("")
        
        # 2. Timeline
        sections.append("## Timeline")
        if errors:
            timestamps = [e.get("timestamp", "Unknown") for e in errors[:10] if e.get("timestamp")]
            if timestamps:
                sections.append("Key events:")
                for ts in timestamps[:5]:
                    sections.append(f"- {ts}")
            else:
                sections.append("Timestamps not available in log format")
        sections.append("")
        
        # 3. Root Cause Analysis
        sections.append("## Root Cause Analysis")
        if top_errors:
            sections.append("Most frequent errors:")
            for err in top_errors[:5]:
                sections.append(f"- **{err.get('count', 0)} occurrences**: {err.get('message', '')[:100]}")
        else:
            sections.append("Error patterns identified through log clustering.")
        sections.append("")
        
        # 4. Impact Assessment
        sections.append("## Impact Assessment")
        sections.append(f"- **Affected Systems**: Log analysis indicates {error_count} error events")
        sections.append(f"- **Severity**: {'High' if error_count > 50 else 'Medium' if error_count > 10 else 'Low'}")
        sections.append("")
        
        # 5. Remediation Steps
        sections.append("## Remediation Steps")
        recommendations = []
        if error_count > 0:
            recommendations.append("1. Review and fix root cause errors identified in log analysis")
            recommendations.append("2. Implement error handling for common failure patterns")
            recommendations.append("3. Add monitoring and alerting for critical error patterns")
            recommendations.append("4. Review system configuration and dependencies")
        
        sections.extend(recommendations)
        sections.append("")
        
        # 6. Prevention
        sections.append("## Prevention")
        sections.append("- Implement comprehensive error logging with context")
        sections.append("- Set up automated alerting for error spikes")
        sections.append("- Regular log analysis and pattern review")
        sections.append("- Improve error handling and graceful degradation")
        sections.append("")
        
        postmortem_md = "\n".join(sections)
        
        return {
            "postmortem": postmortem_md,
            "sections": ["Executive Summary", "Timeline", "Root Cause Analysis", 
                        "Impact Assessment", "Remediation Steps", "Prevention"],
            "recommendations": recommendations,
            "error_count": error_count,
            "warning_count": warning_count
        }