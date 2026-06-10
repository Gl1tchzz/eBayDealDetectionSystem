"""
Sends matching MacBook listings to Discord.

Also includes MusicMagpie trade-in values when available,
so you can quickly see whether a listing is profitable.
"""

import requests

from src.musicmagpie_macbook import get_musicmagpie_price


class DiscordNotifier:
    """
    Handles sending Discord webhook alerts.
    """

    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_listing(self, listing, category):
        """
        Sends a single eBay listing to Discord.
        """

        specs = listing.specs

        description = (
            f"**Category:** {category.name}\n"
            f"**eBay Price:** £{listing.price}\n"
            f"**Max Price:** £{category.max_price}\n\n"
            f"**Model:** {specs['model']}\n"
            f"**CPU:** {specs['cpu']}\n"
            f"**RAM:** {specs['ram']}\n"
            f"**Storage:** {specs['storage']}\n"
            f"**Year:** {specs['year']}\n"
            f"**Size:** {specs['screen_size']}"
        )

        mm_prices = None
        poor_is_profitable = False

        try:
            # Convert parsed string specs into values accepted
            # by the MusicMagpie lookup function.
            model = specs["model"]
            ram_int = int(specs["ram"].replace("GB", "").strip())
            year_int = int(specs["year"])
            size_str = specs["screen_size"].replace('"', "").strip()
            chip_str = specs["cpu"]

            # Look up MusicMagpie trade-in values.
            mm_prices = get_musicmagpie_price(
                model=model,
                screen_size=size_str,
                year=year_int,
                chip=chip_str,
                ram_gb=ram_int,
            )

        except Exception as error:
            print(f"[DiscordNotifier] Could not get resell price: {error}")

        if mm_prices:
            good = mm_prices.get("good")
            poor = mm_prices.get("poor")
            faulty = mm_prices.get("faulty")

            profit_good = round(good - listing.price, 2) if good else None
            profit_poor = round(poor - listing.price, 2) if poor else None
            profit_faulty = round(faulty - listing.price, 2) if faulty else None

            # Red alert and @everyone ping only when poor condition
            # trade-in value is already profitable.
            if profit_poor is not None and profit_poor > 0:
                poor_is_profitable = True

            def fmt(value, profit):
                """
                Formats MusicMagpie value and profit into one string.
                """

                if value is None:
                    return "N/A"

                sign = "+" if profit >= 0 else ""
                return f"£{value} ({sign}£{profit})"

            description += (
                f"\n\n**💰 MusicMagpie Resell Prices:**\n"
                f"Good: {fmt(good, profit_good)}\n"
                f"Poor: {fmt(poor, profit_poor)}\n"
                f"Faulty: {fmt(faulty, profit_faulty)}"
            )

        else:
            description += "\n\n_Resell price unavailable for this model_"

        embed = {
            "title": listing.title[:256],
            "url": listing.url,
            "description": description,
            # Red if poor condition is profitable, blue otherwise.
            "color": 16711680 if poor_is_profitable else 5814783,
            "footer": {"text": "eBay MacBook Tracker"},
        }

        if listing.image_url:
            embed["thumbnail"] = {"url": listing.image_url}

        content = f"🚨 New {category.name} listing found!"

        if poor_is_profitable:
            content = (
                "@everyone 🔥 PROFITABLE FLIP — "
                f"Poor condition is in profit! | {category.name}"
            )

        payload = {
            "content": content,
            "embeds": [embed],
        }

        response = requests.post(
            self.webhook_url,
            json=payload,
        )

        response.raise_for_status()