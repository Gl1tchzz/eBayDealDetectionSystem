"""
Responsible for sending alerts to Discord.
"""

import requests


class DiscordNotifier:

    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_listing(self, listing):
        """
        Sends a listing notification
        to Discord using an embed.
        """

        embed = {
            "title": listing.title[:256],
            "url": listing.url,
            "description":
            f"**Price:** £{listing.price}",
            "color": 5814783,
        }

        if listing.image_url:
            embed["thumbnail"] = {
                "url": listing.image_url
            }

        payload = {
            "content":
            "🚨 New eBay listing found!",
            "embeds": [embed],
        }

        requests.post(
            self.webhook_url,
            json=payload,
        ).raise_for_status()