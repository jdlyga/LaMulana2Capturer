Python script for taking screenshots of La Mulana 2, converting the images to text (OCR), and appending the text to files for keeping notes of all text in the game.

I suggest using AutoHotkey (or something similar) to set up keyboard shortcuts to run the script to capture each type of text.  I've included a sample AutHotkey script.

```
usage: mulanaCapturer.py [-h] [-t | -d | -m]

Screenshot, OCR, and append text to files for La Mulana 2.

optional arguments:
  -h, --help     show this help message and exit
  -t, --tablet   capture and OCR text from a stone tablet
  -d, --dialog   capture and OCR text from dialog
  -m, --message  capture and OCR text from an email message
```

## Requirements:

Windows 10 with Python 3.8 installed

Python dependencies installed (pywin32, pyautogui, google-cloud-vision)

La Mulana 2 needs to be running in a 1920x1080 window

You need to sign up for Google Cloud Vision and your own credentials stored in GOOGLE_APPLICATION_CREDENTIALS (in your path)

&nbsp;

##### Example: tablet.txt
```
||||||||||||||||||||||||||||||||||||||||||||||||||||||

[Face Mural]
There are several face murals by the ruins' entrance. They contain mechanisms
to make the eyes glow, but it isn't in effect at the current time. The reason for the
murals' construction is unclear.
Please head downwards.
[Warning!]
Please do not jump off of the edge unless you are a qualified ninja (or
archaeologist).

||||||||||||||||||||||||||||||||||||||||||||||||||||||

[Split Gate]
Similar to the Candi Bentar of Bali Island, but decorated differently. It's thought to
have been built in tribute to the creator of the La-Mulana ruins, but these claims
are unverified. There are also tales that people emerged from here once, but
these claims, too, are unverified.

||||||||||||||||||||||||||||||||||||||||||||||||||||||
```

Sound effects from Freesound:
* https://freesound.org/s/360329/
* https://freesound.org/s/445978/
* https://freesound.org/s/417141/
