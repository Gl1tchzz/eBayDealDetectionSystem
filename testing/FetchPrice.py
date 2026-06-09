import subprocess
import time
import json
import pyperclip

MACBOOK_BARCODES = {
    ("13", 2020, "M1",     8): "i000000038431",
    ("13", 2020, "M1",    16): "i000000038434",
    ("14", 2021, "M1 Pro", 16): "i000000041694",
    ("13", 2022, "M2",     8): "i000000042410",
    ("13", 2022, "M2",    16): "i000000042415",
}


def get_macbook_price(screen_size: str, year: int, chip: str, ram_gb: int) -> dict:
    """
    Get musicmagpie trade-in prices for a MacBook.

    Args:
        screen_size: "13" or "14"
        year:        2020, 2021, or 2022
        chip:        "M1", "M1 Pro", or "M2"
        ram_gb:      8 or 16

    Returns:
        dict with keys: "good", "poor", "faulty"
    """
    key = (str(screen_size), int(year), chip, int(ram_gb))
    barcode = MACBOOK_BARCODES.get(key)

    if not barcode:
        available = "\n".join(
            f'  {s}" {y} {c} {r}GB'
            for (s, y, c, r) in sorted(MACBOOK_BARCODES.keys())
        )
        raise ValueError(
            f'No match for: {screen_size}" {year} {chip} {ram_gb}GB\n\nAvailable models:\n{available}'
        )

    url = (
        "https://www.musicmagpie.co.uk/Umbraco/Surface/Products/GetProductPrices"
        f"?barcode={barcode}&networkId=-1&website=musicMagpie"
    )

    # Navigate Chrome to the URL (bypasses Cloudflare as it's a real browser)
    subprocess.run([
        "osascript",
        "-e", f'tell application "Google Chrome" to set URL of active tab of front window to "{url}"',
    ], check=True)
    time.sleep(4)

    # Select all and copy — avoids any JS execution issues
    subprocess.run([
        "osascript",
        "-e", 'tell application "Google Chrome" to activate',
        "-e", 'tell application "System Events" to keystroke "a" using command down',
        "-e", 'tell application "System Events" to keystroke "c" using command down',
    ], check=True)
    time.sleep(0.5)

    text = pyperclip.paste().strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse response: {e}\nRaw: {text}")

    return {
        "good":   data.get("good"),
        "poor":   data.get("poor"),
        "faulty": data.get("faulty"),
    }


if __name__ == "__main__":
    prices = get_macbook_price("13", 2020, "M1", 16)
    print(f'Good:   £{prices["good"]}')
    print(f'Poor:   £{prices["poor"]}')
    print(f'Faulty: £{prices["faulty"]}')