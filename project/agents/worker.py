"""
Worker Agent: Executes DevOps plans and generates analysis responses.
"""
import os
import io
from typing import Dict, Optional
from project.core.context_engineering import WORKER_PROMPT
from project.core.a2a_protocol import WorkerOutput
from project.tools.tools import Tools
from project.tools.github_tools import GitHubTools
from project.tools.visualizations import Visualizations
from project.config import Config
from project.core.observability import logger
from project.core.gemini_client import GeminiClient
from PIL import Image as PILImage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class Worker:
    def __init__(self):
        self.client = GeminiClient(WORKER_PROMPT)
        self.mock_mode = False
        
    def work(self, planner_output: Dict) -> Dict:
        instruction = planner_output.get("instruction", "")
        action = planner_output.get("action", "")
        target_paths = planner_output.get("target_paths", [])
        tools_needed = planner_output.get("tools_needed", [])
        repo_path = planner_output.get("repo_path", ".")  # Default to current directory
        
        logger.log("Worker", "Executing DevOps plan", 
                  data={"action": action, "tools": tools_needed, "repo_path": repo_path})
        
        # Mock mode
        if hasattr(self, 'mock_mode') and self.mock_mode:
            return self._mock_work(planner_output)
        
        # Gather context data based on action
        context_data = ""
        tools_used = []
        analysis_results = {}
        
        try:
            if action == "repo_analysis":
                context_data, tools_used, analysis_results = self._handle_repo_analysis(target_paths, repo_path, instruction)
                
            elif action == "incident_analysis":
                context_data, tools_used, analysis_results = self._handle_incident_analysis(target_paths, repo_path)
                
            elif action == "migration":
                context_data, tools_used, analysis_results = self._handle_migration(planner_output, repo_path)
                
            elif action == "refactor":
                context_data, tools_used, analysis_results = self._handle_refactor(target_paths, repo_path)
                
            elif action == "documentation":
                context_data, tools_used, analysis_results = self._handle_documentation(target_paths, repo_path)
                
            elif action == "architecture":
                context_data, tools_used, analysis_results = self._handle_architecture(target_paths, repo_path)
                
            elif action == "enforce_boundary":
                context_data = "User requested destructive operation. Provide safe refusal message."
                tools_used = []
                
            else:  # general_chat
                context_data = "Respond to the user's DevOps question."
                tools_used = []
        
        except Exception as e:
            logger.log("Worker", f"Error executing plan: {e}", level="ERROR")
            context_data = f"Error during analysis: {str(e)}"
            tools_used = []
        
        # Build prompt for LLM
        prompt = f"""
        USER REQUEST: {instruction}
        
        ANALYSIS CONTEXT (ALL ANALYSIS HAS BEEN COMPLETED):
        {context_data}
        
        IMPORTANT INSTRUCTIONS:
        - The analysis has ALREADY BEEN PERFORMED by automated tools
        - Report on the ACTUAL results provided in the context above
        - Do NOT say you cannot execute code or use tools - the work is already done!
        - If complexity heatmap was generated, mention it in your response
        - If dependency graph was generated, mention it in your response
        - Provide insights based on the ACTUAL data, not hypothetical examples
        
        Generate a comprehensive DevOps response reporting on the completed analysis results.
        """
        
        # Generate response
        draft = self.client.generate_response(prompt)
        
        if not draft:
            # Fallback response
            draft = "I apologize, but I'm having trouble generating a response. Please try again with a more specific request."
        
        # Append analysis results if available
        if analysis_results:
            draft += "\n\n## Analysis Results\n\n"
            draft += self._format_analysis_results(analysis_results)
        
        # Store analysis results for main agent to access
        # Ensure visualizations are properly structured
        if "visualizations" not in analysis_results:
            analysis_results["visualizations"] = {}
        
        # Extract visualization images from analysis_results and add to visualizations dict
        # These are stored directly in analysis_results (which is the 'results' dict from _handle_* methods)
        for key in ["dependency_graph_image", "complexity_heatmap"]:
            if key in analysis_results:
                analysis_results["visualizations"][key] = analysis_results.pop(key)
        
        # Extract timeline visualizations (check multiple possible locations)
        # Timeline might be in results["visualizations"]["error_timeline"] or results["{log_file}_timeline"]
        if "visualizations" in analysis_results:
            if "error_timeline" in analysis_results["visualizations"]:
                # Already in visualizations, keep it
                logger.log("Worker", f"Timeline already in visualizations dict: {type(analysis_results['visualizations']['error_timeline'])}", level="INFO")
            else:
                # Check for timeline keys in results (top level) - these are like "autopilot_devops.log_timeline"
                for key, value in list(analysis_results.items()):
                    if "_timeline" in key and hasattr(value, 'save'):  # PIL Image
                        analysis_results["visualizations"]["error_timeline"] = value
                        del analysis_results[key]
                        logger.log("Worker", f"Moved timeline from {key} to visualizations", level="INFO")
                        break
                # Also check nested structures (log file results) - these are like results["autopilot_devops.log"]["timeline"]
                if "error_timeline" not in analysis_results["visualizations"]:
                    for key, value in list(analysis_results.items()):
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                if "_timeline" in sub_key and hasattr(sub_value, 'save'):
                                    analysis_results["visualizations"]["error_timeline"] = sub_value
                                    logger.log("Worker", f"Found timeline in nested structure: {key}.{sub_key}", level="INFO")
                                    break
        else:
            # No visualizations dict yet, check if timeline exists anywhere
            for key, value in list(analysis_results.items()):
                if "_timeline" in key and hasattr(value, 'save'):
                    if "visualizations" not in analysis_results:
                        analysis_results["visualizations"] = {}
                    analysis_results["visualizations"]["error_timeline"] = value
                    logger.log("Worker", f"Created visualizations dict and moved timeline from {key}", level="INFO")
                    break
        
        self._last_analysis_results = analysis_results
        
        return WorkerOutput(
            draft_response=draft,
            tools_used=tools_used,
            technique_applied=None  # Keep for compatibility
        ).to_dict()
    
    def _handle_repo_analysis(self, target_paths: list, repo_path: str = ".", instruction: str = "") -> tuple:
        """Handle repository analysis."""
        tools_used = []
        results = {}
        
        # Read directory tree
        tree_data = Tools.read_directory_tree(repo_path)
        tools_used.append("read_directory_tree")
        results["tree"] = tree_data
        
        # Get dependency graph
        dep_graph = Tools.get_dependency_graph(repo_path)
        tools_used.append("get_dependency_graph")
        results["dependency_graph"] = dep_graph
        
        # Check if user requested complexity heatmap or full complexity analysis
        instruction_lower = instruction.lower() if instruction else ""
        needs_full_complexity = (
            "heatmap" in instruction_lower or 
            "complexity" in instruction_lower or
            "complex" in instruction_lower or
            "hotspot" in instruction_lower or
            "metric" in instruction_lower or
            not target_paths  # If no specific paths, do full analysis
        )
        
        logger.log("Worker", f"Complexity analysis decision: needs_full={needs_full_complexity}, target_paths={target_paths[:3] if target_paths else 'None'}, instruction='{instruction[:100]}'", level="INFO")
        
        # Analyze complexity - ALWAYS analyze all Python files for heatmap/complexity requests
        complexity_data = []
        if target_paths and not needs_full_complexity:
            # Analyze specific files if provided and not a heatmap request
            logger.log("Worker", f"Analyzing specific target paths: {target_paths[:5]}", level="INFO")
            for path in target_paths[:20]:  # Limit to 20 files
                # Handle relative paths within repo
                full_path = os.path.join(repo_path, path) if not os.path.isabs(path) else path
                if full_path.endswith('.py') and os.path.exists(full_path):
                    try:
                        complexity = Tools.compute_complexity(full_path)
                        tools_used.append("compute_complexity")
                        complexity_data.append({"file": path, "complexity": complexity})
                        logger.log("Worker", f"Computed complexity for {path}: avg={complexity.get('avg_complexity', 0)}", level="DEBUG")
                    except Exception as e:
                        logger.log("Worker", f"Failed to compute complexity for {path}: {e}", level="WARNING")
        else:
            # Analyze ALL Python files in repository for full heatmap
            logger.log("Worker", f"Full complexity analysis requested (heatmap/complete). Analyzing all Python files in {repo_path}", level="INFO")
            files_analyzed = 0
            files_failed = 0
            for root, dirs, files in os.walk(repo_path):
                # Skip ignored directories
                dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'venv', 'node_modules', '.gradio', 'tests', 'dist', 'build'}]
                for file in files:
                    if file.endswith('.py'):
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, repo_path)
                        try:
                            complexity = Tools.compute_complexity(full_path)
                            tools_used.append("compute_complexity")
                            complexity_data.append({"file": rel_path, "complexity": complexity})
                            files_analyzed += 1
                            if files_analyzed % 10 == 0:
                                logger.log("Worker", f"Analyzed {files_analyzed} files so far...", level="INFO")
                            # Limit to top 50 files to avoid performance issues
                            if len(complexity_data) >= 50:
                                logger.log("Worker", f"Reached limit of 50 files for complexity analysis", level="INFO")
                                break
                        except Exception as e:
                            files_failed += 1
                            logger.log("Worker", f"Failed to compute complexity for {rel_path}: {e}", level="WARNING")
                if len(complexity_data) >= 50:
                    break
            
            logger.log("Worker", f"Complexity analysis complete: {files_analyzed} files analyzed, {files_failed} failed, {len(complexity_data)} total results", level="INFO")
        
        # Detect dead code
        dead_code = Tools.detect_dead_code(repo_path)
        tools_used.append("detect_dead_code")
        results["dead_code"] = dead_code
        
        # Detect duplicate code
        duplicates = Tools.detect_duplicate_code(repo_path)
        tools_used.append("detect_duplicate_code")
        results["duplicates"] = duplicates
        
        # Generate dependency graph visualization (always generate, even if empty)
        try:
            dep_graph_viz = Visualizations.plot_dependency_graph(dep_graph)
            results["dependency_graph_image"] = dep_graph_viz
            node_count = dep_graph.get("node_count", 0)
            edge_count = dep_graph.get("edge_count", 0)
            logger.log("Worker", f"Generated dependency graph visualization: {node_count} nodes, {edge_count} edges", level="INFO")
        except Exception as e:
            logger.log("Worker", f"Failed to generate dependency graph viz: {e}", level="ERROR")
            import traceback
            logger.log("Worker", f"Traceback: {traceback.format_exc()}", level="ERROR")
            # Create a placeholder image on error
            try:
                fig, ax = plt.subplots(figsize=(8, 6), facecolor='#1a1a1a')
                ax.set_facecolor('#1a1a1a')
                ax.text(0.5, 0.5, f'Error generating dependency graph:\n{str(e)}', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, color='#ff6b6b', fontsize=12)
                ax.axis('off')
                buf = io.BytesIO()
                plt.savefig(buf, format='png', facecolor='#1a1a1a', edgecolor='none')
                buf.seek(0)
                plt.close()
                results["dependency_graph_image"] = PILImage.open(buf)
            except:
                pass
        
        # Generate complexity heatmap (always generate, even if empty)
        try:
            logger.log("Worker", f"Generating complexity heatmap with {len(complexity_data)} files", level="INFO")
            if complexity_data:
                # Log sample complexity data for debugging
                sample = complexity_data[0] if complexity_data else {}
                logger.log("Worker", f"Sample complexity data: file={sample.get('file', 'N/A')}, complexity keys={list(sample.get('complexity', {}).keys())}", level="DEBUG")
            
            heatmap = Visualizations.plot_complexity_heatmap(complexity_data)
            results["complexity_heatmap"] = heatmap
            logger.log("Worker", f"Successfully generated complexity heatmap visualization: {len(complexity_data)} files analyzed", level="INFO")
        except Exception as e:
            logger.log("Worker", f"Failed to generate heatmap: {e}", level="ERROR")
            import traceback
            logger.log("Worker", f"Traceback: {traceback.format_exc()}", level="ERROR")
            # Create a placeholder image on error
            try:
                fig, ax = plt.subplots(figsize=(8, 6), facecolor='#1a1a1a')
                ax.set_facecolor('#1a1a1a')
                ax.text(0.5, 0.5, f'Error generating complexity heatmap:\n{str(e)}', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, color='#ff6b6b', fontsize=12)
                ax.axis('off')
                buf = io.BytesIO()
                plt.savefig(buf, format='png', facecolor='#1a1a1a', edgecolor='none')
                buf.seek(0)
                plt.close()
                results["complexity_heatmap"] = PILImage.open(buf)
            except Exception as e2:
                logger.log("Worker", f"Failed to create error placeholder: {e2}", level="ERROR")
        
        # Format complexity summary for context
        complexity_summary = self._format_complexity(complexity_data)
        heatmap_generated = "complexity_heatmap" in results
        dep_graph_generated = "dependency_graph_image" in results
        
        # Create detailed complexity report
        if complexity_data:
            top_complex = sorted(complexity_data, 
                               key=lambda x: x.get("complexity", {}).get("avg_complexity", 0), 
                               reverse=True)[:10]
            complexity_details = "\n".join([
                f"  {i+1}. {item.get('file', 'unknown')}: avg={item.get('complexity', {}).get('avg_complexity', 0):.1f}, total={item.get('complexity', {}).get('complexity', 0)}, functions={item.get('complexity', {}).get('function_count', 0)}"
                for i, item in enumerate(top_complex)
            ])
        else:
            complexity_details = "  No complexity data collected. Analysis may have failed or no Python files found."
        
        context = f"""
        ========== ANALYSIS RESULTS (ALL COMPLETED) ==========
        
        Repository Structure:
        - Total files: {tree_data.get('file_count', 0)}
        - Dependency nodes: {dep_graph.get('node_count', 0)}
        - Dependency edges: {dep_graph.get('edge_count', 0)}
        
        Code Complexity Analysis (COMPLETED):
        {complexity_summary}
        
        Top 10 Most Complex Files:
        {complexity_details}
        
        - Total files analyzed for complexity: {len(complexity_data)}
        - Complexity heatmap visualization: {"✅ GENERATED - Available in Hotspots tab" if heatmap_generated else "❌ Not generated"}
        
        Dead Code Detection (COMPLETED):
        - Potentially unused functions: {len(dead_code.get('unused_functions', []))}
        - Potentially unused imports: {len(dead_code.get('unused_imports', []))}
        
        Duplicate Code Detection (COMPLETED):
        - Duplicate blocks found: {duplicates.get('total_duplicates', 0)}
        - Files analyzed: {duplicates.get('files_analyzed', 0)}
        
        Dependency Graph Visualization: {"✅ GENERATED - Available in Dependencies tab" if dep_graph_generated else "❌ Not generated"}
        
        ========== CRITICAL INSTRUCTIONS ==========
        - ALL ANALYSIS HAS BEEN COMPLETED by automated tools
        - Report on the ACTUAL results shown above
        - If complexity data exists ({len(complexity_data)} items), report the actual metrics and file names
        - If heatmap was generated, explicitly mention: "A complexity heatmap visualization has been generated and is available in the Hotspots tab of the dashboard"
        - Do NOT say you cannot execute code or use tools - the analysis is already done!
        - Do NOT say "No complexity data" if complexity_data has {len(complexity_data)} items
        ============================================
        """
        
        results["complexity"] = complexity_data
        
        # Generate refactoring suggestions for top complex files
        if complexity_data:
            refactor_suggestions = []
            top_complex = sorted(complexity_data, 
                               key=lambda x: x.get("complexity", {}).get("avg_complexity", 0), 
                               reverse=True)[:5]  # Top 5 most complex files
            
            for item in top_complex:
                file_path = item.get("file", "")
                if not file_path or not file_path.endswith('.py'):
                    continue
                
                full_path = os.path.join(repo_path, file_path) if not os.path.isabs(file_path) else file_path
                if not os.path.exists(full_path):
                    continue
                
                complexity = item.get("complexity", {})
                imports = Tools.extract_imports(full_path)
                tools_used.append("extract_imports")
                
                refactor_suggestions.append({
                    "file": file_path,
                    "complexity": complexity,
                    "imports": imports,
                    "suggestions": self._generate_refactor_suggestions(complexity, imports)
                })
            
            if refactor_suggestions:
                results["refactor_suggestions"] = refactor_suggestions
        
        return context, tools_used, results
    
    def _handle_incident_analysis(self, target_paths: list, repo_path: str = ".") -> tuple:
        """Handle log/incident analysis."""
        tools_used = []
        results = {}
        
        # Default log file if not specified
        log_files = target_paths if target_paths else ["autopilot_devops.log"]
        
        all_errors = []
        all_warnings = []
        
        for log_file in log_files[:3]:  # Limit to 3 log files
            if not log_file:
                continue
            
            # Handle relative paths within repo
            full_path = os.path.join(repo_path, log_file) if not os.path.isabs(log_file) else log_file
            log_data = Tools.parse_logs(full_path)
            tools_used.append("parse_logs")
            
            # ALWAYS generate timeline visualization, even if no errors
            try:
                timeline_viz = Visualizations.plot_error_timeline(log_data)
                # Store in both places for compatibility
                results[f"{log_file}_timeline"] = timeline_viz
                # Also store in visualizations dict for main agent extraction
                if "visualizations" not in results:
                    results["visualizations"] = {}
                results["visualizations"]["error_timeline"] = timeline_viz
                error_count = log_data.get('error_count', 0)
                warning_count = len(log_data.get('warnings', []))
                logger.log("Worker", f"Generated error timeline visualization for {log_file} (errors: {error_count}, warnings: {warning_count})", level="INFO")
            except Exception as e:
                logger.log("Worker", f"Failed to generate timeline: {e}", level="ERROR")
                import traceback
                logger.log("Worker", f"Traceback: {traceback.format_exc()}", level="ERROR")
                # Create placeholder on error
                try:
                    fig, ax = plt.subplots(figsize=(10, 6), facecolor='#1a1a1a')
                    ax.set_facecolor('#1a1a1a')
                    ax.text(0.5, 0.5, f'Error generating timeline:\n{str(e)}', 
                           horizontalalignment='center', verticalalignment='center',
                           transform=ax.transAxes, color='#ff6b6b', fontsize=12)
                    ax.axis('off')
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', facecolor='#1a1a1a', edgecolor='none')
                    buf.seek(0)
                    plt.close()
                    if "visualizations" not in results:
                        results["visualizations"] = {}
                    results["visualizations"]["error_timeline"] = PILImage.open(buf)
                except:
                    pass
            
            if log_data.get("error_count", 0) > 0:
                # Cluster errors
                clusters = Tools.cluster_errors(log_data)
                tools_used.append("cluster_errors")
                
                # Detect anomalies
                anomalies = Tools.detect_anomalies(log_data)
                tools_used.append("detect_anomalies")
                
                # Generate postmortem
                postmortem = Tools.generate_postmortem(clusters, 
                    incident_summary=f"Incident analysis for {log_file}")
                tools_used.append("generate_postmortem")
                
                results[log_file] = {
                    "log_data": log_data,
                    "clusters": clusters,
                    "anomalies": anomalies,
                    "postmortem": postmortem
                }
            else:
                # Store log data even if no errors
                results[log_file] = {
                    "log_data": log_data,
                    "clusters": {},
                    "anomalies": {},
                    "postmortem": {}
                }
            
            all_errors.extend(log_data.get("errors", []))
            all_warnings.extend(log_data.get("warnings", []))
        
        # Helper to safely get clusters count
        def get_clusters_count(log_file_key):
            if not log_file_key or log_file_key not in results:
                return 0
            val = results[log_file_key]
            # Skip PIL Image objects
            if hasattr(val, 'save'):
                return 0
            if isinstance(val, dict):
                clusters = val.get('clusters', {})
                if isinstance(clusters, dict):
                    return len(clusters.get('clusters', []))
            return 0
        
        # Helper to safely get anomalies count from results
        def get_anomalies_count():
            count = 0
            for r in results.values():
                # Skip PIL Image objects and "visualizations" dict
                if hasattr(r, 'save') or not isinstance(r, dict):
                    continue
                anomalies = r.get('anomalies', {})
                if isinstance(anomalies, dict):
                    count += len(anomalies.get('anomalies', []))
            return count
        
        context = f"""
        Log Analysis Summary:
        - Total errors found: {len(all_errors)}
        - Total warnings found: {len(all_warnings)}
        - Log files analyzed: {len(log_files)}
        
        Error Clusters: {get_clusters_count(log_files[0] if log_files else None)}
        Anomalies detected: {get_anomalies_count()}
        """
        
        return context, tools_used, results
    
    def _handle_migration(self, planner_output: Dict, repo_path: str = ".") -> tuple:
        """Handle migration planning."""
        tools_used = []
        results = {}
        
        # Extract source/target from instruction or use defaults
        instruction = planner_output.get("instruction", "")
        # Try to extract framework names (simplified)
        source_framework = "flask"  # Default
        target_framework = "fastapi"  # Default
        
        # Check for outdated libraries
        req_path = os.path.join(repo_path, "requirements.txt")
        outdated = Tools.list_outdated_libraries(req_path)
        tools_used.append("list_outdated_libraries")
        results["outdated_libraries"] = outdated
        
        # Generate migration plan
        migration_plan = Tools.generate_migration_plan(source_framework, target_framework)
        tools_used.append("generate_migration_plan")
        results["migration_plan"] = migration_plan
        
        context = f"""
        Migration Analysis:
        - Source Framework: {source_framework}
        - Target Framework: {target_framework}
        - Deprecated packages found: {len(outdated.get('deprecated', []))}
        
        Migration Steps:
        {chr(10).join(migration_plan.get('steps', []))}
        
        Breaking Changes:
        {chr(10).join(migration_plan.get('breaking_changes', []))}
        """
        
        return context, tools_used, results
    
    def _handle_refactor(self, target_paths: list, repo_path: str = ".") -> tuple:
        """Handle refactoring suggestions."""
        tools_used = []
        results = {}
        
        refactor_suggestions = []
        
        # If no target_paths provided, analyze top complex files from full analysis
        if not target_paths:
            # Perform full complexity analysis to find complex files
            complexity_data = Tools.compute_complexity(repo_path)
            tools_used.append("compute_complexity")
            
            # Sort by complexity and take top 5
            sorted_files = sorted(
                complexity_data,
                key=lambda x: x.get("complexity", {}).get("avg_complexity", 0),
                reverse=True
            )[:5]
            
            target_paths = [item.get("file", "") for item in sorted_files if item.get("file")]
        
        for path in target_paths[:5]:  # Limit to 5 files
            if not path or not path.endswith('.py'):
                continue
            
            # Handle relative paths within repo
            full_path = os.path.join(repo_path, path) if not os.path.isabs(path) else path
            if not os.path.exists(full_path):
                continue
            
            # Read file
            file_data = Tools.read_file(full_path)
            tools_used.append("read_file")
            
            # Compute complexity
            complexity_result = Tools.compute_complexity(full_path)
            tools_used.append("compute_complexity")
            
            # Extract imports
            imports = Tools.extract_imports(full_path)
            tools_used.append("extract_imports")
            
            # Handle both dict and list results from compute_complexity
            if isinstance(complexity_result, list) and len(complexity_result) > 0:
                complexity = complexity_result[0].get("complexity", {})
            elif isinstance(complexity_result, dict):
                complexity = complexity_result
            else:
                complexity = {}
            
            refactor_suggestions.append({
                "file": path,
                "complexity": complexity,
                "imports": imports,
                "suggestions": self._generate_refactor_suggestions(complexity, imports)
            })
        
        results["refactor_suggestions"] = refactor_suggestions
        
        context = f"""
        Refactoring Analysis:
        - Files analyzed: {len(refactor_suggestions)}
        - High complexity files: {sum(1 for r in refactor_suggestions if r['complexity'].get('avg_complexity', 0) > 10)}
        
        Suggestions generated for each file based on complexity and import analysis.
        """
        
        return context, tools_used, results
    
    def _handle_documentation(self, target_paths: list, repo_path: str = ".") -> tuple:
        """Handle documentation generation."""
        tools_used = []
        results = {}
        
        # Get repo structure
        tree_data = Tools.read_directory_tree(repo_path)
        tools_used.append("read_directory_tree")
        
        # Get dependency graph
        dep_graph = Tools.get_dependency_graph(repo_path)
        tools_used.append("get_dependency_graph")
        
        # Generate markdown docs
        repo_map = {"tree": tree_data.get("tree"), "nodes": dep_graph.get("nodes", [])}
        docs = Tools.generate_markdown_docs(repo_map)
        tools_used.append("generate_markdown_docs")
        results["documentation"] = docs
        
        context = f"""
        Documentation Generated:
        - Sections: {len(docs.get('sections', []))}
        - Length: {docs.get('length', 0)} characters
        
        Documentation content is ready for display.
        """
        
        return context, tools_used, results
    
    def _handle_architecture(self, target_paths: list, repo_path: str = ".") -> tuple:
        """Handle architecture analysis."""
        tools_used = []
        results = {}
        
        # Get dependency graph
        dep_graph = Tools.get_dependency_graph(repo_path)
        tools_used.append("get_dependency_graph")
        results["dependency_graph"] = dep_graph
        
        # Read directory tree
        tree_data = Tools.read_directory_tree(repo_path)
        tools_used.append("read_directory_tree")
        results["tree"] = tree_data
        
        context = f"""
        Architecture Overview:
        - Total modules: {dep_graph.get('node_count', 0)}
        - Dependencies: {dep_graph.get('edge_count', 0)}
        - File structure: {tree_data.get('file_count', 0)} files
        
        Dependency relationships and module structure analyzed.
        """
        
        return context, tools_used, results
    
    def _format_complexity(self, complexity_data: list) -> str:
        """Format complexity data for display."""
        if not complexity_data:
            return "No complexity data available. Analysis may not have completed."
        
        formatted = []
        # Sort by average complexity (descending) to show most complex first
        sorted_data = sorted(complexity_data, 
                           key=lambda x: x.get("complexity", {}).get("avg_complexity", 0), 
                           reverse=True)
        
        formatted.append(f"Total files analyzed: {len(complexity_data)}")
        formatted.append(f"\nTop {min(10, len(sorted_data))} most complex files:")
        
        for item in sorted_data[:10]:  # Show top 10
            file = item.get("file", "unknown")
            comp = item.get("complexity", {})
            avg = comp.get("avg_complexity", 0)
            total = comp.get("complexity", 0)
            func_count = comp.get("function_count", 0)
            line_count = comp.get("line_count", 0)
            formatted.append(f"- {file}: {func_count} functions, avg complexity {avg:.1f}, total complexity {total}, {line_count} lines")
        
        return "\n".join(formatted)
    
    def _generate_refactor_suggestions(self, complexity: Dict, imports: Dict) -> list:
        """Generate refactoring suggestions based on analysis."""
        suggestions = []
        
        avg_complexity = complexity.get("avg_complexity", 0)
        if avg_complexity > 10:
            suggestions.append("Consider breaking down complex functions into smaller, more focused functions.")
        
        if len(imports.get("imports", [])) > 20:
            suggestions.append("Consider reducing imports - may indicate tight coupling.")
        
        unused_imports = len(imports.get("imports", [])) - len(set(imports.get("imports", [])))
        if unused_imports > 0:
            suggestions.append(f"Found {unused_imports} potentially unused imports.")
        
        return suggestions
    
    def _format_analysis_results(self, results: Dict) -> str:
        """Format analysis results for display."""
        formatted = []
        
        if "dependency_graph" in results:
            dg = results["dependency_graph"]
            # Skip if it's a PIL Image
            if not hasattr(dg, 'save') and isinstance(dg, dict):
                formatted.append(f"- **Dependencies**: {dg.get('node_count', 0)} modules, {dg.get('edge_count', 0)} relationships")
        
        if "dead_code" in results:
            dc = results["dead_code"]
            # Skip if it's a PIL Image
            if not hasattr(dc, 'save') and isinstance(dc, dict):
                formatted.append(f"- **Dead Code**: {len(dc.get('unused_functions', []))} potentially unused functions")
        
        if "migration_plan" in results:
            mp = results["migration_plan"]
            # Skip if it's a PIL Image
            if not hasattr(mp, 'save') and isinstance(mp, dict):
                formatted.append(f"- **Migration**: {len(mp.get('steps', []))} steps identified")
        
        return "\n".join(formatted) if formatted else ""
    
    def _mock_work(self, planner_output: Dict) -> Dict:
        """Mock worker for testing."""
        action = planner_output.get("action", "general_chat")
        
        if action == "repo_analysis":
            draft = """
            **Repository Analysis Complete**
            
            - Files analyzed: 15
            - Dependencies: 8 modules, 12 relationships
            - Average complexity: 5.2
            - Dead code detected: 3 potentially unused functions
            
            The codebase shows moderate complexity with good modular structure.
            """
        elif action == "incident_analysis":
            draft = """
            **Incident Analysis**
            
            - Errors found: 12
            - Error clusters: 3 unique patterns
            - Root cause: Configuration mismatch in database connection
            
            **Remediation**: Update database configuration and restart service.
            """
        elif action == "migration":
            draft = """
            **Migration Plan: Flask → FastAPI**
            
            1. Replace Flask routes with FastAPI path decorators
            2. Convert request.json to Pydantic models
            3. Update dependency injection patterns
            
            **Breaking Changes**: Async conversion required for routes.
            """
        elif action == "enforce_boundary":
            draft = """
            I cannot perform destructive operations like file deletion or system modifications.
            
            I am a read-only DevOps analysis tool. I can help you:
            - Analyze codebases
            - Parse logs
            - Generate documentation
            - Suggest safe refactoring
            
            Would you like me to suggest a safe alternative?
            """
        else:
            draft = "I'm here to help with DevOps tasks. How can I assist you?"
        
        return WorkerOutput(
            draft_response=draft,
            tools_used=["mock_mode"],
            technique_applied=None
        ).to_dict()
