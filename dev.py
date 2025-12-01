"""
Auto-reload development server for AutoPilot DevOps.
Watches for file changes and automatically restarts the application.
Similar to nodemon for Node.js.
"""
import os
import sys
import time
import signal
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class AppReloadHandler(FileSystemEventHandler):
    """Handles file system events and restarts the app on changes."""
    
    def __init__(self, script_path="app.py"):
        self.script_path = script_path
        self.process = None
        self.last_restart = 0
        self.restart_delay = 1.0  # Prevent rapid restarts
        self.ignored_patterns = [
            '__pycache__',
            '.pyc',
            '.pyo',
            '.pyd',
            '.log',
            '.git',
            'directory_structure.json',
            'devops_preferences.json',
            'autopilot_devops.log'
        ]
        self.start_app()
    
    def should_ignore(self, file_path):
        """Check if file should be ignored."""
        path_str = str(file_path).lower()
        return any(pattern in path_str for pattern in self.ignored_patterns)
    
    def start_app(self):
        """Start the application."""
        if self.process:
            try:
                # Kill existing process
                if sys.platform == "win32":
                    self.process.terminate()
                    time.sleep(0.5)
                    if self.process.poll() is None:
                        self.process.kill()
                else:
                    os.kill(self.process.pid, signal.SIGTERM)
                    try:
                        self.process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        os.kill(self.process.pid, signal.SIGKILL)
                print("\n🛑 Stopped previous instance")
            except Exception as e:
                print(f"⚠️  Error stopping process: {e}")
        
        print(f"\n🚀 Starting {self.script_path}...")
        print("=" * 60)
        
        try:
            self.process = subprocess.Popen(
                [sys.executable, self.script_path],
                stdout=sys.stdout,
                stderr=sys.stderr,
                cwd=os.getcwd()
            )
            self.last_restart = time.time()
        except Exception as e:
            print(f"❌ Error starting app: {e}")
            sys.exit(1)
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        if self.should_ignore(event.src_path):
            return
        
        # Prevent rapid restarts
        if time.time() - self.last_restart < self.restart_delay:
            return
        
        file_path = Path(event.src_path)
        if file_path.suffix in ['.py', '.txt', '.md', '.json', '.env']:
            print(f"\n📝 Detected change: {file_path.name}")
            self.start_app()
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        if self.should_ignore(event.src_path):
            return
        
        file_path = Path(event.src_path)
        if file_path.suffix in ['.py', '.txt', '.md', '.json', '.env']:
            print(f"\n➕ New file detected: {file_path.name}")
            self.start_app()

def main():
    """Main function to start the file watcher."""
    script_path = "app.py"
    
    if not os.path.exists(script_path):
        print(f"❌ Error: {script_path} not found!")
        sys.exit(1)
    
    print("=" * 60)
    print("🔄 Auto-Reload Development Server")
    print("=" * 60)
    print(f"📁 Watching: {os.getcwd()}")
    print(f"📄 Script: {script_path}")
    print(f"🐍 Python: {sys.executable}")
    print("=" * 60)
    print("💡 Press Ctrl+C to stop")
    print("=" * 60)
    
    # Create event handler
    event_handler = AppReloadHandler(script_path)
    
    # Create observer
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
            # Check if process is still running
            if event_handler.process and event_handler.process.poll() is not None:
                print("\n⚠️  Process exited unexpectedly. Restarting...")
                event_handler.start_app()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        observer.stop()
        if event_handler.process:
            try:
                if sys.platform == "win32":
                    event_handler.process.terminate()
                    event_handler.process.wait(timeout=3)
                else:
                    os.kill(event_handler.process.pid, signal.SIGTERM)
                    event_handler.process.wait(timeout=3)
            except:
                if sys.platform == "win32":
                    event_handler.process.kill()
                else:
                    os.kill(event_handler.process.pid, signal.SIGKILL)
        observer.join()
        print("✅ Stopped")

if __name__ == "__main__":
    main()

