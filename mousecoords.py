import pyautogui
import time
from threading import Thread, Event
from typing import Optional, Tuple

class MouseCoordinateTracker:
    def __init__(self, update_interval: float = 0.1, 
                 output_format: str = "console", 
                 log_file: Optional[str] = None):
        """
        Track and display mouse coordinates in real-time
        
        Parameters:
        - update_interval: Seconds between updates (default: 0.1)
        - output_format: How to display coordinates ('console', 'tuple', or 'both')
        - log_file: Optional file path to log coordinates (e.g., 'mouse_log.txt')
        """
        self.update_interval = update_interval
        self.output_format = output_format
        self.log_file = log_file
        self._stop_event = Event()
        self._thread: Optional[Thread] = None
        self.last_position: Optional[Tuple[int, int]] = None
        
    def _track_coordinates(self):
        """Background thread that tracks mouse position"""
        try:
            if self.log_file:
                with open(self.log_file, 'a') as f:
                    f.write("Mouse Coordinate Log\n")
                    f.write("-------------------\n")
            
            while not self._stop_event.is_set():
                x, y = pyautogui.position()
                self.last_position = (x, y)
                
                # Format output
                if self.output_format == "console":
                    output = f"X: {x:4d}, Y: {y:4d}"
                elif self.output_format == "tuple":
                    output = f"({x}, {y})"
                else:  # both
                    output = f"({x}, {y}) - X: {x:4d}, Y: {y:4d}"
                
                # Print to console
                print(output, end='\r', flush=True)
                
                # Log to file if specified
                if self.log_file:
                    with open(self.log_file, 'a') as f:
                        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {output}\n")
                
                time.sleep(self.update_interval)
        except Exception as e:
            print(f"\nTracking error: {e}")
        finally:
            print("\nTracking stopped" + " " * 30)  # Clear line
    
    def get_current_position(self) -> Optional[Tuple[int, int]]:
        """Get the last recorded mouse position"""
        return self.last_position
    
    def start_tracking(self):
        """Begin tracking mouse coordinates"""
        if self._thread and self._thread.is_alive():
            print("Tracking is already running")
            return
        
        self._stop_event.clear()
        self._thread = Thread(target=self._track_coordinates, daemon=True)
        self._thread.start()
        print("Started mouse coordinate tracking (Press Ctrl+C to stop)")
    
    def stop_tracking(self):
        """Stop tracking mouse coordinates"""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1)
        print("\nTracking stopped")
    
    def __enter__(self):
        """Context manager entry point"""
        self.start_tracking()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point"""
        self.stop_tracking()
    
    @staticmethod
    def get_once() -> Tuple[int, int]:
        """Get current mouse coordinates once"""
        return pyautogui.position()

# Example Usage
if __name__ == "__main__":
    print("=== Mouse Coordinate Tracker ===")
    print("1. Track continuously (with context manager)")
    print("2. Track continuously (manual start/stop)")
    print("3. Get single coordinate reading")
     
    choice = input("Choose mode (1-3): ")
    
    if choice == "1":
        # Context manager automatically handles start/stop
        with MouseCoordinateTracker(update_interval=0.05, 
                                 output_format="both",
                                 log_file="mouse_log.txt") as tracker:
            try:
                while True:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                pass
    
    elif choice == "2":
        # Manual start/stop
        tracker = MouseCoordinateTracker(update_interval=0.1)
        tracker.start_tracking()
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            tracker.stop_tracking()
    
    elif choice == "3":
        # Single reading
        x, y = MouseCoordinateTracker.get_once()
        print(f"\nCurrent mouse position: ({x}, {y})")
    
    else:
        print("Invalid choice")