import subprocess
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler #to automatically see the changes in tkinter after ctrl s

# -----------------------
# FILE WATCHER
# -----------------------
class RestartHandler(FileSystemEventHandler):

    def __init__(self):
        self.process = None
        self.last_restart = 0 # For delay save  
        self.restart()

    # -----------------------
    # RESTART APP ON SAVE
    # -----------------------
    def restart(self):
        if self.process:
            self.process.kill()
            print("🔄 Restarting...")

        # launch ui.py directly (bypass login for faster dev)
        self.process = subprocess.Popen(
            [sys.executable, "src/menu.py"]
        )

    def on_modified(self, event):
        # only watch .py files
        if not event.src_path.endswith(".py"):
            return    
        
        # cooldown — ignore if restarted less than 1 second ago
        now = time.time()
        if now - self.last_restart < 1.0:
            return 
        
        self.last_restart = now  
        print(f"📝 Change detected: {event.src_path}")
        self.restart()

# -----------------------
# START WATCHER
# -----------------------
if __name__ == "__main__":
    print("👀 Watching for file changes...")
    print("📂 Edit any .py file and the UI will auto-restart")
    print("🛑 Press Ctrl+C to stop\n")

    handler = RestartHandler()
    observer = Observer()

    # watch the src folder
    observer.schedule(handler, path="src/", recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if handler.process:
            handler.process.kill()

    observer.join()