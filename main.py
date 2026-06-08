"""
Application entry point.

Creates all required objects and injects dependencies
into the EbayTracker before starting the tracking loop.
"""

from src.config import Config
from src.ebay_client import EbayClient
from src.discord_notifier import DiscordNotifier
from src.seen_items_manager import SeenItemsManager
from src.tracker import EbayTracker


def main():
    """
    Creates application services and starts tracking.
    """

    config = Config()

    ebay_client = EbayClient(
        client_id=config.ebay_client_id,
        client_secret=config.ebay_client_secret,
    )

    notifier = DiscordNotifier(
        webhook_url=config.discord_webhook_url,
    )

    seen_items_manager = SeenItemsManager(
        file_path=config.seen_file,
    )

    tracker = EbayTracker(
        ebay_client=ebay_client,
        notifier=notifier,
        seen_items_manager=seen_items_manager,
        search_query=config.search_query,
        max_price=config.max_price,
        check_every_seconds=config.check_every_seconds,
    )

    tracker.run()


if __name__ == "__main__":
    main()