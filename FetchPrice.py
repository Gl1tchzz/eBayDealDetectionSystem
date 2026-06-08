import subprocess
import time
import json
import pyperclip

url = "https://www.musicmagpie.co.uk/Umbraco/Surface/Products/GetProductPrices?barcode=i000000041709&networkId=-1&website=musicMagpie"

subprocess.run([
    "osascript",
    "-e",
    f'tell application "Google Chrome" to open location "{url}"',
    "-e",
    'tell application "Google Chrome" to activate'
])

time.sleep(5)

subprocess.run([
    "osascript",
    "-e",
    'tell application "System Events" to keystroke "a" using command down',
    "-e",
    'tell application "System Events" to keystroke "c" using command down'
])

time.sleep(1)

text = pyperclip.paste()

print("Response:")
print(text)

try:
    data = json.loads(text)
    print("GOOD:", data["good"])
    print("POOR:", data["poor"])
    print("FAULTY:", data["faulty"])
except Exception as e:
    print("Failed to parse JSON:", e)