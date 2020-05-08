import pyautogui
import win32gui
import pytesseract
try:
    from PIL import Image
except ImportError:
    import Image

####################################################################################################

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

####################################################################################################

def main():

    image = captureWindow('Untitled - Paint')
    if image:
        print(ocrCore(image))

####################################################################################################

def captureWindow(windowTitle=None):
    
    hwnd = win32gui.FindWindow(None, windowTitle)

    if not hwnd:
        print("Window not found")
        return None

    win32gui.SetForegroundWindow(hwnd)
    x, y, x1, y1 = win32gui.GetClientRect(hwnd)
    x, y = win32gui.ClientToScreen(hwnd, (x, y))
    x1, y1 = win32gui.ClientToScreen(hwnd, (x1 - x, y1 - y))
    image = pyautogui.screenshot(region=(x, y, x1, y1))
    return image

####################################################################################################

def ocrCore(image):
    """
    This function will handle the core OCR processing of images.
    """
    text = pytesseract.image_to_string(image)  # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
    return text

####################################################################################################

main()