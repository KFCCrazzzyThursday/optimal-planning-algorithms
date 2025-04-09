import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class BackgroundOpenNew(FileSystemEventHandler):
    """Opens newly created images"""
    def on_created(self, event):
        print(event.src_path)
        os.system(f'sleep 0.1; open -g {event.src_path}')

class Watcher(object):
    """Opens newly created files."""
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.observer = Observer()
        self.observer.schedule(BackgroundOpenNew(), self.path, recursive=True)
        self.start()

    def start(self):
        self.observer.start()

    def stop(self):
        self.observer.stop()
