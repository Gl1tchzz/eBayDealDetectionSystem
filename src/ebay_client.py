import base64
import time

import requests


class EbayClient:
    def __init__(self, credentials):
        self.credentials = credentials
        self.current_index = 0
        self.token = None
        self.token_created_at = 0

    @property
    def current_credentials(self):
        return self.credentials[self.current_index]

    def rotate_credentials(self):
        self.current_index = (self.current_index + 1) % len(self.credentials)
        self.token = None
        self.token_created_at = 0
        print(f"[eBay] Rotated API key. Now using key {self.current_index + 1}/{len(self.credentials)}")

    def get_access_token(self):
        credentials = self.current_credentials
        raw_credentials = f"{credentials['client_id']}:{credentials['client_secret']}"
        encoded = base64.b64encode(raw_credentials.encode()).decode()

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
            timeout=20,
        )

        if response.status_code == 429:
            raise requests.exceptions.HTTPError("429 while getting eBay token", response=response)

        response.raise_for_status()

        self.token = response.json()["access_token"]
        self.token_created_at = time.time()
        return self.token

    def get_valid_token(self):
        if self.token is None or time.time() - self.token_created_at > 7000:
            return self.get_access_token()
        return self.token

    def request_with_rotation(self, params):
        for _ in range(len(self.credentials)):
            token = self.get_valid_token()

            response = requests.get(
                "https://api.ebay.com/buy/browse/v1/item_summary/search",
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-EBAY-C-MARKETPLACE-ID": "EBAY_GB",
                },
                params=params,
                timeout=20,
            )

            if response.status_code == 429:
                print("[eBay] 429 Too Many Requests. Trying next API key...")
                self.rotate_credentials()
                continue

            response.raise_for_status()
            return response

        print("[eBay] All API keys are currently rate limited.")
        return None

    def search(self, query, max_price, category_ids=None):
        all_items = []
        offset = 0
        page_size = 50
        total = None

        params = {
            "q": query,
            "filter": (
                f"price:[0..{max_price}],"
                f"priceCurrency:GBP,"
                f"buyingOptions:{{FIXED_PRICE}}"
            ),
            "sort": "newlyListed",
            "limit": page_size,
        }

        if category_ids:
            params["category_ids"] = category_ids

        while True:
            params["offset"] = offset
            response = self.request_with_rotation(params=params)

            if response is None:
                break

            data = response.json()

            if total is None:
                total = data.get("total", 0)
                print(f"  (eBay reports {total} total results)")

            items = data.get("itemSummaries", [])
            all_items.extend(items)

            offset += page_size

            if offset >= min(total, 10000) or not items:
                break

            time.sleep(0.5)

        print(f"  (fetched {len(all_items)} total)")
        return all_items

    def search_auctions_ending_soon(self, query, max_price, category_ids=None):
        params = {
            "q": query,
            "filter": (
                f"price:[0..{max_price}],"
                f"priceCurrency:GBP,"
                f"buyingOptions:{{AUCTION}}"
            ),
            "sort": "endingSoonest",
            "limit": 50,
        }

        if category_ids:
            params["category_ids"] = category_ids

        response = self.request_with_rotation(params=params)

        if response is None:
            return []

        data = response.json()
        return data.get("itemSummaries", [])