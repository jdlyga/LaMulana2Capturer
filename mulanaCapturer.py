import pyautogui
import win32gui
import win32clipboard
import io
import os
import sys
import traceback
import tempfile
import json
import argparse
from playsound import playsound
from dataclasses import dataclass
from google.cloud.vision import types
from google.cloud import vision

####################################################################################################

def main():

    tabletLog, dialogLog, messageLog, skullLog, glossaryLog, screenshotsDirectory = parseConfigJson()

    argumentParser = argparse.ArgumentParser(description="Screenshot, OCR, and append text to files for La Mulana 2.")
    group = argumentParser.add_mutually_exclusive_group()
    group.add_argument("-t", "--tablet", action='store_true', help="capture and OCR text from a stone tablet")
    group.add_argument("-d", "--dialog", action='store_true', help="capture and OCR text from dialog")
    group.add_argument("-m", "--message", action='store_true', help="capture and OCR text from an email message")
    group.add_argument("-k", "--skull", action='store_true', help="capture and OCR text from a crystal skull")
    group.add_argument("-g", "--glossary", action='store_true', help="capture and OCR text from the glossary")
    group.add_argument("-s", "--screenshotCopy", action='store_true', help="take a screenshot for making maps to the clipboard")
    group.add_argument("-sv", "--screenshotSave", action='store_true', help="take a screenshot for making maps and write it to a file")


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
    elif (args['skull']):
        captureAndLog(logFilename=skullLog, 
                      clippingRegion=ClippingRegion(left=203, top=231, right=203, bottom=176))
    elif (args['glossary']):
        captureAndLog(logFilename=glossaryLog, 
                      clippingRegion=ClippingRegion(left=310, top=286, right=771, bottom=171))
    elif (args['screenshotCopy']):
        try:
            PILImage = captureWindow(windowTitle='LaMulana2', clippingRegion=ClippingRegion(left=127, top=134, right=127, bottom=64))
            sendToClipboard(PILImage)
            playsound('sounds/Screenshot.mp3')
        except:
            playsound('sounds/Error.mp3')
    elif (args['screenshotSave']):
        try:
            PILImage = captureWindow(windowTitle='LaMulana2', clippingRegion=ClippingRegion(left=127, top=134, right=127, bottom=64))
            nextPath = getNextPath(f'{screenshotsDirectory}/mapScreenshot-')
            PILImage.save(nextPath, format="png")
            playsound('sounds/Screenshot.mp3')
        except:
            playsound("sounds/Error.mp3")

    else:
        argumentParser.print_help()

####################################################################################################

@dataclass
class ClippingRegion:
    """represents the amount of pixels on each side to clip from the edge of the screen"""
    left: int
    top: int
    right: int
    bottom: int

####################################################################################################

def parseConfigJson():
    """the destination for OCR'd text is specified in a json config file"""
    with open("config.json") as configFile:
        configData = json.load(configFile)
    
    if not configData:
        raise FileNotFoundError

    return configData['tabletLog'], configData['dialogLog'], configData['messageLog'], configData['skullLog'], configData['glossaryLog'], configData['screenshotsDirectory']

####################################################################################################

def captureAndLog(logFilename: str, clippingRegion: ClippingRegion):
    """takes a screenshot, runs OCR conversion, and logs the result to a file"""

    playsound('sounds/Screenshot.mp3')

    try:
        tempFileName = tempfile.mktemp()
        PILImage = captureWindow(windowTitle='LaMulana2', clippingRegion=clippingRegion)
        PILImage.save(tempFileName, format="png")
        detectedText = detectText(tempFileName)

        with open(logFilename, "a", encoding='utf-8') as outputFile:
            outputFile.write(detectedText)
            outputFile.write("\n" + "|"*60 + "\n\n")

        os.remove(tempFileName)
        playsound('sounds/Success.mp3')
        
    except:
        playsound('sounds/Error.mp3')

####################################################################################################

def getNextPath(pathPattern: str):
    """
    Finds the next free path in an sequentially named list of files

    e.g. pathPattern = 'file-%s.txt':

    file-1.txt
    file-2.txt
    file-3.txt

    Runs in log(n) time where n is the number of existing files in sequence
    """
    i = 1

    # First do an exponential search
    while os.path.exists(f"{pathPattern}{str(i).zfill(5)}.png"):
        i = i * 2

    # Result lies somewhere in the interval (i/2..i]
    # We call this interval (a..b] and narrow it down until a + 1 = b
    a, b = (i // 2, i)
    while a + 1 < b:
        c = (a + b) // 2 # interval midpoint
        a, b = (c, b) if os.path.exists(f"{pathPattern}{str(c).zfill(5)}.png") else (a, c)

    return f"{pathPattern}{str(b).zfill(5)}.png"

####################################################################################################

def captureWindow(windowTitle: str, clippingRegion: ClippingRegion):
    """takes a screenshot of a specific window (windows only)"""
    
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

    return PILImage

####################################################################################################

def detectText(filename: str):
    """uses google cloud vision to OCR the text of an image file"""

    client = vision.ImageAnnotatorClient()

    with io.open(filename, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)
    response = client.text_detection(image=image, max_results=1)
    texts = response.text_annotations

    return texts[0].description

####################################################################################################

def sendToClipboard(image):
    output = io.BytesIO()
    image.convert('RGB').save(output, 'BMP')
    data = output.getvalue()[14:]
    output.close()

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

####################################################################################################

main()