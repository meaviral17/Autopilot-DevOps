"""
Planner Agent: Analyzes DevOps requests and creates actionable plans.
"""
import json
import re
from typing import Dict, Optional
from project.core.context_engineering import PLANNER_PROMPT
from project.core.a2a_protocol import PlannerOutput
from project.core.observability import logger
from project.core.gemini_client import GeminiClient

class Planner:
    def __init__(self):
        self.client = GeminiClient(PLANNER_PROMPT)
        self.mock_mode = False 
        
    def _check_destructive_request(self, text: str) -> bool:
        """Heuristic check for destructive operation requests."""
        patterns = [
            r"rm\s+-rf",
            r"delete\s+.*file",
            r"drop\s+table",
            r"format\s+disk",
            r"shutdown",
            r"sudo\s+",
            r"systemctl\s+(stop|restart|disable)",
            r"kubectl\s+delete",
            r"chmod\s+777",
            r"remove\s+.*directory",
            r"uninstall",
            r"destroy"
        ]
        text_lower = text.lower()
        return any(re.search(p, text_lower) for p in patterns)

    def plan(self, user_input: str, history_str: str, memory_str: str = "") -> Dict:
        logger.log("Planner", "Analyzing DevOps request...", 
                   data={"input_length": len(user_input)})
        
        # 1. HARD RULE: Destructive Operation Pre-check
        if self._check_destructive_request(user_input):
            logger.log("Planner", "⚠️ DESTRUCTIVE OPERATION DETECTED")
            return PlannerOutput(
                emotion="alert",  # Keep for compatibility
                risk_level="HIGH",
                distress_score=10,  # Keep for compatibility
                action="enforce_boundary",
                instruction="User requested destructive operation. Firmly state that you are a read-only analysis tool and cannot perform file deletions, system modifications, or execute commands. Suggest safe read-only alternatives.",
                technique_suggestion="none",  # Keep for compatibility
                needs_validation=True,
                save_preference=None
            ).to_dict()

        # Mock mode
        if hasattr(self, 'mock_mode') and self.mock_mode:
            return self._mock_plan(user_input)
        
        # Prepare prompt with context
        prompt = f"""
        Analyze this DevOps request and provide a structured plan.
        
        USER PREFERENCES/CONTEXT:
        {memory_str}
        
        CONVERSATION HISTORY:
        {history_str}
        
        CURRENT USER REQUEST:
        {user_input}
        
        Remember: 
        1. Output ONLY valid JSON.
        2. Map request to appropriate task_type and action.
        3. Identify required tools and target paths.
        """
        
        response_data = self.client.generate_json(prompt)
        
        if not response_data:
            logger.log("Planner", "Failed to get valid response, using fallback")
            return PlannerOutput(
                emotion="unknown",  # Keep for compatibility
                risk_level="LOW",
                distress_score=5,  # Keep for compatibility
                action="general_chat",
                instruction="Respond to the user's DevOps request.",
                technique_suggestion="none",  # Keep for compatibility
                needs_validation=True,
                save_preference=None
            ).to_dict()
        
        # Map new task_type to legacy fields for compatibility
        task_type = response_data.get("task_type", "general_chat")
        action = response_data.get("action", task_type)
        
        # Convert to legacy format while preserving new fields
        legacy_output = {
            "emotion": response_data.get("emotion", "neutral"),  # Keep for UI compatibility
            "risk_level": response_data.get("complexity", "LOW"),  # Map complexity to risk_level
            "distress_score": 5 if response_data.get("complexity") == "HIGH" else 3,  # Map complexity
            "action": action,
            "instruction": response_data.get("instruction", ""),
            "technique_suggestion": "none",  # Keep for compatibility
            "needs_validation": response_data.get("needs_validation", True),
            "save_preference": response_data.get("save_preference"),
            # New DevOps-specific fields
            "task_type": task_type,
            "complexity": response_data.get("complexity", "LOW"),
            "tools_needed": response_data.get("tools_needed", []),
            "target_paths": response_data.get("target_paths", [])
        }
        
        logger.log("Planner", "Analysis complete", data=legacy_output)
        return legacy_output
    
    def _mock_plan(self, user_input: str) -> Dict:
        """Mock planning logic for DevOps requests."""
        user_lower = user_input.lower()
        
        if "analyze" in user_lower and ("repo" in user_lower or "codebase" in user_lower):
            return PlannerOutput(
                emotion="neutral",
                risk_level="LOW",
                distress_score=3,
                action="repo_analysis",
                instruction="Analyze repository structure, dependencies, and complexity.",
                technique_suggestion="none",
                needs_validation=True,
                save_preference=None
            ).to_dict()
        
        if "log" in user_lower or "incident" in user_lower or "error" in user_lower:
            return PlannerOutput(
                emotion="alert",
                risk_level="MEDIUM",
                distress_score=7,
                action="incident_analysis",
                instruction="Parse logs, cluster errors, and identify root causes.",
                technique_suggestion="none",
                needs_validation=True,
                save_preference=None
            ).to_dict()
        
        if "migrate" in user_lower or "migration" in user_lower:
            return PlannerOutput(
                emotion="neutral",
                risk_level="MEDIUM",
                distress_score=5,
                action="migration",
                instruction="Generate migration plan and code transformation suggestions.",
                technique_suggestion="none",
                needs_validation=True,
                save_preference=None
            ).to_dict()
        
        if "refactor" in user_lower:
            return PlannerOutput(
                emotion="neutral",
                risk_level="LOW",
                distress_score=4,
                action="refactor",
                instruction="Analyze code and suggest refactoring improvements.",
                technique_suggestion="none",
                needs_validation=True,
                save_preference=None
            ).to_dict()
        
        if "doc" in user_lower or "documentation" in user_lower:
            return PlannerOutput(
                emotion="neutral",
                risk_level="LOW",
                distress_score=2,
                action="documentation",
                instruction="Generate comprehensive markdown documentation.",
                technique_suggestion="none",
                needs_validation=True,
                save_preference=None
            ).to_dict()
        
        return PlannerOutput(
            emotion="neutral",
            risk_level="LOW",
            distress_score=3,
            action="general_chat",
            instruction="Respond to the DevOps request.",
            technique_suggestion="none",
            needs_validation=True,
            save_preference=None
        ).to_dict()
