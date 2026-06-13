"""
Sends matching MacBook listings to Discord.
"""

import requests

from src.musicmagpie_macbook import get_musicmagpie_price


class DiscordNotifier:
    """
    Handles Discord webhook alerts.
    """

    def __init__(self, webhook_url, auction_webhook_url):
        self.webhook_url = webhook_url
        self.auction_webhook_url = auction_webhook_url

    def send_listing(self, listing, category):
        """
        Sends Buy It Now / fixed-price listings to the normal Discord channel.
        """

        description, poor_is_profitable = self.build_description(
            listing=listing,
            category=category,
            price_label="eBay Price",
            include_auction_end=False,
        )

        embed = self.build_embed(
            listing=listing,
            description=description,
            color=16711680 if poor_is_profitable else 5814783,
            footer_text="eBay MacBook Tracker",
        )

        content = f"🚨 New {category.name} listing found!"

        if poor_is_profitable:
            content = (
                "@everyone 🔥 PROFITABLE FLIP — "
                f"Poor condition is in profit! | {category.name}"
            )

        self.post_to_discord(
            webhook_url=self.webhook_url,
            content=content,
            embed=embed,
        )

    def send_auction_listing(self, listing, category):
        """
        Sends auction listings to the separate auction Discord channel.
        """

        description, _ = self.build_description(
            listing=listing,
            category=category,
            price_label="Current Bid",
            include_auction_end=True,
        )

        embed = self.build_embed(
            listing=listing,
            description=description,
            color=16753920,
            footer_text="eBay MacBook Auction Tracker",
        )

        self.post_to_discord(
            webhook_url=self.auction_webhook_url,
            content=f"🔨 Auction ending soon: {category.name}",
            embed=embed,
        )

    def build_description(self, listing, category, price_label, include_auction_end):
        """
        Builds the Discord embed description.

        Used by both Buy It Now and auction alerts.
        """

        specs = listing.specs

        description = (
            f"**Category:** {category.name}\n"
            f"**{price_label}:** £{listing.price}\n"
            f"**Max Price:** £{category.max_price}\n\n"
            f"**Model:** {specs['model']}\n"
            f"**CPU:** {specs['cpu']}\n"
            f"**RAM:** {specs['ram']}\n"
            f"**Storage:** {specs['storage']}\n"
            f"**Year:** {specs['year']}\n"
            f"**Size:** {specs['screen_size']}"
        )

        if include_auction_end:
            if listing.item_end_date:
                description += f"\n**Ends:** {listing.item_end_date}"

            description += "\n\n⏰ **Auction ending within 24 hours**"

        mm_prices = self.get_resell_prices(listing)

        if mm_prices:
            description, poor_is_profitable = self.add_resell_section(
                description=description,
                listing=listing,
                mm_prices=mm_prices,
            )
        else:
            description += "\n\n_Resell price unavailable for this model_"
            poor_is_profitable = False

        return description, poor_is_profitable

    def build_embed(self, listing, description, color, footer_text):
        """
        Builds the Discord embed object.
        """

        embed = {
            "title": listing.title[:256],
            "url": listing.url,
            "description": description,
            "color": color,
            "footer": {"text": footer_text},
        }

        if listing.image_url:
            embed["thumbnail"] = {"url": listing.image_url}

        return embed

    def get_resell_prices(self, listing):
        """
        Looks up MusicMagpie prices using the parsed listing specs.
        """

        specs = listing.specs

        try:
            model = specs["model"]
            ram_int = int(specs["ram"].replace("GB", "").strip())
            year_int = int(specs["year"])
            size_str = specs["screen_size"].replace('"', "").strip()
            chip_str = specs["cpu"]

            return get_musicmagpie_price(
                model=model,
                screen_size=size_str,
                year=year_int,
                chip=chip_str,
                ram_gb=ram_int,
            )

        except Exception as error:
            print(f"[DiscordNotifier] Could not get resell price: {error}")
            return None

    def add_resell_section(self, description, listing, mm_prices):
        """
        Adds MusicMagpie price and profit calculations to Discord embed.
        """

        good = mm_prices.get("good")
        poor = mm_prices.get("poor")
        faulty = mm_prices.get("faulty")

        profit_good = round(good - listing.price, 2) if good else None
        profit_poor = round(poor - listing.price, 2) if poor else None
        profit_faulty = round(faulty - listing.price, 2) if faulty else None

        poor_is_profitable = profit_poor is not None and profit_poor > 0

        def fmt(value, profit):
            if value is None or profit is None:
                return "N/A"

            sign = "+" if profit >= 0 else ""
            return f"£{value} ({sign}£{profit})"

        description += (
            f"\n\n**💰 MusicMagpie Resell Prices:**\n"
            f"Good: {fmt(good, profit_good)}\n"
            f"Poor: {fmt(poor, profit_poor)}\n"
            f"Faulty: {fmt(faulty, profit_faulty)}"
        )

        return description, poor_is_profitable

    def post_to_discord(self, webhook_url, content, embed):
        """
        Sends a Discord webhook payload.
        """

        payload = {
            "content": content,
            "embeds": [embed],
        }

        response = requests.post(
            webhook_url,
            json=payload,
            timeout=20,
        )

        response.raise_for_status()