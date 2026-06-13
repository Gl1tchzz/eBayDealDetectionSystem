import json
import subprocess
import time

import pyperclip


MACBOOK_BARCODES = {
    ("Air", "13", 2020, "M1", 8): "i000000038437",
    ("Air", "13", 2020, "M1", 16): "i000000038444",

    ("Air", "13", 2022, "M2", 8): "i000000042859",
    ("Air", "13", 2022, "M2", 16): "i000000042968",

    ("Pro", "13", 2020, "M1", 8): "i000000038431",
    ("Pro", "13", 2020, "M1", 16): "i000000038434",

    ("Pro", "14", 2021, "M1 Pro", 16): "i000000041694",
    ("Pro", "14", 2021, "M1 Pro", 32): "i000000041705",

    ("Pro", "16", 2021, "M1 Pro", 16): "i000000041818",
    ("Pro", "16", 2021, "M1 Pro", 32): "i000000041753",

    ("Pro", "13", 2022, "M2", 8): "i000000042410",
    ("Pro", "13", 2022, "M2", 16): "i000000042415",

    # Add the correct 14-inch M2 Pro barcode here when verified.
    # Do NOT use i000000042415 because that is for 13-inch M2 Pro 16GB.
    # ("Pro", "14", 2023, "M2 Pro", 16): "CORRECT_BARCODE_HERE",
}


def normalise_screen_size(screen_size):
    size = str(screen_size).replace('"', "").replace("'", "").strip().lower()

    if size in ["13.3", "13 inch", "13-inch"]:
        return "13"

    if size in ["14.2", "14 inch", "14-inch"]:
        return "14"

    if size in ["16.2", "16 inch", "16-inch"]:
        return "16"

    return size


def normalise_chip(chip):
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
    size = normalise_screen_size(screen_size)
    chip_key = normalise_chip(chip)

    if not chip_key:
        return None

    try:
        year = int(year)
        ram = int(str(ram_gb).replace("GB", "").replace("gb", "").strip())
    except (ValueError, TypeError):
        return None

    key = (model, size, year, chip_key, ram)
    barcode = MACBOOK_BARCODES.get(key)

    if not barcode:
        print(f"[MusicMagpie] No barcode found for: {key}")
        return None

    url = (
        "https://www.musicmagpie.co.uk/Umbraco/Surface/Products/GetProductPrices"
        f"?barcode={barcode}&networkId=-1&website=musicMagpie"
    )

    try:
        subprocess.run(
            [
                "osascript",
                "-e",
                f'tell application "Google Chrome" to set URL of active tab of front window to "{url}"',
            ],
            check=True,
        )

        time.sleep(4)

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

        data = json.loads(pyperclip.paste().strip())

        return {
            "good": data.get("good"),
            "poor": data.get("poor"),
            "faulty": data.get("faulty"),
        }

    except Exception as error:
        print(f"[MusicMagpie] Failed to fetch price: {error}")
        return None