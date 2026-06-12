import base64
import time
import requests
from datetime import datetime, timedelta, timezone


class EbayClient:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.token_created_at = 0

    def get_access_token(self):
        credentials = f"{self.client_id}:{self.client_secret}"
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
        self.token = response.json()["access_token"]
        self.token_created_at = time.time()
        return self.token

    def get_valid_token(self):
        if self.token is None:
            return self.get_access_token()
        if time.time() - self.token_created_at > 7000:
            return self.get_access_token()
        return self.token

    def search(self, query, max_price):
        """
        Fetches ALL listings by paginating through eBay results.
        eBay allows max 50 per page and max 10,000 results (offset limit).
        """
        token = self.get_valid_token()
        all_items = []
        offset = 0
        page_size = 50
        total = None

        while True:
            response = requests.get(
                "https://api.ebay.com/buy/browse/v1/item_summary/search",
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-EBAY-C-MARKETPLACE-ID": "EBAY_GB",
                },
                params={
                    "q": query,
                    "category_ids": "111422",
                    "filter": (
                        f"price:[0..{max_price}],"
                        f"priceCurrency:GBP,"
                        f"buyingOptions:{{FIXED_PRICE}}"
                    ),
                    "sort": "newlyListed",
                    "limit": page_size,
                    "offset": offset,
                },
            )
            response.raise_for_status()
            data = response.json()

            if total is None:
                total = data.get("total", 0)
                print(f"  (eBay reports {total} total results)")

            items = data.get("itemSummaries", [])
            all_items.extend(items)

            offset += page_size

            # Stop if we've fetched everything or hit eBay's 10,000 offset limit
            if offset >= min(total, 10000) or not items:
                break

            # Small delay between pages to avoid rate limiting
            time.sleep(0.5)

        print(f"  (fetched {len(all_items)} total)")
        return all_items
    
    def search_auctions_ending_soon(self, query, max_price):
        """
        Searches auction listings only.

        Only returns auctions:
        - ending within the next 24 hours
        - with current bid price under the category max price
        """

        token = self.get_valid_token()

        now = datetime.now(timezone.utc)
        tomorrow = now + timedelta(hours=24)

        start_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time = tomorrow.strftime("%Y-%m-%dT%H:%M:%SZ")

        response = requests.get(
            "https://api.ebay.com/buy/browse/v1/item_summary/search",
            headers={
                "Authorization": f"Bearer {token}",
                "X-EBAY-C-MARKETPLACE-ID": "EBAY_GB",
            },
            params={
                "q": query,
                "category_ids": "111422",
                "filter": (
                    f"price:[0..{max_price}],"
                    f"priceCurrency:GBP,"
                    f"buyingOptions:{{AUCTION}},"
                    f"itemEndDate:[{start_time}..{end_time}]"
                ),
                "sort": "endingSoonest",
                "limit": 50,
            },
        )

        response.raise_for_status()
        data = response.json()

        return data.get("itemSummaries", [])  