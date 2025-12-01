import gradio as gr
import os
import sys
import matplotlib
matplotlib.use('Agg') # Non-interactive backend for server environments
import matplotlib.pyplot as plt
import io
from PIL import Image
from loguru import logger
from dotenv import load_dotenv
from typing import Dict, List, Optional

# Load environment variables
load_dotenv()

# --- 1. SETUP LOGGING ---
LOG_FILE = "autopilot_devops.log"
# Clear logs on restart so you see fresh output
with open(LOG_FILE, "w") as f:
    f.write("--- AutoPilot DevOps System Session Started ---\n")

logger.add(LOG_FILE, rotation="1 MB", format="{time:HH:mm:ss} | {level} | {message}")

# --- 2. IMPORT AGENT ---
try:
    from project.main_agent import MainAgent
    from project.config import Config
    
    # Validation logic
    try:
        Config.validate()
        mode = "MOCK" if Config.MOCK_MODE else "LIVE"
        logger.info(f"System Startup: {mode} Mode")
    except Exception as e:
        logger.warning(f"Config validation warning: {e}")

    # Initialize Global Agent Wrapper
    agent_instance = MainAgent()

except ImportError as e:
    logger.error(f"Failed to import project modules: {e}")
    # Fallback for UI testing if backend is missing
    class MockAgent:
        def handle_message(self, msg):
            return {
                "response": "Backend modules missing. Please check import paths.",
                "plan": {"action": "error", "risk_level": "LOW", "emotion": "Error", "distress_score": 0},
                "safety_status": "SAFE"
            }
    agent_instance = MockAgent()

# --- 3. HELPER FUNCTIONS ---

def get_empty_state():
    """Returns initial state for a new user session."""
    return {
        "complexity_history": [],  # Code complexity scores over time
        "msg_count": 0,
        "current_severity": "LOW",  # Severity of code issues
        "last_module": "None",  # Last analyzed module/file
        "max_complexity": 0
    }

def generate_plot(user_state):
    """Generates a matplotlib chart of code complexity metrics based on user state."""
    if user_state is None:
        user_state = get_empty_state()
        
    history = user_state.get("complexity_history", [])
    
    # Create figure with light mode styling - compact size (80% scale)
    fig = plt.figure(figsize=(4.4, 1.28), facecolor='#1a1a1a')
    ax = plt.gca()
    ax.set_facecolor('#1a1a1a')
    
    if not history:
        plt.text(0.5, 0.5, 'Awaiting Analysis Request...', 
                 horizontalalignment='center', verticalalignment='center', 
                 transform=ax.transAxes, color='#a0a0a0', fontsize=12, fontweight=500)
        plt.axis('off')
    else:
        x = list(range(1, len(history) + 1))
        y = history
        
        # Dark mode colors
        last_score = history[-1]
        line_color = '#4ade80'  # Green
        if last_score > 5: line_color = '#fbbf24'  # Amber
        if last_score > 10: line_color = '#f87171'  # Red

        plt.plot(x, y, marker='o', linestyle='-', color=line_color, linewidth=2.5, markersize=6, markerfacecolor='#1a1a1a', markeredgewidth=2)
        plt.fill_between(x, y, color=line_color, alpha=0.2)
        
        plt.title("Code Complexity Trend", color='#e5e5e5', fontsize=8, fontweight=600, pad=3.2)
        plt.xlabel("Analysis #", color='#a0a0a0', fontsize=6.4, fontweight=500)
        plt.ylabel("Complexity Score", color='#a0a0a0', fontsize=6.4, fontweight=500)
        plt.ylim(0, max(max(history) * 1.15, 15) if history else 15)
        plt.grid(True, linestyle='--', alpha=0.2, color='#444444', linewidth=1)
        
        ax.tick_params(axis='x', colors='#a0a0a0', labelsize=6.4)
        ax.tick_params(axis='y', colors='#a0a0a0', labelsize=6.4)
        
        for spine in ax.spines.values():
            spine.set_color('#333333')
            spine.set_linewidth(1)

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', facecolor='#1a1a1a', edgecolor='none', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return Image.open(buf)

def generate_stats_html(user_state):
    """Generates the HTML for the Code Health Monitor."""
    if user_state is None:
        user_state = get_empty_state()

    severity = user_state.get("current_severity", "LOW")
    
    color_class = "status-green"
    icon = "✅"
    bg_color = "#f0fff4"
    border_color = "#9ae6b4"
    if severity == "MEDIUM": 
        color_class = "status-orange"
        icon = "⚠️"
        bg_color = "#fffaf0"
        border_color = "#fbd38d"
    elif severity == "HIGH": 
        color_class = "status-red"
        icon = "🚨"
        bg_color = "#fff5f5"
        border_color = "#fc8181"

    # Dark mode color classes
    color_classes = {
        "LOW": "bg-green-900/20 border-green-700/50 text-green-400",
        "MEDIUM": "bg-yellow-900/20 border-yellow-700/50 text-yellow-400",
        "HIGH": "bg-red-900/20 border-red-700/50 text-red-400"
    }
    
    icons = {
        "LOW": "✅",
        "MEDIUM": "⚠️",
        "HIGH": "🚨"
    }
    
    status_class = color_classes.get(severity, color_classes["LOW"])
    icon = icons.get(severity, "✅")
    text_color = "text-green-400" if severity == "LOW" else "text-yellow-400" if severity == "MEDIUM" else "text-red-400"

    return f"""
    <div class="grid grid-cols-2 gap-2 mb-3">
        <button type="button" class="w-full bg-[#1a1a1a] border border-[#333333] rounded-md p-3 hover:border-[#3291ff] hover:bg-[#2a2a2a] transition-all text-left cursor-pointer group focus:outline-none focus:ring-2 focus:ring-[#3291ff] focus:ring-offset-1">
            <div class="text-[10px] font-medium text-[#a0a0a0] uppercase tracking-wide mb-1.5">CODE HEALTH</div>
            <div class="text-base font-bold {text_color} flex items-center gap-1.5">
                <span>{icon}</span>
                <span>{severity}</span>
            </div>
        </button>
        <button type="button" class="w-full bg-[#1a1a1a] border border-[#333333] rounded-md p-3 hover:border-[#3291ff] hover:bg-[#2a2a2a] transition-all text-left cursor-pointer group focus:outline-none focus:ring-2 focus:ring-[#3291ff] focus:ring-offset-1">
            <div class="text-[10px] font-medium text-[#a0a0a0] uppercase tracking-wide mb-1.5">LAST MODULE</div>
            <div class="text-base font-bold text-[#e5e5e5] truncate">{user_state.get("last_module", "None").title()}</div>
        </button>
        <button type="button" class="w-full bg-[#1a1a1a] border border-[#333333] rounded-md p-3 hover:border-[#3291ff] hover:bg-[#2a2a2a] transition-all text-left cursor-pointer group focus:outline-none focus:ring-2 focus:ring-[#3291ff] focus:ring-offset-1">
            <div class="text-[10px] font-medium text-[#a0a0a0] uppercase tracking-wide mb-1.5">PEAK COMPLEXITY</div>
            <div class="text-base font-bold text-[#e5e5e5]">
                {user_state.get("max_complexity", 0)}<span class="text-xs text-[#a0a0a0] font-normal ml-1">/15</span>
            </div>
        </button>
        <button type="button" class="w-full bg-[#1a1a1a] border border-[#333333] rounded-md p-3 hover:border-[#3291ff] hover:bg-[#2a2a2a] transition-all text-left cursor-pointer group focus:outline-none focus:ring-2 focus:ring-[#3291ff] focus:ring-offset-1">
            <div class="text-[10px] font-medium text-[#a0a0a0] uppercase tracking-wide mb-1.5">ANALYSES</div>
            <div class="text-base font-bold text-[#e5e5e5]">{user_state.get("msg_count", 0)}</div>
        </button>
    </div>
    """

def _format_dead_code_display(dead_code_data: Dict) -> str:
    """Format dead code data for display."""
    if not dead_code_data or not isinstance(dead_code_data, dict):
        return "Run repository analysis to see dead code report."
    
    unused_funcs = dead_code_data.get("unused_functions", [])
    unused_imports = dead_code_data.get("unused_imports", [])
    total_funcs = dead_code_data.get("total_functions", 0)
    total_imports = dead_code_data.get("total_imports", 0)
    
    md = f"""## Dead Code Analysis

**Summary:**
- Potentially unused functions: **{len(unused_funcs)}**
- Potentially unused imports: **{len(unused_imports)}**
- Total functions analyzed: {total_funcs}
- Total imports analyzed: {total_imports}

"""
    
    if unused_funcs:
        md += "### Unused Functions\n\n"
        for func in unused_funcs[:10]:  # Limit to 10
            md += f"- `{func}`\n"
        if len(unused_funcs) > 10:
            md += f"\n*... and {len(unused_funcs) - 10} more*\n"
    
    if unused_imports:
        md += "\n### Unused Imports\n\n"
        for imp in unused_imports[:10]:  # Limit to 10
            md += f"- `{imp}`\n"
        if len(unused_imports) > 10:
            md += f"\n*... and {len(unused_imports) - 10} more*\n"
    
    if not unused_funcs and not unused_imports:
        md += "✅ No dead code detected!"
    
    return md

def _format_migration_display(migration_data: Dict) -> str:
    """Format migration plan for display."""
    if not migration_data or not isinstance(migration_data, dict):
        return """## Migration Analysis

**Status:** No migration plan available

To generate a migration plan, ask for migration analysis, for example:
- "Migrate Flask to FastAPI"
- "Upgrade Django to version 4"
- "Migrate from Python 2 to Python 3"

The system will analyze your codebase and generate a detailed migration plan with steps, breaking changes, and compatibility notes.
"""
    
    plan_title = migration_data.get("plan", "Migration Plan")
    steps = migration_data.get("steps", [])
    breaking_changes = migration_data.get("breaking_changes", [])
    compatibility = migration_data.get("compatibility", "Unknown")
    effort = migration_data.get("estimated_effort", "Medium")
    
    md = f"""## {plan_title}

**Compatibility:** {compatibility}  
**Estimated Effort:** {effort}

"""
    
    if steps:
        md += "### Migration Steps\n\n"
        for i, step in enumerate(steps, 1):
            md += f"{i}. {step}\n"
    else:
        md += "### Migration Steps\n\n*No specific steps defined.*\n"
    
    if breaking_changes:
        md += "\n### Breaking Changes\n\n"
        for change in breaking_changes:
            md += f"- ⚠️ {change}\n"
    else:
        md += "\n### Breaking Changes\n\n✅ No breaking changes identified.\n"
    
    return md

def _format_refactor_display(refactor_data: List) -> str:
    """Format refactoring suggestions for display."""
    if not refactor_data or not isinstance(refactor_data, list):
        return """## Refactoring Suggestions

**Status:** No refactoring suggestions available

To get refactoring suggestions, request a refactoring analysis, for example:
- "Refactor main_agent.py"
- "Suggest refactoring for high complexity files"
- "Analyze code quality and suggest improvements"

The system will analyze code complexity and provide specific refactoring recommendations.
"""
    
    md = "## Refactoring Suggestions\n\n"
    
    if not refactor_data:
        md += "✅ No refactoring suggestions needed. Code quality is good!"
        return md
    
    for item in refactor_data:
        if isinstance(item, dict):
            file_path = item.get("file", "Unknown")
            complexity = item.get("complexity", {})
            suggestions = item.get("suggestions", [])
            
            avg_comp = complexity.get("avg_complexity", 0)
            func_count = complexity.get("function_count", 0)
            
            md += f"### `{file_path}`\n\n"
            md += f"- **Average Complexity:** {avg_comp:.1f}\n"
            md += f"- **Functions:** {func_count}\n\n"
            
            if suggestions:
                md += "**Suggestions:**\n"
                for suggestion in suggestions:
                    md += f"- {suggestion}\n"
            else:
                md += "*No specific suggestions for this file.*\n"
            md += "\n"
        else:
            md += f"- {item}\n"
    
    return md

def _format_duplicate_display(duplicate_data: Dict) -> str:
    """Format duplicate code data for display."""
    if not duplicate_data or not isinstance(duplicate_data, dict):
        return "Run repository analysis to see duplicate code detection."
    
    duplicates = duplicate_data.get("duplicates", [])
    total = duplicate_data.get("total_duplicates", 0)
    files_analyzed = duplicate_data.get("files_analyzed", 0)
    
    md = f"""## Duplicate Code Detection

**Summary:**
- Duplicate blocks found: **{total}**
- Files analyzed: {files_analyzed}

"""
    
    if duplicates:
        md += "### Duplicate Blocks\n\n"
        for dup in duplicates[:10]:  # Limit to 10
            file1 = dup.get("file1", "Unknown")
            file2 = dup.get("file2", "Unknown")
            similarity = dup.get("similarity", 0)
            common_blocks = dup.get("common_blocks", [])
            
            md += f"**{file1}** ↔ **{file2}** (Similarity: {similarity:.1%})\n"
            if common_blocks:
                total_lines = sum(block.get("lines", 0) for block in common_blocks)
                md += f"- {len(common_blocks)} common block(s), {total_lines} total lines\n"
            md += "\n"
        
        if len(duplicates) > 10:
            md += f"\n*... and {len(duplicates) - 10} more duplicate pairs*\n"
    else:
        md += "✅ No duplicate code detected!"
    
    return md

def _format_postmortem_display(postmortem_data: Dict) -> str:
    """Format postmortem for display."""
    if not postmortem_data or not isinstance(postmortem_data, dict):
        return """## Incident Postmortem

**Status:** No postmortem available

To generate a postmortem, analyze logs or incidents, for example:
- "Analyze the logs"
- "Generate postmortem for recent errors"
- "What caused the incident?"

The system will analyze log files, cluster errors, and generate a structured postmortem report with root cause analysis and recommendations.
"""
    
    postmortem_md = postmortem_data.get("postmortem", "")
    if postmortem_md and isinstance(postmortem_md, str) and len(postmortem_md) > 10:
        return postmortem_md
    
    # Fallback: build from available data
    error_count = postmortem_data.get("error_count", 0)
    warning_count = postmortem_data.get("warning_count", 0)
    recommendations = postmortem_data.get("recommendations", [])
    clusters = postmortem_data.get("clusters", {})
    anomalies = postmortem_data.get("anomalies", {})
    
    md = f"""## Incident Postmortem

**Summary:**
- Errors found: {error_count}
- Warnings found: {warning_count}
"""
    
    if clusters:
        cluster_count = len(clusters.get("clusters", []))
        if cluster_count > 0:
            md += f"- Error clusters: {cluster_count}\n"
    
    if anomalies:
        anomaly_count = len(anomalies.get("anomalies", []))
        if anomaly_count > 0:
            md += f"- Anomalies detected: {anomaly_count}\n"
    
    md += "\n"
    
    if recommendations:
        md += "### Recommendations\n\n"
        for rec in recommendations:
            md += f"- {rec}\n"
    else:
        md += "### Recommendations\n\n*No specific recommendations available.*\n"
    
    if error_count == 0 and warning_count == 0:
        md += "\n✅ **No incidents detected.** System is operating normally.\n"
    
    return md
    
    md = f"""## Incident Postmortem

**Summary:**
- Errors: {error_count}
- Warnings: {warning_count}

### Recommendations

"""
    for rec in recommendations:
        md += f"{rec}\n"
    
    return md

def get_live_logs():
    """Reads the last N chars of the log file."""
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return f.read()[-3000:]
        except Exception:
            return "Loading logs..."
    return "Initializing system logs..."

def response_generator(message, history, user_state, repo_url=None):
    """
    Generator function for ChatInterface.
    Uses gr.State (user_state) to keep data separate for every user.
    """
    if user_state is None:
        user_state = get_empty_state()

    if not message:
        # Return empty message with default values for all outputs
        empty_plot = generate_plot(user_state)
        empty_stats = generate_stats_html(user_state)
        yield (
            "",  # Message (string only for chatbot)
            user_state,  # State
            empty_plot,  # Plot image
            empty_stats,  # Stats HTML
            None,  # Dep graph
            None,  # Heatmap
            None,  # Timeline
            "Run repository analysis to see dead code report.",  # Dead code
            "Ask for migration analysis to see plans.",  # Migration
            "Request refactoring analysis for suggestions.",  # Refactor
            "Run repository analysis to see duplicate code detection.",  # Duplicates
            "Analyze logs to generate postmortem."  # Postmortem
        )
        return
        
    try:
        # Update GitHub token from environment if available
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            from project.config import Config
            Config.GITHUB_TOKEN = github_token
        
        # Run the agent with optional repository URL
        result_dict = agent_instance.handle_message(message, repo_url=repo_url)
        response_text = result_dict.get("response", "Error: No response text found.")
        
        # Extract metadata
        plan = result_dict.get('plan', {})
        action = plan.get('action')
        severity = plan.get('risk_level', 'LOW')  # Map risk_level to severity
        complexity = plan.get('complexity', 'LOW')
        task_type = plan.get('task_type', action)
        safety_status = result_dict.get("safety_status")
        
        # Extract visualizations
        visualizations = result_dict.get("visualizations", {})
        dep_graph_img = visualizations.get("dependency_graph_image")
        heatmap_img = visualizations.get("complexity_heatmap")
        
        # Debug logging for visualization extraction
        if dep_graph_img:
            logger.info(f"Dependency graph image extracted: {type(dep_graph_img)}, has save method: {hasattr(dep_graph_img, 'save')}")
        else:
            logger.info(f"No dependency graph image found in visualizations. Keys: {list(visualizations.keys())}")
        
        if heatmap_img:
            logger.info(f"Complexity heatmap image extracted: {type(heatmap_img)}, has save method: {hasattr(heatmap_img, 'save')}")
        else:
            logger.info(f"No complexity heatmap image found in visualizations. Keys: {list(visualizations.keys())}")
        timeline_img = None
        # Check for timeline in visualizations (direct key)
        if "error_timeline" in visualizations:
            timeline_img = visualizations["error_timeline"]
            logger.info(f"Found error_timeline in visualizations: {type(timeline_img)}")
        else:
            # Find timeline in log results (could be in nested structure)
            for key, value in visualizations.items():
                # Skip if value is a PIL Image (don't treat it as dict)
                if hasattr(value, 'save'):  # Direct PIL Image
                    if "timeline" in str(key).lower():
                        timeline_img = value
                        logger.info(f"Found timeline as direct value: {key}")
                        break
                elif isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        # Check if sub_value is a PIL Image
                        if hasattr(sub_value, 'save'):  # PIL Image
                            if "_timeline" in sub_key or "timeline" in str(sub_key).lower():
                                timeline_img = sub_value
                                logger.info(f"Found timeline in nested structure: {sub_key}")
                                break
                        elif isinstance(sub_value, dict) and "timeline" in str(sub_value):
                            # Nested dict with timeline key
                            if "timeline" in sub_value:
                                timeline_val = sub_value.get("timeline")
                                if hasattr(timeline_val, 'save'):
                                    timeline_img = timeline_val
                                    logger.info(f"Found timeline in deeply nested structure: {key}.{sub_key}")
                                    break
        
        if not timeline_img:
            logger.info(f"No timeline image found. Visualization keys: {list(visualizations.keys())}")
        
        # Extract structured data for tabs - check multiple sources
        dead_code_data = result_dict.get("dead_code_report", {})
        migration_data = result_dict.get("migration_plan_report", {})
        refactor_data = result_dict.get("refactor_suggestions_report", [])
        duplicate_data = result_dict.get("duplicate_code_report", {})
        postmortem_data = result_dict.get("postmortem_report", {})
        
        # Fallback: check visualizations dict
        if not dead_code_data:
            dead_code_data = visualizations.get("dead_code", {})
        if not migration_data:
            migration_data = visualizations.get("migration_plan", {})
        if not refactor_data:
            refactor_data = visualizations.get("refactor_suggestions", [])
        if not duplicate_data:
            duplicate_data = visualizations.get("duplicates", {})
        if not postmortem_data:
            postmortem_data = visualizations.get("postmortem", {})
        
        # Fallback: check nested structures in visualizations
        # IMPORTANT: Skip PIL Image objects - they don't have .get() method
        for key, value in visualizations.items():
            # Skip if value is a PIL Image (has 'save' method) - don't treat as dict
            if hasattr(value, 'save'):
                continue  # This is an image, not a dict
            elif isinstance(value, dict):
                if "dead_code" in value and not dead_code_data:
                    dead_code_data = value.get("dead_code", {})
                if "migration_plan" in value and not migration_data:
                    migration_data = value.get("migration_plan", {})
                if "refactor_suggestions" in value and not refactor_data:
                    refactor_data = value.get("refactor_suggestions", [])
                if "duplicates" in value and not duplicate_data:
                    duplicate_data = value.get("duplicates", {})
                if "postmortem" in value and not postmortem_data:
                    postmortem_data = value.get("postmortem", {})
        
        # Final fallback: check analysis_results directly from worker
        if hasattr(agent_instance, 'worker') and hasattr(agent_instance.worker, '_last_analysis_results'):
            analysis_results = agent_instance.worker._last_analysis_results
            if isinstance(analysis_results, dict):
                # Extract reports, but skip PIL Image objects
                for key, value in analysis_results.items():
                    # Skip PIL Image objects - they don't have .get() method
                    if hasattr(value, 'save'):
                        continue  # This is an image, not a dict
                    elif isinstance(value, dict):
                        if not dead_code_data and "dead_code" in value:
                            dead_code_data = value.get("dead_code", {})
                        if not migration_data and "migration_plan" in value:
                            migration_data = value.get("migration_plan", {})
                        if not refactor_data and "refactor_suggestions" in value:
                            refactor_data = value.get("refactor_suggestions", [])
                        if not duplicate_data and "duplicates" in value:
                            duplicate_data = value.get("duplicates", {})
                        if not postmortem_data and "postmortem" in value:
                            postmortem_data = value.get("postmortem", {})
                
                # Also check top-level keys (if not already found) - but verify they're not images
                if not dead_code_data and "dead_code" in analysis_results:
                    val = analysis_results["dead_code"]
                    if isinstance(val, dict) and not hasattr(val, 'save'):
                        dead_code_data = val
                if not migration_data and "migration_plan" in analysis_results:
                    val = analysis_results["migration_plan"]
                    if isinstance(val, dict) and not hasattr(val, 'save'):
                        migration_data = val
                if not refactor_data and "refactor_suggestions" in analysis_results:
                    val = analysis_results["refactor_suggestions"]
                    if isinstance(val, list) and not hasattr(val, 'save'):
                        refactor_data = val
                if not duplicate_data and "duplicates" in analysis_results:
                    val = analysis_results["duplicates"]
                    if isinstance(val, dict) and not hasattr(val, 'save'):
                        duplicate_data = val
        
        # Update State - map complexity to numeric score
        try:
            # Convert complexity level to numeric score
            complexity_map = {"LOW": 3, "MEDIUM": 7, "HIGH": 12}
            current_score = complexity_map.get(complexity, 5)
        except (ValueError, TypeError):
            current_score = 5
            
        if current_score > 0:
            user_state["complexity_history"].append(current_score)
            
        user_state["msg_count"] += 1
        user_state["current_severity"] = severity
        # Extract module name from target_paths if available
        target_paths = plan.get('target_paths', [])
        if target_paths:
            last_path = target_paths[0]
            user_state["last_module"] = last_path.split('/')[-1] if '/' in last_path else last_path.split('\\')[-1] if '\\' in last_path else last_path
        else:
            user_state["last_module"] = task_type.replace('_', ' ').title() if task_type else "None"
        user_state["max_complexity"] = max(user_state["max_complexity"], current_score)
        
        # Log to server console
        logger.info(f"User input processed. Severity: {severity} | Action: {action} | Task: {task_type}")

        # Add visual indicators to the text
        prefix = ""
        if severity == "HIGH":
            prefix = "🚨 **HIGH SEVERITY ISSUES DETECTED**\n\n"
        elif action == "enforce_boundary":
            prefix = "🛡️ **Safety Boundary Enforced:** "
        
        final_response = prefix + response_text
        
        # Prepare visualization outputs (use None if not available)
        plot_img = generate_plot(user_state)
        
        # Ensure PIL Images are properly formatted for Gradio
        dep_graph = dep_graph_img if dep_graph_img and hasattr(dep_graph_img, 'save') else None
        heatmap = heatmap_img if heatmap_img and hasattr(heatmap_img, 'save') else None
        timeline = timeline_img if timeline_img and hasattr(timeline_img, 'save') else None
        
        # Debug: Log visualization status
        if dep_graph:
            logger.info(f"Dependency graph ready: {type(dep_graph)}, size: {dep_graph.size if hasattr(dep_graph, 'size') else 'unknown'}")
        else:
            logger.info(f"No dependency graph image available. dep_graph_img type: {type(dep_graph_img)}")
        
        if heatmap:
            logger.info(f"Complexity heatmap ready: {type(heatmap)}, size: {heatmap.size if hasattr(heatmap, 'size') else 'unknown'}")
        else:
            logger.info(f"No complexity heatmap image available. heatmap_img type: {type(heatmap_img)}")
        
        if timeline:
            logger.info(f"Error timeline ready: {type(timeline)}, size: {timeline.size if hasattr(timeline, 'size') else 'unknown'}")
        else:
            logger.info(f"No error timeline image available. timeline_img type: {type(timeline_img)}")
        
        # Format data for display tabs
        dead_code_md = _format_dead_code_display(dead_code_data)
        migration_md = _format_migration_display(migration_data)
        refactor_md = _format_refactor_display(refactor_data)
        duplicate_md = _format_duplicate_display(duplicate_data)
        postmortem_md = _format_postmortem_display(postmortem_data)
        
        # Yield result with all outputs
        # First element must be the message string for the chatbot component
        # Remaining elements correspond to additional_outputs in order
        yield (
            final_response,  # Message string (for chatbot)
            user_state,  # State update
            plot_img,  # Plot image
            generate_stats_html(user_state),  # Stats HTML
            dep_graph,  # Dependency graph image
            heatmap,  # Heatmap image
            timeline,  # Timeline image
            dead_code_md,  # Dead code markdown
            migration_md,  # Migration markdown
            refactor_md,  # Refactor markdown
            duplicate_md,  # Duplicate markdown
            postmortem_md  # Postmortem markdown
        )

    except Exception as e:
        logger.error(f"Runtime Error: {e}")
        error_plot = generate_plot(user_state)
        error_stats = generate_stats_html(user_state)
        yield (
            f"System Error: {str(e)}",  # Error message (string)
            user_state,  # State
            error_plot,  # Plot image
            error_stats,  # Stats HTML
            None,  # Dep graph
            None,  # Heatmap
            None,  # Timeline
            "Error loading dead code data.",  # Dead code
            "Error loading migration data.",  # Migration
            "Error loading refactoring data.",  # Refactor
            "Error loading duplicate code data.",  # Duplicates
            "Error loading postmortem data."  # Postmortem
        )

# --- 4. UI LAYOUT ---

with gr.Blocks(title="AutoPilot DevOps") as demo:
    
    # State management for independent user sessions
    user_session = gr.State(value=get_empty_state())

    # 1. Initialization of Dynamic Output Components
    plot_output = gr.Image(label="Code Metrics Trend", type="pil", elem_id="plot_panel", interactive=False, render=False)
    stats_output = gr.HTML(value=generate_stats_html(get_empty_state()), elem_id="stats_panel", render=False)
    
    # New visualization outputs
    dep_graph_output = gr.Image(label="Dependency Graph", type="pil", elem_id="dep_graph_panel", interactive=False, render=False)
    heatmap_output = gr.Image(label="Complexity Heatmap", type="pil", elem_id="heatmap_panel", interactive=False, render=False)
    timeline_output = gr.Image(label="Error Timeline", type="pil", elem_id="timeline_panel", interactive=False, render=False)
    
    # Data display outputs for tabs
    dead_code_output = gr.Markdown(value="Run repository analysis to see dead code report.", elem_id="dead_code_display", render=False)
    migration_output = gr.Markdown(value="Ask for migration analysis to see plans.", elem_id="migration_display", render=False)
    refactor_output = gr.Markdown(value="Request refactoring analysis for suggestions.", elem_id="refactor_display", render=False)
    duplicate_output = gr.Markdown(value="Run repository analysis to see duplicate code detection.", elem_id="duplicate_display", render=False)
    postmortem_output = gr.Markdown(value="Analyze logs to generate postmortem.", elem_id="postmortem_display", render=False)

    # 2. Material Design UI with Vercel-like Aesthetics
    gr.HTML("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
        
        * { 
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        /* Material Design Color Palette - Dark Mode */
        :root {
            --md-primary: #3291ff;
            --md-primary-dark: #0070f3;
            --md-primary-light: #66b3ff;
            --md-surface: #1a1a1a;
            --md-background: #0a0a0a;
            --md-surface-variant: #2a2a2a;
            --md-on-surface: #e5e5e5;
            --md-on-surface-variant: #a0a0a0;
            --md-border: #333333;
            --md-shadow: rgba(0, 0, 0, 0.3);
            --md-elevation-1: 0 1px 3px rgba(0, 0, 0, 0.4), 0 1px 2px rgba(0, 0, 0, 0.5);
            --md-elevation-2: 0 3px 6px rgba(0, 0, 0, 0.5), 0 3px 6px rgba(0, 0, 0, 0.6);
            --md-elevation-4: 0 10px 20px rgba(0, 0, 0, 0.6), 0 6px 6px rgba(0, 0, 0, 0.7);
        }
        
        body, .gradio-container {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif !important;
            background: var(--md-background) !important;
            color: var(--md-on-surface) !important;
            line-height: 1.6;
        }
        
        .gradio-container {
            background: var(--md-background) !important;
            padding: 0 !important;
            min-height: 100vh;
        }
        
        /* Material Design Chatbot */
        .gradio-chatbot {
            border-radius: 12px !important;
            border: 1px solid var(--md-border) !important;
            background: var(--md-surface) !important;
            padding: 16px !important;
            box-shadow: var(--md-elevation-1) !important;
            transition: box-shadow 0.3s ease !important;
        }
        
        .gradio-chatbot:hover {
            box-shadow: var(--md-elevation-2) !important;
        }
        
        .gradio-chatbot > div:first-child {
            height: 10rem !important;
            max-height: 10rem !important;
        }
        
        .gradio-chatbot .chat-messages,
        .gradio-chatbot [class*="message-container"],
        .gradio-chatbot [class*="chat-history"] {
            max-height: 7.5rem !important;
        }
        
        /* Material Design Example Buttons */
        .gradio-chatbot .examples {
            gap: 8px !important;
            margin-bottom: 12px !important;
            display: flex !important;
            flex-wrap: wrap !important;
        }
        
        .gradio-chatbot .examples button {
            padding: 8px 16px !important;
            font-size: 13px !important;
            border-radius: 8px !important;
            border: 1px solid var(--md-border) !important;
            background: var(--md-surface) !important;
            color: var(--md-on-surface) !important;
            font-weight: 500 !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            height: auto !important;
            min-height: auto !important;
            cursor: pointer !important;
            text-transform: none !important;
            letter-spacing: 0 !important;
        }
        
        .gradio-chatbot .examples button:hover {
            background: var(--md-surface-variant) !important;
            border-color: var(--md-primary) !important;
            color: var(--md-primary) !important;
            transform: translateY(-2px) !important;
            box-shadow: var(--md-elevation-1) !important;
        }
        
        .gradio-chatbot .examples button:active {
            transform: translateY(0) !important;
        }
        
        /* Material Design Input Fields */
        input[type="text"], textarea {
            border: 1px solid var(--md-border) !important;
            border-radius: 8px !important;
            padding: 12px 16px !important;
            font-size: 14px !important;
            height: 48px !important;
            min-height: 48px !important;
            background: var(--md-surface) !important;
            color: var(--md-on-surface) !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        input[type="text"]:focus, textarea:focus {
            outline: none !important;
            border-color: var(--md-primary) !important;
            box-shadow: 0 0 0 3px rgba(0, 112, 243, 0.1) !important;
        }
        
        input[type="text"]::placeholder, textarea::placeholder {
            color: var(--md-on-surface-variant) !important;
            opacity: 0.6 !important;
        }
        
        /* Material Design Buttons */
        button.primary,
        .gradio-button.primary {
            background: var(--md-primary) !important;
            color: white !important;
            font-weight: 500 !important;
            padding: 12px 24px !important;
            border-radius: 8px !important;
            font-size: 14px !important;
            height: 48px !important;
            min-height: 48px !important;
            border: none !important;
            text-transform: none !important;
            letter-spacing: 0 !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: var(--md-elevation-1) !important;
            cursor: pointer !important;
        }
        
        button.primary:hover,
        .gradio-button.primary:hover {
            background: var(--md-primary-dark) !important;
            transform: translateY(-2px) !important;
            box-shadow: var(--md-elevation-2) !important;
        }
        
        button.primary:active,
        .gradio-button.primary:active {
            transform: translateY(0) !important;
            box-shadow: var(--md-elevation-1) !important;
        }
        
        /* Material Design Tabs */
        .gradio-tabs {
            background: var(--md-surface) !important;
            border: 1px solid var(--md-border) !important;
            border-radius: 12px !important;
            padding: 4px !important;
            box-shadow: var(--md-elevation-1) !important;
            display: flex !important;
            gap: 4px !important;
        }
        
        .gradio-tabs button {
            border-radius: 8px !important;
            padding: 10px 16px !important;
            font-weight: 500 !important;
            font-size: 13px !important;
            height: auto !important;
            min-height: auto !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            color: var(--md-on-surface-variant) !important;
            background: transparent !important;
            border: none !important;
            text-transform: none !important;
            cursor: pointer !important;
        }
        
        .gradio-tabs button:hover {
            background: var(--md-surface-variant) !important;
            color: var(--md-on-surface) !important;
        }
        
        .gradio-tabs button.selected {
            background: var(--md-primary) !important;
            color: white !important;
            box-shadow: var(--md-elevation-1) !important;
        }
        
        /* Material Design Accordion */
        .gradio-accordion {
            border: 1px solid var(--md-border) !important;
            border-radius: 12px !important;
            background: var(--md-surface) !important;
            box-shadow: var(--md-elevation-1) !important;
            overflow: hidden !important;
        }
        
        .gradio-accordion:hover {
            box-shadow: var(--md-elevation-2) !important;
        }
        
        /* Logs */
        #log_panel textarea {
            background: #1f2937 !important;
            color: #4ade80 !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.6875rem !important;
            border: 1px solid #374151 !important;
            border-radius: 0.5rem !important;
            padding: 0.75rem !important;
            height: 400px !important;
            min-height: 400px !important;
            max-height: 400px !important;
            width: 100% !important;
            resize: none !important;
            overflow-y: auto !important;
        }
        
        /* Material Design Cards for Visualizations */
        #plot_panel, #dep_graph_panel, #heatmap_panel, #timeline_panel {
            background: var(--md-surface) !important;
            border: 1px solid var(--md-border) !important;
            border-radius: 12px !important;
            padding: 16px !important;
            box-shadow: var(--md-elevation-1) !important;
            transition: box-shadow 0.3s ease !important;
        }
        
        #plot_panel:hover, #dep_graph_panel:hover, #heatmap_panel:hover, #timeline_panel:hover {
            box-shadow: var(--md-elevation-2) !important;
        }
        
        #plot_panel img, #dep_graph_panel img, #heatmap_panel img, #timeline_panel img {
            border-radius: 8px !important;
            max-width: 100% !important;
            height: auto !important;
        }
        
        /* Scrollbar - Dark Mode */
        ::-webkit-scrollbar { width: 0.375rem; height: 0.375rem; }
        ::-webkit-scrollbar-track { background: #1a1a1a; }
        ::-webkit-scrollbar-thumb { background: #444444; border-radius: 0.25rem; }
        ::-webkit-scrollbar-thumb:hover { background: #555555; }
        
        /* Markdown - Dark Mode */
        .markdown { color: #e5e5e5; line-height: 1.6; }
        .markdown code {
            background: #2a2a2a;
            padding: 0.125rem 0.375rem;
            border-radius: 0.25rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.875em;
            color: #ff6b6b;
        }
        
        /* Description text - Dark Mode */
        .gradio-chatbot .description {
            font-size: 0.75rem !important;
            color: #a0a0a0 !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Dark mode for all Gradio components */
        .gradio-container > div {
            background: var(--md-background) !important;
        }
        
        /* Chat messages dark mode */
        .gradio-chatbot .message {
            background: var(--md-surface) !important;
            color: var(--md-on-surface) !important;
        }
        
        /* Labels dark mode */
        label {
            color: var(--md-on-surface) !important;
        }
        
        /* Markdown content areas */
        .markdown-body, [class*="markdown"] {
            background: var(--md-surface) !important;
            color: var(--md-on-surface) !important;
        }
        
        /* Dead code, migration, refactor, duplicate, postmortem panels */
        #dead_code_display, #migration_display, #refactor_display, 
        #duplicate_display, #postmortem_display {
            background: var(--md-surface) !important;
            color: var(--md-on-surface) !important;
            padding: 16px !important;
            border-radius: 8px !important;
        }
    </style>
    """)

    # 3. Material Design Header (Vercel-style)
    with gr.Row(elem_classes="w-full"):
        gr.HTML("""
        <div style="width: 100%; background: var(--md-surface); border-bottom: 1px solid var(--md-border); padding: 20px 24px; box-shadow: var(--md-elevation-1);">
            <div style="max-width: 1280px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h1 style="font-size: 20px; font-weight: 700; color: var(--md-on-surface); margin-bottom: 4px; letter-spacing: -0.02em;">AutoPilot DevOps</h1>
                    <p style="font-size: 12px; color: var(--md-on-surface-variant); font-weight: 400;">Multi-Agent Code Intelligence & DevOps Automation</p>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <a href="https://google.com" target="_blank" rel="noopener" style="padding: 8px 16px; font-size: 13px; font-weight: 500; color: var(--md-on-surface); background: var(--md-surface-variant); border: 1px solid var(--md-border); border-radius: 8px; cursor: pointer; transition: all 0.2s; text-decoration: none; display: inline-block;">
                        Docs
                    </a>
                    <a href="https://google.com" target="_blank" rel="noopener" style="padding: 8px 16px; font-size: 13px; font-weight: 500; color: white; background: var(--md-primary); border: none; border-radius: 8px; cursor: pointer; transition: all 0.2s; box-shadow: var(--md-elevation-1); text-decoration: none; display: inline-block;">
                        GitHub
                    </a>
                </div>
            </div>
        </div>
        """)

    # 4. Main Content Area - Compact Design
    with gr.Row(elem_classes="max-w-7xl mx-auto px-4 py-4 gap-4"):
        
        # LEFT: Chat Interface
        with gr.Column(scale=3, elem_classes="space-y-3"):
            # Compact Repo Config
            with gr.Accordion("⚙️ Repository Config", open=False, elem_classes="text-xs"):
                with gr.Row():
                    repo_url_input = gr.Textbox(
                        label="GitHub URL",
                        placeholder="owner/repo or full URL",
                        value="",
                        scale=2,
                        container=False
                    )
                    github_token_input = gr.Textbox(
                        label="Token",
                        placeholder="ghp_...",
                        value=os.getenv("GITHUB_TOKEN", ""),
                        type="password",
                        scale=1,
                        container=False
                    )
                repo_status = gr.Markdown("**Status:** Ready", elem_classes="text-xs text-gray-500")
            
            # Chat Interface
            chat_interface = gr.ChatInterface(
                fn=response_generator,
                additional_inputs=[user_session, repo_url_input],
                additional_outputs=[user_session, plot_output, stats_output, dep_graph_output, heatmap_output, 
                                  timeline_output, dead_code_output, migration_output, refactor_output, 
                                  duplicate_output, postmortem_output],
                title="",
                description="Ask about your codebase, logs, or DevOps tasks.",
                examples=[
                    ["Analyze this repository", None],
                    ["Generate architecture docs", None],
                    ["Find tech debt", None],
                    ["Explain logs", None],
                    ["Migrate Flask to FastAPI", None],
                    ["Refactor main_agent.py", None]
                ],
                cache_examples=False  # Disable example caching to avoid tuple serialization issues
            )
        
        # RIGHT: Material Design Dashboard with All Tabs
        with gr.Column(scale=2, elem_classes="space-y-3"):
            with gr.Tabs():
                # Tab 1: Analytics
                with gr.TabItem("📊 Analytics"):
                    gr.HTML("""
                    <div style="margin-bottom: 16px;">
                        <h3 style="font-size: 14px; font-weight: 600; color: var(--md-on-surface); margin-bottom: 12px;">Code Health Metrics</h3>
                    </div>
                    """)
                    stats_output.render()
                    
                    gr.HTML("""
                    <div style="margin-top: 24px; margin-bottom: 16px;">
                        <h3 style="font-size: 14px; font-weight: 600; color: var(--md-on-surface); margin-bottom: 12px;">Complexity Trend</h3>
                    </div>
                    """)
                    plot_output.render()
                
                # Tab 2: Dependency Graph
                with gr.TabItem("🔗 Dependencies"):
                    gr.HTML("""
                    <div style="margin-bottom: 16px;">
                        <h3 style="font-size: 14px; font-weight: 600; color: var(--md-on-surface); margin-bottom: 12px;">Module Dependency Graph</h3>
                        <p style="font-size: 12px; color: var(--md-on-surface-variant);">Visual representation of code dependencies</p>
                    </div>
                    """)
                    dep_graph_output.render()
                
                # Tab 3: Complexity Heatmap
                with gr.TabItem("🔥 Hotspots"):
                    gr.HTML("""
                    <div style="margin-bottom: 16px;">
                        <h3 style="font-size: 14px; font-weight: 600; color: var(--md-on-surface); margin-bottom: 12px;">Code Complexity Heatmap</h3>
                        <p style="font-size: 12px; color: var(--md-on-surface-variant);">High-complexity modules requiring attention</p>
                    </div>
                    """)
                    heatmap_output.render()
                
                # Tab 4: Dead Code
                with gr.TabItem("🧹 Dead Code"):
                    gr.HTML("""
                    <div style="margin-bottom: 16px;">
                        <h3 style="font-size: 14px; font-weight: 600; color: var(--md-on-surface); margin-bottom: 12px;">Unused Code Detection</h3>
                        <p style="font-size: 12px; color: var(--md-on-surface-variant);">Potentially unused functions and imports</p>
                    </div>
                    """)
                    dead_code_output.render()
                
                # Tab 5: Migration
                with gr.TabItem("🔄 Migration"):
                    gr.HTML("""
                    <div style="margin-bottom: 16px;">
                        <h3 style="font-size: 14px; font-weight: 600; color: var(--md-on-surface); margin-bottom: 12px;">Framework Migration Plans</h3>
                        <p style="font-size: 12px; color: var(--md-on-surface-variant);">Migration strategies and breaking changes</p>
                    </div>
                    """)
                    migration_output.render()
                
                # Tab 6: Refactoring
                with gr.TabItem("♻️ Refactoring"):
                    gr.HTML("""
                    <div style="margin-bottom: 16px;">
                        <h3 style="font-size: 14px; font-weight: 600; color: var(--md-on-surface); margin-bottom: 12px;">Refactoring Suggestions</h3>
                        <p style="font-size: 12px; color: var(--md-on-surface-variant);">Code improvement recommendations</p>
                    </div>
                    """)
                    refactor_output.render()
                
                # Tab 7: Timeline
                with gr.TabItem("📈 Timeline"):
                    gr.HTML("""
                    <div style="margin-bottom: 16px;">
                        <h3 style="font-size: 14px; font-weight: 600; color: var(--md-on-surface); margin-bottom: 12px;">Error & Warning Timeline</h3>
                        <p style="font-size: 12px; color: var(--md-on-surface-variant);">Temporal analysis of log events</p>
                    </div>
                    """)
                    timeline_output.render()
                
                # Tab 7.5: Postmortem
                with gr.TabItem("📝 Postmortem"):
                    gr.HTML("""
                    <div style="margin-bottom: 16px;">
                        <h3 style="font-size: 14px; font-weight: 600; color: var(--md-on-surface); margin-bottom: 12px;">Incident Postmortem</h3>
                        <p style="font-size: 12px; color: var(--md-on-surface-variant);">Structured incident analysis and recommendations</p>
                    </div>
                    """)
                    postmortem_output.render()
                
                # Tab 8: Logs
                with gr.TabItem("📋 Logs"):
                    logs_display = gr.TextArea(
                        elem_id="log_panel", 
                        interactive=False, 
                        lines=20, 
                        label="",
                        value="System initializing...",
                        show_label=False,
                        container=False
                    )
                
                # Tab 9: Settings
                with gr.TabItem("⚙️ Settings"):
                    gr.HTML("""
                    <div style="margin-bottom: 16px;">
                        <h3 style="font-size: 14px; font-weight: 600; color: var(--md-on-surface); margin-bottom: 12px;">GitHub Integration</h3>
                    </div>
                    """)
                    settings_token = gr.Textbox(
                        label="",
                        placeholder="ghp_xxxxxxxxxxxx",
                        value=os.getenv("GITHUB_TOKEN", ""),
                        type="password",
                        container=False
                    )
                    save_token_btn = gr.Button("Save Token", variant="primary")
                    token_status = gr.Markdown(
                        "Token stored in session only.",
                        elem_classes="text-xs"
                    )
                    
                    def save_token(token):
                        if token:
                            os.environ["GITHUB_TOKEN"] = token
                            from project.config import Config
                            Config.GITHUB_TOKEN = token
                            return "✅ Token saved (session only)"
                        return "⚠️ No token provided"
                    
                    save_token_btn.click(
                        fn=save_token,
                        inputs=[settings_token],
                        outputs=[token_status]
                    )

    # 5. Compact Footer
    with gr.Row(elem_classes="w-full mt-4"):
        gr.HTML("""
        <div class="w-full bg-white border-t border-gray-200 py-3 px-6">
            <div class="max-w-7xl mx-auto flex items-center justify-between">
                <div class="text-xs text-gray-500">
                    <span class="font-medium text-gray-700">AutoPilot DevOps</span> v2.0 • Read-only analysis
                </div>
                <a href="https://github.com" target="_blank" rel="noopener" 
                   class="w-7 h-7 rounded-md bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" class="text-gray-600">
                        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                    </svg>
                </a>
            </div>
        </div>
        """)

    
    # Auto-Refresh Timer for Logs
    timer = gr.Timer(value=2)
    timer.tick(get_live_logs, None, logs_display)

# --- 5. LAUNCH ---
if __name__ == "__main__":
    is_spaces = "SPACE_ID" in os.environ
    
    print("--- AutoPilot DevOps Launching ---")
    if is_spaces:
        demo.queue().launch(server_name="0.0.0.0", server_port=7860)
    else:
        demo.queue().launch(server_name="127.0.0.1", server_port=7860, share=False)
