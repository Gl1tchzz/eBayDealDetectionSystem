"""
Handles all communication with eBay APIs.

Responsible for:
- Authentication
- Token management
- Listing searches
"""

import base64
import time
import requests


class EbayClient:

    def __init__(self, client_id, client_secret):

        self.client_id = client_id
        self.client_secret = client_secret

        # Cached OAuth token
        self.token = None

        # Time token was created
        self.token_created_at = 0

    def get_access_token(self):
        """
        Requests a new OAuth token from eBay.
        """

        credentials = (
            f"{self.client_id}:{self.client_secret}"
        )

        encoded = (
            base64.b64encode(credentials.encode())
            .decode()
        )

        response = requests.post(
            "https://api.ebay.com/identity/v1/oauth2/token",
            headers={
                "Content-Type":
                "application/x-www-form-urlencoded",
                "Authorization":
                f"Basic {encoded}",
            },
            data={
                "grant_type":
                "client_credentials",
                "scope":
                "https://api.ebay.com/oauth/api_scope",
            },
        )

        response.raise_for_status()

        self.token = response.json()["access_token"]

        self.token_created_at = time.time()

        return self.token

    def get_valid_token(self):
        """
        Returns existing token or refreshes it
        if expired.
        """

        if self.token is None:
            return self.get_access_token()

        if (
            time.time()
            - self.token_created_at
            > 7000
        ):
            return self.get_access_token()

        return self.token

    def search(self, query, max_price):
        """
        Searches eBay for matching listings.
        """

        token = self.get_valid_token()

        response = requests.get(
            "https://api.ebay.com/buy/browse/v1/item_summary/search",
            headers={
                "Authorization":
                f"Bearer {token}",
                "X-EBAY-C-MARKETPLACE-ID":
                "EBAY_GB",
            },
            params={
                "q": query,
                "category_ids": "111422",
                "filter":
                f"price:[0..{max_price}],"
                f"priceCurrency:GBP,"
                f"buyingOptions:{{FIXED_PRICE}}",
                "sort": "newlyListed",
                "limit": "50",
            },
        )

        response.raise_for_status()

        return response.json().get(
            "itemSummaries",
            [],
        )