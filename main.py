"""
Application entry point.
"""

from src.config import Config
from src.ebay_client import EbayClient
from src.discord_notifier import DiscordNotifier
from src.seen_items_manager import SeenItemsManager
from src.tracker import EbayTracker


def main():
    """
    Creates dependencies and starts the tracker.
    """

    config = Config()

    ebay_client = EbayClient(
        client_id=config.ebay_client_id,
        client_secret=config.ebay_client_secret,
    )

    notifier = DiscordNotifier(
        webhook_url=config.discord_webhook_url,
        auction_webhook_url=config.discord_auction_webhook_url,
    )

    seen_items_manager = SeenItemsManager(
        file_path=config.seen_file,
    )

    tracker = EbayTracker(
        ebay_client=ebay_client,
        notifier=notifier,
        seen_items_manager=seen_items_manager,
        search_categories=config.search_categories,
        check_every_seconds=config.check_every_seconds,
    )

    tracker.run()


if __name__ == "__main__":
    main()