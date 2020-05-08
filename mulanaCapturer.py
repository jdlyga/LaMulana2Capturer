import pyautogui
import win32gui
from google.cloud import vision
from google.cloud.vision import types
import io

####################################################################################################

def main():

    imageFile = io.BytesIO()
    captureWindow('Lamulana2', imageFile)
    if imageFile:
        detectText('test.png')

####################################################################################################

def captureWindow(windowTitle, imageFile):
    
    hwnd = win32gui.FindWindow(None, windowTitle)

    if not hwnd:
        print("Window not found")
        return None

    win32gui.SetForegroundWindow(hwnd)
    x, y, x1, y1 = win32gui.GetClientRect(hwnd)
    x, y = win32gui.ClientToScreen(hwnd, (x, y))
    x1, y1 = win32gui.ClientToScreen(hwnd, (x1 - x, y1 - y))
    PILImage = pyautogui.screenshot(region=(x, y, x1, y1))
    
    PILImage.save('test.png')

    return imageFile

####################################################################################################

def detectText(path):
    """Detects text in the file."""

    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)
    response = client.text_detection(image=image, max_results=1)
    texts = response.text_annotations

    print(texts[0].description)

####################################################################################################

main()