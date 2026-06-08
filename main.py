import base64
import os
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("EBAY_CLIENT_ID")
CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")

SEARCH_QUERY = "MacBook Pro M1 Pro"
MAX_PRICE = 550
CHECK_EVERY_SECONDS = 300  # 5 minutes
SEEN_FILE = "seen_items.json"


def get_access_token():
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()

    response = requests.post(
        "https://api.ebay.com/identity/v1/oauth2/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded}",
        },
        data={
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope",
        },
    )

    response.raise_for_status()
    return response.json()["access_token"]


def load_seen_items():
    if not os.path.exists(SEEN_FILE):
        return set()

    with open(SEEN_FILE, "r") as file:
        return set(json.load(file))


def save_seen_items(seen_items):
    with open(SEEN_FILE, "w") as file:
        json.dump(list(seen_items), file)


def search_ebay(token):
    response = requests.get(
        "https://api.ebay.com/buy/browse/v1/item_summary/search",
        headers={
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_GB",
        },
        params={
            "q": SEARCH_QUERY,
            "category_ids": "111422",  # Laptops & Netbooks
            "filter": f"price:[0..{MAX_PRICE}],priceCurrency:GBP,buyingOptions:{{FIXED_PRICE}}",
            "sort": "newlyListed",
            "limit": "50",
        },
    )

    response.raise_for_status()
    return response.json().get("itemSummaries", [])


def is_good_listing(item):
    title = item.get("title", "").lower()

    required_words = ["macbook", "pro", "m1"]
    banned_words = [
        "case",
        "cover",
        "screen protector",
        "keyboard",
        "charger",
        "box only",
        "for parts",
        "spares",
        "repair",
        "faulty",
        "icloud",
        "locked",
    ]

    if not all(word in title for word in required_words):
        return False

    if any(word in title for word in banned_words):
        return False

    price = float(item.get("price", {}).get("value", 999999))

    return price <= MAX_PRICE


def main():
    seen_items = load_seen_items()

    print(f"Tracking: {SEARCH_QUERY}")
    print(f"Max price: £{MAX_PRICE}")
    print(f"Checking every {CHECK_EVERY_SECONDS} seconds...")
    print("-" * 50)

    token = get_access_token()

    while True:
        try:
            items = search_ebay(token)

            for item in items:
                item_id = item.get("itemId")

                if item_id in seen_items:
                    continue

                seen_items.add(item_id)

                if is_good_listing(item):
                    title = item.get("title", "N/A")
                    price = item.get("price", {})
                    value = price.get("value", "N/A")
                    url = item.get("itemWebUrl", "N/A")

                    print("\nNEW MATCH FOUND!")
                    print("Title:", title)
                    print("Price: £" + str(value))
                    print("URL:", url)
                    print("-" * 50)

            save_seen_items(seen_items)

        except requests.exceptions.HTTPError as e:
            print("HTTP error:", e)

            if "401" in str(e):
                print("Refreshing token...")
                token = get_access_token()

        except Exception as e:
            print("Error:", e)

        time.sleep(CHECK_EVERY_SECONDS)


if __name__ == "__main__":
    main()