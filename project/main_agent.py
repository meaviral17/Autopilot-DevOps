"""
Main Agent: Orchestrator for the multi-agent pipeline.
"""
import re
from project.agents.planner import Planner
from project.agents.worker import Worker
from project.agents.evaluator import Evaluator
from project.memory.session_memory import SessionMemory
from project.memory.long_term_memory import LongTermMemory # NEW IMPORT
from project.tools.github_tools import GitHubTools
from project.core.observability import logger
from project.config import Config
from typing import Dict, Optional

class MainAgent:
    def __init__(self, mock_mode: bool = None):
        # Initialize components
        self.planner = Planner()
        self.worker = Worker()
        self.evaluator = Evaluator()
        self.memory = SessionMemory(max_history=8)
        self.long_term_memory = LongTermMemory() # NEW COMPONENT
        
        # Set mock mode
        self.mock_mode = mock_mode if mock_mode is not None else Config.MOCK_MODE
        self.planner.mock_mode = self.mock_mode
        self.worker.mock_mode = self.mock_mode
        self.evaluator.mock_mode = self.mock_mode
        
        logger.log("MainAgent", f"Initialized in {'MOCK' if self.mock_mode else 'LIVE'} mode")
    
    def handle_message(self, user_input: str, repo_url: Optional[str] = None) -> Dict:
        """Process a single user message through the pipeline.
        
        Args:
            user_input: User's message/request
            repo_url: Optional GitHub repository URL to analyze
        """
        logger.log("System", "Processing new message", 
                   data={"input_preview": user_input[:50] + "...", "repo_url": repo_url})
        
        try:
            # 0. Handle GitHub repository cloning if URL provided or detected
            repo_path = "."
            if repo_url:
                clone_result = GitHubTools.clone_repository(
                    repo_url, 
                    github_token=Config.GITHUB_TOKEN
                )
                if clone_result.get("success"):
                    repo_path = clone_result["local_path"]
                    logger.log("MainAgent", f"Cloned repository to: {repo_path}")
                else:
                    error_msg = clone_result.get("error", "Unknown error")
                    logger.log("MainAgent", f"Failed to clone repository: {error_msg}", level="WARNING")
                    # Continue with current directory if clone fails
            else:
                # Try to detect GitHub URL in user input
                github_url = self._extract_github_url(user_input)
                if github_url:
                    clone_result = GitHubTools.clone_repository(
                        github_url,
                        github_token=Config.GITHUB_TOKEN
                    )
                    if clone_result.get("success"):
                        repo_path = clone_result["local_path"]
                        logger.log("MainAgent", f"Detected and cloned repository: {github_url}")
                        user_input = user_input.replace(github_url, "").strip()  # Remove URL from input
                    else:
                        logger.log("MainAgent", f"Failed to clone detected repository: {clone_result.get('error')}", level="WARNING")
            
            # 1. Update Memory
            self.memory.add_message("user", user_input)
            history_str = self.memory.get_history_string()
            
            # 2. Get Long Term Context
            lt_memory_str = self.long_term_memory.get_preferences_string()
            
            # 3. Planner (Analyze Input + History + Long Term Memory)
            plan = self.planner.plan(user_input, history_str, lt_memory_str)
            
            # 3c. Add repository path to plan
            plan["repo_path"] = repo_path
            
            # 3a. Save Preferences if detected
            save_pref = plan.get("save_preference")
            if save_pref and isinstance(save_pref, dict):
                key = save_pref.get("key")
                value = save_pref.get("value")
                if key and value:
                    self.long_term_memory.update_preference(key, value)
                    logger.log("MainAgent", f"Saved User Preference: {key}={value}")
            
            # 3b. Store repo analysis results if this was a repo analysis
            if plan.get("action") == "repo_analysis":
                # Extract analysis summary from worker results later if available
                pass
            
            # 4. Worker (Execute Plan)
            worker_res = self.worker.work(plan)
            
            # 5. Extract visualization data from worker (stored in _last_analysis_results)
            visualizations = {}
            if hasattr(self.worker, '_last_analysis_results'):
                analysis_results = getattr(self.worker, '_last_analysis_results', {})
                # Extract visualizations from the nested structure
                if isinstance(analysis_results, dict):
                    # Visualizations are stored in analysis_results["visualizations"]
                    visualizations = analysis_results.get("visualizations", {})
                    # Also check if visualizations are at the top level (for backward compatibility)
                    if not visualizations:
                        # Check for direct visualization keys
                        for key in ["dependency_graph_image", "complexity_heatmap"]:
                            if key in analysis_results:
                                if not visualizations:
                                    visualizations = {}
                                visualizations[key] = analysis_results[key]
                
                # Debug: Log what visualizations are available
                logger.log("MainAgent", f"Extracted visualizations: {list(visualizations.keys())}", level="INFO")
                if "dependency_graph_image" in visualizations:
                    img = visualizations["dependency_graph_image"]
                    logger.log("MainAgent", f"Dependency graph image type: {type(img)}, has save: {hasattr(img, 'save')}", level="INFO")
                if "complexity_heatmap" in visualizations:
                    img = visualizations["complexity_heatmap"]
                    logger.log("MainAgent", f"Complexity heatmap image type: {type(img)}, has save: {hasattr(img, 'save')}", level="INFO")
                if "error_timeline" in visualizations:
                    img = visualizations["error_timeline"]
                    logger.log("MainAgent", f"Error timeline image type: {type(img)}, has save: {hasattr(img, 'save')}", level="INFO")
                else:
                    # Check for timeline in nested structures in analysis_results
                    logger.log("MainAgent", f"Timeline not in visualizations, searching analysis_results. Keys: {list(analysis_results.keys())[:10]}", level="INFO")
                    for key, value in list(analysis_results.items()):
                        if "_timeline" in key and hasattr(value, 'save'):
                            if not visualizations:
                                visualizations = {}
                            visualizations["error_timeline"] = value
                            logger.log("MainAgent", f"Found timeline in analysis_results: {key}", level="INFO")
                            break
                        elif isinstance(value, dict):
                            # Check nested dicts (like log file results)
                            for sub_key, sub_value in value.items():
                                if "_timeline" in sub_key and hasattr(sub_value, 'save'):
                                    if not visualizations:
                                        visualizations = {}
                                    visualizations["error_timeline"] = sub_value
                                    logger.log("MainAgent", f"Found timeline in nested structure: {key}.{sub_key}", level="INFO")
                                    break
            
            # 6. Evaluator (Check Output vs Input)
            eval_res = self.evaluator.evaluate(worker_res, user_input)
            
            final_response = eval_res.get("final_response")
            
            # 7. Update Memory
            self.memory.add_message("assistant", final_response)
            
            # 7. Extract reports from analysis_results (dead_code, migration_plan, etc.)
            dead_code_report = {}
            migration_plan_report = {}
            refactor_suggestions_report = []
            duplicate_code_report = {}
            postmortem_report = {}
            
            if hasattr(self.worker, '_last_analysis_results'):
                analysis_results = getattr(self.worker, '_last_analysis_results', {})
                if isinstance(analysis_results, dict):
                    # Extract reports from top level
                    dead_code_report = analysis_results.get("dead_code", {})
                    migration_plan_report = analysis_results.get("migration_plan", {})
                    refactor_suggestions_report = analysis_results.get("refactor_suggestions", [])
                    duplicate_code_report = analysis_results.get("duplicates", {})
                    
                    # Postmortem might be in nested log file results
                    for key, value in analysis_results.items():
                        if isinstance(value, dict) and "postmortem" in value:
                            postmortem_report = value.get("postmortem", {})
                            break
            
            # 8. Compile results
            return {
                "response": final_response,
                "plan": plan,
                "tools_used": worker_res.get("tools_used", []),
                "safety_status": eval_res.get("status"),
                "conversation_stats": self.memory.get_stats(),
                "logs": logger.get_logs(),
                "visualizations": visualizations,  # Include visualizations
                "dead_code_report": dead_code_report,
                "migration_plan_report": migration_plan_report,
                "refactor_suggestions_report": refactor_suggestions_report,
                "duplicate_code_report": duplicate_code_report,
                "postmortem_report": postmortem_report
            }
            
        except Exception as e:
            logger.log("MainAgent", f"Pipeline error: {e}")
            error_response = "I apologize, but I'm experiencing technical difficulties. Please try again later."
            self.memory.add_message("assistant", error_response)
            
            return {
                "response": error_response,
                "plan": {"emotion": "error", "risk_level": "LOW", "action": "general_chat", "task_type": "general_chat"},
                "tools_used": [],
                "safety_status": "REJECTED",
                "conversation_stats": self.memory.get_stats(),
                "logs": logger.get_logs()
            }
    
    def get_conversation_summary(self) -> str:
        return self.memory.get_conversation_summary()
    
    def clear_memory(self):
        self.memory.clear()
        logger.log("MainAgent", "Conversation memory cleared")
    
    def _extract_github_url(self, text: str) -> Optional[str]:
        """Extract GitHub repository URL from text.
        
        Args:
            text: Text to search for GitHub URLs
            
        Returns:
            GitHub URL if found, None otherwise
        """
        # Patterns for GitHub URLs
        patterns = [
            r'https://github\.com/[^\s/]+/[^\s/]+',
            r'git@github\.com:[^\s/]+/[^\s/]+',
            r'github\.com/[^\s/]+/[^\s/]+',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                url = match.group(0)
                # Normalize to full URL
                if not url.startswith('http'):
                    url = 'https://' + url
                return url
        
        # Check for owner/repo format
        owner_repo_pattern = r'\b([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)\b'
        match = re.search(owner_repo_pattern, text)
        if match and 'github' in text.lower():
            owner, repo = match.groups()
            return f"https://github.com/{owner}/{repo}"
        
        return None