import pyautogui
import cv2
import numpy as np
import time
import pytesseract
import os
import subprocess
import tkinter as tk
from tkinter import simpledialog
from tkinter import filedialog

# Set the path to Tesseract executable if not in PATH
def set_tesseract_path():
    potential_paths = [
        r'/usr/local/bin/tesseract',
        r'/opt/homebrew/bin/tesseract'  # Common path for Homebrew on Apple Silicon
    ]
    for path in potential_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return
    raise FileNotFoundError("Tesseract is not installed or it's not in your PATH. Install Tesseract or update the script with the correct path.")

set_tesseract_path()

# Function to bring Chrome to the foreground using AppleScript
def bring_chrome_to_foreground():
    try:
        applescript = """
        tell application "Google Chrome"
            activate
        end tell
        """
        subprocess.run(["osascript", "-e", applescript])
        time.sleep(1)
    except Exception as e:
        print(f"Failed to bring Chrome to the foreground: {e}")

# Allow user to draw a box on the screen to define the region of interest
def get_roi():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    print("Please select the region of interest by clicking and dragging on the screen.")
    roi = pyautogui.screenshot()  # Placeholder for actual ROI selection method
    root.destroy()
    return roi

# Loop until all names are processed
def find_and_click_names():
    # Allow the user to draw the region of interest
    roi_bbox = pyautogui.screenshot()
    if roi_bbox is None:
        print("No region selected. Exiting.")
        return

    while True:
        try:
            # Bring Chrome window to the foreground
            bring_chrome_to_foreground()
            time.sleep(1)

            # Take a screenshot of the selected region
            screenshot = pyautogui.screenshot()

            # Convert screenshot to a format compatible with OpenCV
            screenshot_np = np.array(screenshot)
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

            # Define the region of interest to search for names
            roi = screenshot_gray

            # Use OCR to detect text (names) in the screenshot
            # Get bounding boxes of detected names
            d = pytesseract.image_to_data(roi, output_type=pytesseract.Output.DICT)

            for i in range(len(d['text'])):
                if int(d['conf'][i]) > 70 and d['text'][i].strip():  # Confidence threshold to filter results
                    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])

                    # Move to the matched location and click on the name
                    pyautogui.moveTo(x + w // 2, y + h // 2, duration=0.5)
                    pyautogui.click()

                    # Wait for the page to load
                    time.sleep(3)

                    # Bring Chrome window to the foreground again
                    bring_chrome_to_foreground()
                    time.sleep(1)

                    # Take a screenshot of the selected region again
                    screenshot = pyautogui.screenshot()
                    screenshot_np = np.array(screenshot)
                    screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

                    # Use OCR to detect and click the text "About"
                    d_about = pytesseract.image_to_data(screenshot_gray, output_type=pytesseract.Output.DICT)
                    for j in range(len(d_about['text'])):
                        if d_about['text'][j].strip().lower() == 'about' and int(d_about['conf'][j]) > 70:
                            (about_x, about_y, about_w, about_h) = (d_about['left'][j], d_about['top'][j], d_about['width'][j], d_about['height'][j])

                            # Move to the matched location and click on the "About" text
                            pyautogui.moveTo(about_x + about_w // 2, about_y + about_h // 2, duration=0.5)
                            pyautogui.click()

                            # Wait for the "About" page to load and perform the desired action
                            time.sleep(3)

                            # Perform any additional actions on the "About" page here
                            # e.g., pyautogui.click() to interact with elements

                            # Go back to the previous page (two times)
                            pyautogui.hotkey('command', 'left')  # First back navigation
                            time.sleep(1)
                            pyautogui.hotkey('command', 'left')  # Second back navigation
                            time.sleep(3)
                            break
                    break
        except Exception as e:
            print(f"An error occurred: {e}")

find_and_click_names()
