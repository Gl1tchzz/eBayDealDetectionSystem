"""
Core application logic.

Coordinates:
- eBay searches
- Listing filtering
- Duplicate detection
- Command-line logging
- Discord notifications
"""

import time
import requests

from src.listing import Listing


class EbayTracker:
    """
    Main tracker class.

    This class controls the program loop and decides
    which listings should be logged and sent to Discord.
    """

    def __init__(
        self,
        ebay_client,
        notifier,
        seen_items_manager,
        search_query,
        max_price,
        check_every_seconds,
    ):
        # Handles all eBay API requests
        self.ebay_client = ebay_client

        # Handles Discord webhook alerts
        self.notifier = notifier

        # Handles saving/loading seen listing IDs
        self.seen_items_manager = seen_items_manager

        # Search configuration
        self.search_query = search_query
        self.max_price = max_price
        self.check_every_seconds = check_every_seconds

        # Load listings that have already been processed
        self.seen_items = self.seen_items_manager.load()

        # Listings must contain all of these words
        self.required_words = [
            "macbook",
            "pro",
            "m1",
        ]

        # Listings containing any of these words are ignored
        self.banned_words = [
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

    def is_good_listing(self, listing):
        """
        Checks whether a listing matches the rules.

        A good listing must:
        - contain all required words
        - not contain banned words
        - be under the maximum price
        """

        title = listing.title_lower()

        if not all(word in title for word in self.required_words):
            return False

        if any(word in title for word in self.banned_words):
            return False

        return listing.price <= self.max_price

    def log_scan(self, number_of_items):
        """
        Logs each scan to the command line.
        """

        print(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Found {number_of_items} listings"
        )

    def log_match(self, listing):
        """
        Logs a matching listing to the command line.
        """

        print("\n" + "=" * 60)
        print("🚨 NEW MATCH FOUND")
        print("=" * 60)
        print(f"Title : {listing.title}")
        print(f"Price : £{listing.price}")
        print(f"URL   : {listing.url}")
        print("=" * 60)

    def run(self):
        """
        Runs the tracker forever until manually stopped.

        Press Ctrl + C in the terminal to stop the program.
        """

        print(f"Tracking: {self.search_query}")
        print(f"Max price: £{self.max_price}")
        print(f"Checking every {self.check_every_seconds} seconds...")
        print("-" * 60)

        while True:
            try:
                items = self.ebay_client.search(
                    query=self.search_query,
                    max_price=self.max_price,
                )

                self.log_scan(len(items))

                for item in items:
                    listing = Listing(item)

                    if not listing.id:
                        continue

                    # Skip listings already processed
                    if listing.id in self.seen_items:
                        continue

                    # Mark as seen before filtering so we do not
                    # repeatedly process bad listings every scan
                    self.seen_items.add(listing.id)

                    if self.is_good_listing(listing):
                        self.log_match(listing)

                        try:
                            self.notifier.send_listing(listing)

                            # Small delay to avoid Discord webhook rate limits
                            time.sleep(2)

                        except requests.exceptions.HTTPError as error:
                            print("Discord HTTP error:", error)

                            # If Discord rate-limits us, wait longer
                            if error.response is not None and error.response.status_code == 429:
                                print("Rate limited by Discord. Waiting 10 seconds...")
                                time.sleep(10)

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