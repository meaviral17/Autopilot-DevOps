"""
Manages short-term conversation history with safety limits.
"""

class SessionMemory:
    def __init__(self, max_history: int = 10):
        self.history = []  # List of {"role": "user/assistant", "content": "...", "timestamp": float}
        self.max_history = max_history
    
    def add_message(self, role: str, content: str):
        """Add message to history with timestamp."""
        import time
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
        
        # Maintain history limit
        if len(self.history) > self.max_history * 2:  # *2 for user+assistant pairs
            self.history = self.history[-self.max_history * 2:]
    
    def get_history_string(self, last_n: int = 5) -> str:
        """
        Returns formatted history for LLM context.
        Includes only last N exchanges to stay within token limits.
        """
        recent = self.history[-last_n * 2:]  # N exchanges = 2N messages
        
        if not recent:
            return "No prior conversation."
        
        formatted = []
        for msg in recent:
            role = msg["role"].upper()
            content = msg["content"]
            # Truncate very long messages
            if len(content) > 200:
                content = content[:200] + "..."
            formatted.append(f"{role}: {content}")
        
        return "\n".join(formatted)
    
    def get_conversation_summary(self) -> str:
        """Get brief summary of conversation flow."""
        if not self.history:
            return "New conversation"
        
        user_msgs = [m for m in self.history if m["role"] == "user"]
        return f"{len(user_msgs)} messages exchanged"
    
    def clear(self):
        """Clear all history."""
        self.history = []
    
    def get_stats(self) -> dict:
        """Get conversation statistics."""
        return {
            "total_messages": len(self.history),
            "user_messages": len([m for m in self.history if m["role"] == "user"]),
            "assistant_messages": len([m for m in self.history if m["role"] == "assistant"])
        }