import time
from datetime import datetime, timedelta, timezone

import requests

from src.listing import Listing


class EbayTracker:
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
        title = listing.title_lower()

        if not all(word.lower() in title for word in category.required_words):
            return False

        if any(word.lower() in title for word in category.banned_words):
            return False

        return listing.price <= category.max_price

    def auction_ends_within_24_hours(self, listing):
        if not listing.item_end_date:
            return False

        try:
            end_time = datetime.fromisoformat(
                listing.item_end_date.replace("Z", "+00:00")
            )

            now = datetime.now(timezone.utc)
            return now <= end_time <= now + timedelta(hours=24)

        except Exception:
            return False

    def log_match(self, listing, category):
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

    def print_fixed_summary(self, category, found_count, posted_count, skipped_count):
        print("\n" + "-" * 60)
        print(f"🛒 Buy It Now summary: {category.name}")
        print("-" * 60)
        print(f"Found         : {found_count}")
        print(f"Posted        : {posted_count}")
        print(f"Skipped/Seen  : {skipped_count}")
        print("-" * 60 + "\n")

    def print_auction_summary(self, category, found_count, stats):
        print("\n" + "-" * 60)
        print(f"🔨 Auction summary: {category.name}")
        print("-" * 60)
        print(f"Found         : {found_count}")
        print(f"Posted        : {stats['posted']}")
        print(f"Already seen  : {stats['already_seen']}")
        print(f"Not ending 24h: {stats['not_ending_24h']}")
        print(f"Failed filters: {stats['failed_filters']}")
        print(f"Duplicates    : {stats['duplicates']}")
        print(f"Missing ID    : {stats['missing_id']}")
        print("-" * 60 + "\n")

    def process_fixed_price_category(self, category):
        print(
            f"[{time.strftime('%H:%M:%S')}] "
            f"🛒 Buy It Now: {category.name}"
        )

        items = self.ebay_client.search(
            query=category.query,
            max_price=category.max_price,
        )

        posted_count = 0
        skipped_count = 0

        for item in items:
            listing = Listing(item)

            if not listing.id:
                skipped_count += 1
                continue

            seen_key = f"FIXED:{category.name}:{listing.id}"

            if seen_key in self.seen_items:
                skipped_count += 1
                continue

            if not self.is_good_listing(listing, category):
                skipped_count += 1
                continue

            self.seen_items.add(seen_key)
            self.seen_items_manager.save(self.seen_items)

            self.log_match(listing, category)

            try:
                self.notifier.send_listing(
                    listing=listing,
                    category=category,
                )

                posted_count += 1
                time.sleep(2)

            except requests.exceptions.HTTPError as error:
                print(f"Discord HTTP error: {error}")

                if error.response is not None and error.response.status_code == 429:
                    print("Rate limited. Waiting 10 seconds...")
                    time.sleep(10)

        self.print_fixed_summary(
            category=category,
            found_count=len(items),
            posted_count=posted_count,
            skipped_count=skipped_count,
        )

    def process_auction_category(self, category):
        print(
            f"[{time.strftime('%H:%M:%S')}] "
            f"🔨 Auctions: {category.name}"
        )

        items = self.ebay_client.search_auctions_ending_soon(
            query=category.query,
            max_price=category.max_price,
        )

        stats = {
            "posted": 0,
            "already_seen": 0,
            "not_ending_24h": 0,
            "failed_filters": 0,
            "duplicates": 0,
            "missing_id": 0,
        }

        duplicate_titles_seen = set()

        for item in items:
            listing = Listing(item)

            if not listing.id:
                stats["missing_id"] += 1
                continue

            normalised_title = " ".join(
                listing.title_lower().split()
            )

            if normalised_title in duplicate_titles_seen:
                stats["duplicates"] += 1
                continue

            duplicate_titles_seen.add(normalised_title)

            seen_key = f"AUCTION:{category.name}:{listing.id}"

            if seen_key in self.seen_items:
                stats["already_seen"] += 1
                continue

            if not self.auction_ends_within_24_hours(listing):
                stats["not_ending_24h"] += 1
                continue

            if not self.is_good_listing(listing, category):
                stats["failed_filters"] += 1
                continue

            self.seen_items.add(seen_key)
            self.seen_items_manager.save(self.seen_items)

            self.log_match(listing, category)

            try:
                self.notifier.send_auction_listing(
                    listing=listing,
                    category=category,
                )

                stats["posted"] += 1
                time.sleep(2)

            except requests.exceptions.HTTPError as error:
                print(f"Discord auction HTTP error: {error}")

                if error.response is not None and error.response.status_code == 429:
                    print("Auction webhook rate limited. Waiting 10 seconds...")
                    time.sleep(10)

        self.print_auction_summary(
            category=category,
            found_count=len(items),
            stats=stats,
        )

    def run(self):
        print("\nStarting multi-MacBook tracker...")
        print(f"Checking every {self.check_every_seconds} seconds")
        print("=" * 60)

        while True:
            try:
                for category in self.search_categories:
                    self.process_fixed_price_category(category)
                    self.process_auction_category(category)
                    self.seen_items_manager.save(self.seen_items)

                print(
                    f"[{time.strftime('%H:%M:%S')}] "
                    f"✅ Cycle finished. Sleeping for "
                    f"{self.check_every_seconds} seconds..."
                )
                print("=" * 60)

            except requests.exceptions.HTTPError as error:
                print(f"eBay HTTP error: {error}")

            except KeyboardInterrupt:
                print("\nTracker stopped by user.")
                self.seen_items_manager.save(self.seen_items)
                break

            except Exception as error:
                print(f"Unexpected error: {error}")

            time.sleep(self.check_every_seconds)