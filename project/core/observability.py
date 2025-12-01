"""
Enhanced observability module for logging agent activities.
Supports console output, log levels, and optional file logging.
"""

import datetime
import threading
from typing import Optional, Any, Dict
import json

class Logger:
    def __init__(self, log_to_file: bool = False, log_file: str = "agent_logs.txt"):
        self.logs = []
        self.log_to_file = log_to_file
        self.log_file = log_file
        self._lock = threading.Lock()  # Thread safety
        self._setup_file_logging()
    
    def _setup_file_logging(self):
        """Initialize log file if enabled."""
        if self.log_to_file:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"=== Mental Health Companion Logs ===\n")
                f.write(f"Started: {datetime.datetime.now().isoformat()}\n\n")
    
    def log(self, agent_name: str, message: str, data: Optional[Any] = None, level: str = "INFO"):
        """
        Log an event with timestamp, agent name, message, and optional data.
        
        Args:
            agent_name: Name of the agent/component logging
            message: Main log message
            data: Optional additional data (will be JSON-serialized)
            level: Log level (INFO, WARNING, ERROR, DEBUG)
        """
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Format log entry
        entry = f"[{timestamp}] {level:<5} {agent_name}: {message}"
        
        # Add data if provided
        if data is not None:
            try:
                # Serialize data nicely
                if isinstance(data, dict):
                    data_str = json.dumps(data, indent=2)
                else:
                    data_str = str(data)
                entry += f"\n{' '*20} Data: {data_str}"
            except Exception:
                entry += f"\n{' '*20} Data: {str(data)}"
        
        # Thread-safe logging
        with self._lock:
            # Print to console (always)
            print(entry)
            
            # Store in memory
            self.logs.append(entry)
            
            # Write to file if enabled
            if self.log_to_file:
                try:
                    with open(self.log_file, 'a', encoding='utf-8') as f:
                        f.write(entry + "\n")
                except Exception as e:
                    print(f"[{timestamp}] ERROR Logger: Failed to write to log file: {e}")
    
    def info(self, agent_name: str, message: str, data: Optional[Any] = None):
        """Convenience method for INFO level logs."""
        self.log(agent_name, message, data, level="INFO")
    
    def error(self, agent_name: str, message: str, data: Optional[Any] = None):
        """Convenience method for ERROR level logs."""
        self.log(agent_name, message, data, level="ERROR")
    
    def warning(self, agent_name: str, message: str, data: Optional[Any] = None):
        """Convenience method for WARNING level logs."""
        self.log(agent_name, message, data, level="WARNING")
    
    def debug(self, agent_name: str, message: str, data: Optional[Any] = None):
        """Convenience method for DEBUG level logs."""
        self.log(agent_name, message, data, level="DEBUG")
    
    def get_logs(self, last_n: Optional[int] = None) -> str:
        """
        Get all logs or last N logs as a formatted string.
        
        Args:
            last_n: Number of recent logs to return (None for all)
        """
        with self._lock:
            if last_n:
                logs_to_return = self.logs[-last_n:]
            else:
                logs_to_return = self.logs
            
            return "\n".join(logs_to_return)
    
    def clear(self):
        """Clear all logs from memory."""
        with self._lock:
            self.logs.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """Get logging statistics."""
        with self._lock:
            return {
                "total_logs": len(self.logs),
                "by_level": {
                    "INFO": sum(1 for log in self.logs if " INFO " in log),
                    "ERROR": sum(1 for log in self.logs if " ERROR " in log),
                    "WARNING": sum(1 for log in self.logs if " WARNING " in log),
                    "DEBUG": sum(1 for log in self.logs if " DEBUG " in log)
                }
            }

# Singleton instance for global use
logger = Logger(log_to_file=False)