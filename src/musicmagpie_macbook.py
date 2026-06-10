"""
MusicMagpie trade-in price lookup.

Uses MusicMagpie's internal product barcodes to retrieve
Good / Poor / Faulty trade-in prices for supported MacBooks.
"""

import json
import subprocess
import time

import pyperclip


# Mapping format:
# (Model, Screen Size, Year, Chip, RAM) -> MusicMagpie barcode
#
# Model is included because some MacBooks share the same:
# - screen size
# - year
# - chip
# - RAM
#
# Example:
# A 13-inch 2020 M1 8GB MacBook can be either Air or Pro.
MACBOOK_BARCODES = {
    # MacBook Air M1 13-inch 2020
    ("Air", "13", 2020, "M1", 8): "i000000038437",
    ("Air", "13", 2020, "M1", 16): "i000000038444",

    # MacBook Air M2 13-inch 2022
    ("Air", "13", 2022, "M2", 8): "i000000042859",
    ("Air", "13", 2022, "M2", 16): "i000000042968",

    # MacBook Pro M1 13-inch 2020
    ("Pro", "13", 2020, "M1", 8): "i000000038431",
    ("Pro", "13", 2020, "M1", 16): "i000000038434",

    # MacBook Pro M1 Pro 14-inch 2021
    ("Pro", "14", 2021, "M1 Pro", 16): "i000000041694",
    ("Pro", "14", 2021, "M1 Pro", 32): "i000000041705",
}


def normalise_screen_size(screen_size):
    """
    Converts parsed screen sizes into barcode lookup format.

    Examples:
        13.3" -> 13
        14.2" -> 14
        16.2" -> 16
    """

    size = str(screen_size).replace('"', "").replace("'", "").strip()

    if size in ["13.3", "13 inch", "13-inch"]:
        return "13"

    if size in ["14.2", "14 inch", "14-inch"]:
        return "14"

    if size in ["16.2", "16 inch", "16-inch"]:
        return "16"

    return size


def normalise_chip(chip):
    """
    Converts parsed CPU values into barcode lookup format.
    """

    chip_clean = str(chip).upper().replace("APPLE ", "").strip()

    chip_map = {
        "M1": "M1",
        "M1 PRO": "M1 Pro",
        "M1 MAX": "M1 Max",
        "M2": "M2",
        "M2 PRO": "M2 Pro",
        "M2 MAX": "M2 Max",
        "M3": "M3",
        "M3 PRO": "M3 Pro",
        "M3 MAX": "M3 Max",
    }

    return chip_map.get(chip_clean)


def get_musicmagpie_price(model, screen_size, year, chip, ram_gb):
    """
    Gets MusicMagpie trade-in prices for a MacBook.

    Args:
        model:
            Air or Pro.

        screen_size:
            Screen size, e.g. 13, 14, 16.

        year:
            Release year.

        chip:
            Apple Silicon chip, e.g. M1, M1 Pro, M2.

        ram_gb:
            RAM amount in GB.

    Returns:
        dict:
            {
                "good": price,
                "poor": price,
                "faulty": price
            }

        None:
            Returned if no barcode exists or the request fails.
    """

    # Clean the parsed specs so they match the dictionary keys.
    size = normalise_screen_size(screen_size)
    chip_key = normalise_chip(chip)

    if not chip_key:
        return None

    try:
        year = int(year)
        ram = int(str(ram_gb).replace("GB", "").replace("gb", "").strip())
    except (ValueError, TypeError):
        return None

    # Full unique lookup key.
    key = (model, size, year, chip_key, ram)

    barcode = MACBOOK_BARCODES.get(key)

    if not barcode:
        print(f"[MusicMagpie] No barcode found for: {key}")
        return None

    # MusicMagpie endpoint that returns JSON trade-in values.
    url = (
        "https://www.musicmagpie.co.uk/Umbraco/Surface/Products/GetProductPrices"
        f"?barcode={barcode}&networkId=-1&website=musicMagpie"
    )

    try:
        # Open the endpoint in the current Chrome tab.
        subprocess.run(
            [
                "osascript",
                "-e",
                f'tell application "Google Chrome" to set URL of active tab of front window to "{url}"',
            ],
            check=True,
        )

        time.sleep(4)

        # Select all page text and copy it to clipboard.
        subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "Google Chrome" to activate',
                "-e",
                'tell application "System Events" to keystroke "a" using command down',
                "-e",
                'tell application "System Events" to keystroke "c" using command down',
            ],
            check=True,
        )

        time.sleep(0.5)

        # Parse the copied JSON response.
        data = json.loads(
            pyperclip.paste().strip()
        )

        return {
            "good": data.get("good"),
            "poor": data.get("poor"),
            "faulty": data.get("faulty"),
        }

    except Exception as error:
        print(f"[MusicMagpie] Failed to fetch price: {error}")
        return None