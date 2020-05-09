import pyautogui
import win32gui
import io
import tempfile
import json
import argparse
from dataclasses import dataclass
from google.cloud.vision import types
from google.cloud import vision

####################################################################################################

def main():

    tabletLog, dialogLog, messageLog = parseConfigJson()

    argumentParser = argparse.ArgumentParser(description="Screenshot, OCR, and append text to files for La Mulana 2.")
    group = argumentParser.add_mutually_exclusive_group()
    group.add_argument("-t", "--tablet", action='store_true', help="capture and OCR text from a stone tablet")
    group.add_argument("-d", "--dialog", action='store_true', help="capture and OCR text from dialog")
    group.add_argument("-m", "--message", action='store_true', help="capture and OCR text from an email message")

    args = vars(argumentParser.parse_args())

    if (args['tablet']):
        captureAndLog(logFilename=tabletLog, 
                      clippingRegion=ClippingRegion(left=200, top=150, right=200, bottom=150))
    elif (args['dialog']):
        captureAndLog(logFilename=dialogLog, 
                      clippingRegion=ClippingRegion(left=130, top=70, right=770, bottom=380))
    elif (args['message']):
        captureAndLog(logFilename=messageLog, 
                      clippingRegion=ClippingRegion(left=200, top=170, right=240, bottom=224))
    else:
        argumentParser.print_help()

####################################################################################################

@dataclass
class ClippingRegion:
    left: int
    top: int
    right: int
    bottom: int

####################################################################################################

def parseConfigJson():
    with open("config.json") as configFile:
        configData = json.load(configFile)
    
    if not configData:
        raise FileNotFoundError

    return configData['tabletLog'], configData['dialogLog'], configData['messageLog'] 

####################################################################################################

def captureAndLog(logFilename: str, clippingRegion: ClippingRegion):

    tempFileName = tempfile.mktemp()
    captureWindow(windowTitle='LaMulana2', filename=tempFileName, clippingRegion=clippingRegion)
    detectedText = detectText(tempFileName)

    with open(logFilename, "a") as outputFile:
        outputFile.write(detectedText)
        outputFile.write("\n" + "|"*100 + "\n\n")

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

    try:
        return texts[0].description
    except:
        return ""

####################################################################################################

main()