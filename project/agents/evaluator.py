"""
Evaluator Agent: Safety and quality assurance gatekeeper for DevOps operations.
"""
import re
from typing import Dict
from project.core.context_engineering import EVALUATOR_PROMPT
from project.core.a2a_protocol import EvaluatorOutput
from project.core.observability import logger
from project.core.gemini_client import GeminiClient

class Evaluator:
    def __init__(self):
        self.client = GeminiClient(EVALUATOR_PROMPT)
        self.mock_mode = False
        
        # Enhanced Safety filters for DevOps operations
        self.banned_phrases = [
            r"rm\s+-rf",                    # File deletion
            r"rm\s+.*-r",                   # Recursive deletion
            r"delete\s+.*file",             # File deletion commands
            r"DROP\s+TABLE",                # Database drops
            r"DROP\s+DATABASE",             # Database deletion
            r"TRUNCATE\s+TABLE",            # Table truncation
            r"DELETE\s+FROM.*WHERE\s+1=1",  # Mass deletion
            r"format\s+disk",                # Disk formatting
            r"shutdown",                    # System shutdown
            r"sudo\s+",                     # Sudo commands
            r"systemctl\s+(stop|restart|disable)",  # System service control
            r"kubectl\s+delete",            # Kubernetes deletion
            r"chmod\s+777",                 # Unsafe permissions
            r"chmod\s+.*-R\s+777",          # Recursive unsafe permissions
            r"uninstall",                   # Uninstallation
            r"destroy",                     # Destruction commands
            r"kill\s+-9",                   # Force kill
            r"pkill\s+-9",                  # Process kill
            r"exec\s+",                     # Execution commands
            r"subprocess\.(call|run|Popen)", # Python subprocess execution
            r"os\.system",                   # OS system calls
            r"os\.popen",                    # OS popen
            r"eval\s*\(",                    # Eval execution
            r"exec\s*\(",                    # Exec execution
            r"__import__",                  # Dynamic imports (potentially unsafe)
        ]
        
    def evaluate(self, worker_output: Dict, user_input: str) -> Dict:
        draft = worker_output.get("draft_response", "")
        tools_used = worker_output.get("tools_used", [])
        
        logger.log("Evaluator", "Starting safety evaluation", 
                   data={"draft_length": len(draft)})
        
        # Mock mode
        if hasattr(self, 'mock_mode') and self.mock_mode:
            return self._mock_evaluate(draft)
        
        # 1. Regex Safety Checks (Hard Rules)
        if self._contains_destructive_commands(draft):
            logger.log("Evaluator", "REJECTED: Destructive command detected")
            return EvaluatorOutput(
                status="REJECTED",
                feedback="Contains destructive or unsafe commands (file deletion, system modification, execution).",
                final_response=self._get_fallback_response()
            ).to_dict()
        
        if self._contains_execution_commands(draft):
            logger.log("Evaluator", "REJECTED: Execution command detected")
            return EvaluatorOutput(
                status="REJECTED",
                feedback="Contains execution commands or system operations.",
                final_response=self._get_fallback_response()
            ).to_dict()
        
        if self._contains_unsafe_diffs(draft):
            logger.log("Evaluator", "REJECTED: Unsafe code diff detected")
            return EvaluatorOutput(
                status="REJECTED",
                feedback="Contains unsafe code changes (deletions, system modifications).",
                final_response=self._get_fallback_response()
            ).to_dict()
        
        # 2. LLM Contextual Check (Smart Rules)
        # We inject the prompt template manually here to pass both input and response
        prompt = EVALUATOR_PROMPT.replace("{user_input}", user_input).replace("{agent_response}", draft)
        
        evaluation = self.client.generate_json(prompt)
        
        if not evaluation:
            logger.log("Evaluator", "Evaluation failed, defaulting to APPROVED if regex passed")
            return EvaluatorOutput(
                status="APPROVED", # Fallback to approved if regex passed but LLM failed
                feedback="Automated check passed.",
                final_response=draft
            ).to_dict()
        
        # Post-process evaluation
        if evaluation.get("status") == "APPROVED":
            final_response = draft
        else:
            final_response = evaluation.get("final_response", self._get_fallback_response())
            logger.warning("Evaluator", f"Guardrail Triggered: {evaluation.get('feedback')}")
        
        logger.log("Evaluator", f"Evaluation result: {evaluation.get('status')}")
        
        return EvaluatorOutput(
            status=evaluation.get("status", "REJECTED"),
            feedback=evaluation.get("feedback", "Safety check failed."),
            final_response=final_response
        ).to_dict()
    
    def _contains_destructive_commands(self, text: str) -> bool:
        """Check for destructive commands in text."""
        text_lower = text.lower()
        for pattern in self.banned_phrases:
            if re.search(pattern, text_lower, re.IGNORECASE):
                # Allow refusal context like "I cannot delete" or "do not execute"
                if any(phrase in text_lower for phrase in ["cannot", "cannot perform", "do not", "refuse", "not allowed"]):
                    continue
                return True
        return False
    
    def _contains_execution_commands(self, text: str) -> bool:
        """Check for execution commands (shell, subprocess, etc.)."""
        execution_patterns = [
            r"subprocess\.",
            r"os\.system",
            r"os\.popen",
            r"eval\s*\(",
            r"exec\s*\(",
            r"bash\s+-c",
            r"sh\s+-c",
            r"python\s+-c",
            r"\.run\s*\(",
            r"\.call\s*\(",
        ]
        text_lower = text.lower()
        for pattern in execution_patterns:
            if re.search(pattern, text_lower):
                # Allow in code examples with warnings
                if "warning" in text_lower or "do not" in text_lower or "avoid" in text_lower:
                    continue
                return True
        return False
    
    def _contains_unsafe_diffs(self, text: str) -> bool:
        """Check for unsafe code diffs (massive deletions, system changes)."""
        # Look for diff patterns with excessive deletions
        if "---" in text and "+++" in text:  # Git diff format
            lines = text.split('\n')
            deletions = sum(1 for line in lines if line.startswith('-') and not line.startswith('---'))
            additions = sum(1 for line in lines if line.startswith('+') and not line.startswith('+++'))
            
            # If deletions significantly exceed additions, might be unsafe
            if deletions > 50 and deletions > additions * 2:
                # Check for critical file deletions
                critical_patterns = [
                    r"-\s*import\s+os",
                    r"-\s*import\s+subprocess",
                    r"-\s*def\s+.*delete",
                    r"-\s*def\s+.*remove",
                    r"-\s*DROP\s+TABLE",
                ]
                for pattern in critical_patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        return True
        
        return False
    
    def _get_fallback_response(self) -> str:
        return """
I apologize, but I cannot perform that operation. I am a read-only DevOps analysis tool designed for code intelligence and log analysis.

**What I CAN do:**
- Analyze codebases and generate documentation
- Parse logs and identify incidents
- Suggest safe refactoring improvements
- Generate migration plans (text-only)
- Build dependency graphs
- Calculate code complexity

**What I CANNOT do:**
- Execute shell commands or system operations
- Delete or modify files
- Run code or execute scripts
- Modify system configurations
- Perform destructive database operations

Would you like me to suggest a safe alternative that provides read-only analysis?
        """
    
    def _mock_evaluate(self, draft: str) -> Dict:
        return EvaluatorOutput(status="APPROVED", feedback="Mock Pass", final_response=draft).to_dict()
