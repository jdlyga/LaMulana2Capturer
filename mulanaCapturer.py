import pyautogui
import win32gui
from google.cloud import vision
from google.cloud.vision import types
import io
import tempfile
from dataclasses import dataclass

####################################################################################################

def main():
    captureTablet()

####################################################################################################

@dataclass
class ClippingRegion:
    left: int
    top: int
    right: int
    bottom: int

####################################################################################################

def captureTablet():
    capture(clippingRegion=ClippingRegion(left=200, top=150, right=200, bottom=150))

####################################################################################################

def captureDialog():
    capture(clippingRegion=ClippingRegion(left=130, top=70, right=770, bottom=380))

####################################################################################################

def captureMessage():
    capture(clippingRegion=ClippingRegion(left=200, top=170, right=240, bottom=224))

####################################################################################################

def capture(clippingRegion: ClippingRegion):

    tempFileName = tempfile.mktemp()
    captureWindow(windowTitle='LaMulana2', filename=tempFileName, clippingRegion=clippingRegion)
    detectText(tempFileName)

####################################################################################################

def captureWindow(windowTitle: str, filename: str, clippingRegion: ClippingRegion):
    
    hwnd = win32gui.FindWindow(None, windowTitle)

    if not hwnd:
        print("Window not found")
        return None

    win32gui.SetForegroundWindow(hwnd)
    x, y, x1, y1 = win32gui.GetClientRect(hwnd)
    x, y = win32gui.ClientToScreen(hwnd, (x, y))
    x1, y1 = win32gui.ClientToScreen(hwnd, (x1 - x, y1 - y))
    PILImage = pyautogui.screenshot(
        region=(x + clippingRegion.left, 
                y + clippingRegion.top, 
                x1 - clippingRegion.right - clippingRegion.left, 
                y1 - clippingRegion.top - clippingRegion.bottom))

    PILImage.save(filename, format="png")
    PILImage.show()

####################################################################################################

def detectText(filename: str):
    """Detects text in the file."""

    client = vision.ImageAnnotatorClient()

    with io.open(filename, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)
    response = client.text_detection(image=image, max_results=1)
    texts = response.text_annotations

    print(texts[0].description)

####################################################################################################

main()