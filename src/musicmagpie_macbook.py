import json
import os
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


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

    # Add the correct 14-inch M2 Pro barcode when verified.
    # ("Pro", "14", 2023, "M2 Pro", 16): "CORRECT_BARCODE_HERE",
}

# Project root:
# EbayPriceTracker/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

BROWSER_DATA_DIR = Path(
    os.getenv(
        "MUSICMAGPIE_BROWSER_DATA_DIR",
        str(DATA_DIR / "musicmagpie-browser"),
    )
)

DEBUG_DIR = Path(
    os.getenv(
        "MUSICMAGPIE_DEBUG_DIR",
        str(DATA_DIR / "musicmagpie-debug"),
    )
)


def normalise_screen_size(screen_size):
    size = (
        str(screen_size)
        .replace('"', "")
        .replace("'", "")
        .strip()
        .lower()
    )

    size_map = {
        "13.3": "13",
        "13 inch": "13",
        "13-inch": "13",
        "14.2": "14",
        "14 inch": "14",
        "14-inch": "14",
        "16.2": "16",
        "16 inch": "16",
        "16-inch": "16",
    }

    return size_map.get(size, size)


def normalise_chip(chip):
    chip_clean = (
        str(chip)
        .upper()
        .replace("APPLE ", "")
        .strip()
    )

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


def normalise_price(value):
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    try:
        return float(
            str(value)
            .replace("£", "")
            .replace(",", "")
            .strip()
        )
    except (TypeError, ValueError):
        return None


def response_looks_blocked(body_text):
    blocked_phrases = (
        "checking your browser",
        "verify you are human",
        "just a moment",
        "attention required",
        "cloudflare",
        "access denied",
        "enable javascript and cookies",
    )

    lowered_body = body_text.lower()

    return any(
        phrase in lowered_body
        for phrase in blocked_phrases
    )


def save_debug_files(page, barcode, body_text):
    try:
        DEBUG_DIR.mkdir(parents=True, exist_ok=True)

        screenshot_path = DEBUG_DIR / f"{barcode}.png"
        response_path = DEBUG_DIR / f"{barcode}.txt"

        page.screenshot(
            path=str(screenshot_path),
            full_page=True,
        )

        response_path.write_text(
            body_text,
            encoding="utf-8",
        )

        print(
            "[MusicMagpie] Debug files saved to "
            f"{DEBUG_DIR}"
        )

    except Exception as error:
        print(
            "[MusicMagpie] Failed to save debug files: "
            f"{error}"
        )


def fetch_musicmagpie_prices(barcode):
    BROWSER_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    url = (
        "https://www.musicmagpie.co.uk/"
        "Umbraco/Surface/Products/GetProductPrices"
        f"?barcode={barcode}"
        "&networkId=-1"
        "&website=musicMagpie"
    )

    with sync_playwright() as playwright:
        context = None

        try:
            # headless=False is intentional.
            # Xvfb provides the virtual graphical display on Ubuntu.
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(BROWSER_DATA_DIR),
                headless=False,
                channel="chromium",
                viewport={
                    "width": 1365,
                    "height": 768,
                },
                locale="en-GB",
                timezone_id="Europe/London",
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--window-size=1365,768",
                ],
            )

            if context.pages:
                page = context.pages[0]
            else:
                page = context.new_page()

            print(
                "[MusicMagpie] Opening pricing page for "
                f"barcode {barcode}"
            )

            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60_000,
            )

            if response is None:
                print(
                    "[MusicMagpie] Browser returned no response"
                )
                return None

            print(
                "[MusicMagpie] Response status: "
                f"{response.status}"
            )

            # Allow JavaScript, redirects and Cloudflare checks time to finish.
            page.wait_for_timeout(8_000)

            body_text = page.locator("body").inner_text().strip()

            if response_looks_blocked(body_text):
                print(
                    "[MusicMagpie] A Cloudflare or access "
                    "challenge was detected"
                )

                save_debug_files(
                    page,
                    barcode,
                    body_text,
                )

                return None

            try:
                data = json.loads(body_text)

            except json.JSONDecodeError:
                print(
                    "[MusicMagpie] The browser response was "
                    "not valid JSON"
                )

                print(
                    "[MusicMagpie] Response preview: "
                    f"{body_text[:300]}"
                )

                save_debug_files(
                    page,
                    barcode,
                    body_text,
                )

                return None

            if not isinstance(data, dict):
                print(
                    "[MusicMagpie] Unexpected JSON type: "
                    f"{type(data).__name__}"
                )
                return None

            prices = {
                "good": normalise_price(data.get("good")),
                "poor": normalise_price(data.get("poor")),
                "faulty": normalise_price(data.get("faulty")),
            }

            if all(
                value is None
                for value in prices.values()
            ):
                print(
                    "[MusicMagpie] No usable prices returned: "
                    f"{data}"
                )
                return None

            print(
                "[MusicMagpie] Prices fetched successfully: "
                f"{prices}"
            )

            return prices

        except PlaywrightTimeoutError as error:
            print(
                "[MusicMagpie] Browser timed out: "
                f"{error}"
            )
            return None

        except Exception as error:
            print(
                "[MusicMagpie] Browser fetch failed: "
                f"{type(error).__name__}: {error}"
            )
            return None

        finally:
            if context is not None:
                context.close()


def get_musicmagpie_price(
    model,
    screen_size,
    year,
    chip,
    ram_gb,
):
    size = normalise_screen_size(screen_size)
    chip_key = normalise_chip(chip)

    if not chip_key:
        print(
            f"[MusicMagpie] Unsupported chip: {chip}"
        )
        return None

    try:
        year = int(year)

        ram = int(
            str(ram_gb)
            .replace("GB", "")
            .replace("gb", "")
            .strip()
        )

    except (ValueError, TypeError):
        print(
            "[MusicMagpie] Invalid specifications: "
            f"year={year}, ram={ram_gb}"
        )
        return None

    key = (
        model,
        size,
        year,
        chip_key,
        ram,
    )

    barcode = MACBOOK_BARCODES.get(key)

    if not barcode:
        print(
            f"[MusicMagpie] No barcode found for: {key}"
        )
        return None

    return fetch_musicmagpie_prices(barcode)