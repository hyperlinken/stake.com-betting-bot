import pyautogui
import numpy as np
from typing import Tuple, List, Union
import time

class ScreenPixelDetector:
    def __init__(self, debug: bool = False):
        """
        Initialize the pixel detector
        
        Parameters:
        - debug: If True, will print debug information
        """
        self.debug = debug
        self.cached_regions = {}
        
    def get_pixel_color(self, x: int, y: int) -> Tuple[int, int, int]:
        """
        Get RGB color of a single pixel at (x, y) coordinates
        
        Returns:
        - Tuple of (R, G, B) values (0-255)
        """
        pixel = pyautogui.pixel(x, y)
        if self.debug:
            print(f"Pixel at ({x}, {y}): RGB{pixel}")
        return pixel
    
    def get_region_color(self, x: int, y: int, width: int, height: int, 
                        sample_method: str = 'average') -> Union[Tuple[int, int, int], List[Tuple[int, int, int]]]:
        """
        Get color(s) from a screen region
        
        Parameters:
        - x, y: Top-left coordinates
        - width, height: Region dimensions
        - sample_method: 
            - 'average': Returns average color of region
            - 'all': Returns list of all pixel colors
            - 'center': Returns center pixel color
            - 'first': Returns top-left pixel color
        
        Returns:
        - Depending on sample_method, either a single RGB tuple or list of tuples
        """
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        pixels = np.array(screenshot)
        
        if sample_method == 'average':
            avg_color = np.mean(pixels, axis=(0, 1)).astype(int)
            if self.debug:
                print(f"Average color in region ({x}, {y}, {width}, {height}): RGB{tuple(avg_color)}")
            return tuple(avg_color)
        elif sample_method == 'all':
            return [tuple(pixel) for pixel in pixels.reshape(-1, 3)]
        elif sample_method == 'center':
            center_x, center_y = width // 2, height // 2
            center_color = tuple(pixels[center_y, center_x])
            if self.debug:
                print(f"Center color in region ({x}, {y}, {width}, {height}): RGB{center_color}")
            return center_color
        elif sample_method == 'first':
            first_color = tuple(pixels[0, 0])
            if self.debug:
                print(f"First color in region ({x}, {y}, {width}, {height}): RGB{first_color}")
            return first_color
        else:
            raise ValueError("Invalid sample_method. Use 'average', 'all', 'center', or 'first'")
    
    def cache_region(self, name: str, x: int, y: int, width: int, height: int):
        """
        Cache a screen region for faster repeated checking
        """
        self.cached_regions[name] = (x, y, width, height)
    
    def get_cached_region_color(self, name: str, sample_method: str = 'average') -> Union[Tuple[int, int, int], List[Tuple[int, int, int]]]:
        """
        Get color from a previously cached region
        """
        if name not in self.cached_regions:
            raise ValueError(f"No cached region named '{name}'")
        x, y, width, height = self.cached_regions[name]
        return self.get_region_color(x, y, width, height, sample_method)
    
    def wait_for_color(self, x: int, y: int, expected_color: Tuple[int, int, int], 
                      timeout: float = 10, interval: float = 0.1, 
                      tolerance: int = 0) -> bool:
        """
        Wait until a pixel matches the expected color
        
        Parameters:
        - x, y: Pixel coordinates
        - expected_color: RGB tuple
        - timeout: Maximum time to wait (seconds)
        - interval: Check interval (seconds)
        - tolerance: Allowed color difference (0-255)
        
        Returns:
        - True if color matched, False if timeout reached
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            current_color = self.get_pixel_color(x, y)
            if self._color_match(current_color, expected_color, tolerance):
                if self.debug:
                    print(f"Color matched at ({x}, {y}) after {time.time() - start_time:.2f}s")
                return True
            time.sleep(interval)
        return False
    
    def wait_for_region_color(self, x: int, y: int, width: int, height: int,
                            expected_color: Tuple[int, int, int], 
                            timeout: float = 10, interval: float = 0.1,
                            tolerance: int = 0, sample_method: str = 'average') -> bool:
        """
        Wait until a region matches the expected color
        
        Parameters:
        - x, y, width, height: Region coordinates
        - expected_color: RGB tuple
        - timeout: Maximum time to wait (seconds)
        - interval: Check interval (seconds)
        - tolerance: Allowed color difference (0-255)
        - sample_method: How to sample region ('average', 'center', 'first')
        
        Returns:
        - True if color matched, False if timeout reached
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            current_color = self.get_region_color(x, y, width, height, sample_method)
            if self._color_match(current_color, expected_color, tolerance):
                if self.debug:
                    print(f"Region color matched after {time.time() - start_time:.2f}s")
                return True
            time.sleep(interval)
        return False
    
    def _color_match(self, color1: Tuple[int, int, int], 
                    color2: Tuple[int, int, int], 
                    tolerance: int = 0) -> bool:
        """
        Check if two colors match within tolerance
        """
        return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2))
    
    def detect_color_in_region(self, 
                         x: int, 
                         y: int, 
                         width: int, 
                         height: int, 
                         target_color: Tuple[int, int, int], 
                         tolerance: int = 0,
                         sample_method: str = 'all') -> bool:
        if sample_method == 'all':
            # Get all pixel colors in the region
            pixels = self.get_region_color(x, y, width, height, 'all')
            # Check if any pixel matches within tolerance
            return any(self._color_match(pixel, target_color, tolerance) for pixel in pixels)
        elif sample_method == 'average':
            avg_color = self.get_region_color(x, y, width, height, 'average')
            return self._color_match(avg_color, target_color, tolerance)
        else:
            # For 'first' or 'center' methods
            pixel = self.get_region_color(x, y, width, height, sample_method)
            return self._color_match(pixel, target_color, tolerance)

# Example Usage
if __name__ == "__main__":
    # Initialize detector with debug mode
    detector = ScreenPixelDetector(debug=True)
    
    # Example 1: Check single pixel
    while(True):
        pixel_color = detector.get_pixel_color(380, 714)
        # print(f"Pixel color at (1267, 686): {pixel_color}")
        # time.sleep(0.3)
    
    # Example 2: Check region average color
    # while(True):
    #     avg_color = detector.get_region_color(457, 589, 180, 30, 'average')
    #     print(f"Average color in region: {avg_color}")
    #     time.sleep(0.3)
    
    # # Example 3: Cache and monitor a region
    # detector.cache_region('button_area', 300, 300, 50, 50)
    # button_color = detector.get_cached_region_color('button_area', 'center')
    # print(f"Cached button color: {button_color}")
    
    # # Example 4: Wait for color change
    # print("Waiting for pixel (500, 500) to turn red...")
    # success = detector.wait_for_color(500, 500, (255, 0, 0), timeout=5)
    # print(f"Success: {success}")
    
    # # Example 5: Wait for region color change with tolerance
    # print("Waiting for region to become approximately white...")
    # success = detector.wait_for_region_color(
    #     400, 400, 100, 100, (240, 240, 240), 
    #     tolerance=20
    # )
    # print(f"Success: {success}")