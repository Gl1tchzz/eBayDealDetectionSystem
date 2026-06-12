"""
Main tracker loop.

Searches eBay for matching MacBook listings and sends Discord alerts.
"""

import time
import requests

from src.listing import Listing


class EbayTracker:
    """
    Runs Buy It Now and auction searches.
    """

    def __init__(
        self,
        ebay_client,
        notifier,
        seen_items_manager,
        search_categories,
        check_every_seconds,
    ):
        self.ebay_client = ebay_client
        self.notifier = notifier
        self.seen_items_manager = seen_items_manager
        self.search_categories = search_categories
        self.check_every_seconds = check_every_seconds

        self.seen_items = self.seen_items_manager.load()

    def is_good_listing(self, listing, category):
        """
        Checks whether a listing matches category rules.
        """

        title = listing.title_lower()

        if not all(word in title for word in category.required_words):
            return False

        if any(word in title for word in category.banned_words):
            return False

        return listing.price <= category.max_price

    def log_match(self, listing, category):
        """
        Logs a matching listing to the command line.
        """

        specs = listing.specs

        print("\n" + "=" * 60)
        print("🚨 NEW MATCH FOUND")
        print("=" * 60)
        print(f"Category : {category.name}")
        print(f"Title    : {listing.title}")
        print(f"Price    : £{listing.price}")
        print(f"Model    : {specs['model']}")
        print(f"CPU      : {specs['cpu']}")
        print(f"RAM      : {specs['ram']}")
        print(f"Storage  : {specs['storage']}")
        print(f"Year     : {specs['year']}")
        print(f"Size     : {specs['screen_size']}")

        if listing.item_end_date:
            print(f"Ends     : {listing.item_end_date}")

        print(f"URL      : {listing.url}")
        print("=" * 60)

    def process_fixed_price_category(self, category):
        """
        Searches and processes Buy It Now listings for one category.
        """

        print(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Searching Buy It Now: {category.name}"
        )

        items = self.ebay_client.search(
            query=category.query,
            max_price=category.max_price,
        )

        print(f"Found {len(items)} Buy It Now listings")

        for item in items:
            listing = Listing(item)

            if not listing.id:
                continue

            seen_key = f"FIXED:{category.name}:{listing.id}"

            if seen_key in self.seen_items:
                continue

            self.seen_items.add(seen_key)

            if self.is_good_listing(listing, category):
                self.log_match(listing, category)

                try:
                    self.notifier.send_listing(
                        listing=listing,
                        category=category,
                    )

                    time.sleep(2)

                except requests.exceptions.HTTPError as error:
                    print("Discord HTTP error:", error)

                    if error.response is not None and error.response.status_code == 429:
                        print("Rate limited. Waiting 10 seconds...")
                        time.sleep(10)

    def process_auction_category(self, category):
        """
        Searches and processes auction listings for one category.
        """

        print(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Searching auctions ending soon: {category.name}"
        )

        items = self.ebay_client.search_auctions_ending_soon(
            query=category.query,
            max_price=category.max_price,
        )

        print(f"Found {len(items)} auction listings")

        for item in items:
            listing = Listing(item)

            if not listing.id:
                continue

            seen_key = f"AUCTION:{category.name}:{listing.id}"

            if seen_key in self.seen_items:
                continue

            self.seen_items.add(seen_key)

            if self.is_good_listing(listing, category):
                self.log_match(listing, category)

                try:
                    self.notifier.send_auction_listing(
                        listing=listing,
                        category=category,
                    )

                    time.sleep(2)

                except requests.exceptions.HTTPError as error:
                    print("Discord auction HTTP error:", error)

                    if error.response is not None and error.response.status_code == 429:
                        print("Auction webhook rate limited. Waiting 10 seconds...")
                        time.sleep(10)

    def run(self):
        """
        Runs the tracker forever until stopped.
        """

        print("Starting multi-MacBook tracker...")
        print(f"Checking every {self.check_every_seconds} seconds")
        print("-" * 60)

        while True:
            try:
                for category in self.search_categories:
                    self.process_fixed_price_category(category)
                    self.process_auction_category(category)

                    self.seen_items_manager.save(self.seen_items)

            except requests.exceptions.HTTPError as error:
                print("eBay HTTP error:", error)

            except KeyboardInterrupt:
                print("\nTracker stopped by user.")
                self.seen_items_manager.save(self.seen_items)
                break

            except Exception as error:
                print("Unexpected error:", error)

            time.sleep(self.check_every_seconds)