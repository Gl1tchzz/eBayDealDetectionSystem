import requests

from src.musicmagpie_macbook import get_musicmagpie_price
from src.ps5_resell import get_ps5_resell_price


class DiscordNotifier:
    def __init__(
        self,
        macbook_webhook_url,
        macbook_auction_webhook_url,
        ps5_webhook_url,
        ps5_auction_webhook_url,
    ):
        self.macbook_webhook_url = macbook_webhook_url
        self.macbook_auction_webhook_url = macbook_auction_webhook_url
        self.ps5_webhook_url = ps5_webhook_url
        self.ps5_auction_webhook_url = ps5_auction_webhook_url

    def send_listing(self, listing, category):
        description, is_profitable = self.build_description(
            listing=listing,
            category=category,
            price_label="eBay Price",
            include_auction_end=False,
        )

        footer_text = self.footer_for(category, is_auction=False)

        embed = self.build_embed(
            listing=listing,
            description=description,
            color=16711680 if is_profitable else 5814783,
            footer_text=footer_text,
        )

        content = f"🚨 New {category.name} listing found!"

        if is_profitable:
            content = f"@everyone 🔥 PROFITABLE FLIP | {category.name}"

        self.post_to_discord(
            webhook_url=self.webhook_for(category, is_auction=False),
            content=content,
            embed=embed,
        )

    def send_auction_listing(self, listing, category):
        description, is_profitable = self.build_description(
            listing=listing,
            category=category,
            price_label="Current Bid",
            include_auction_end=True,
        )

        embed = self.build_embed(
            listing=listing,
            description=description,
            color=16753920 if not is_profitable else 16711680,
            footer_text=self.footer_for(category, is_auction=True),
        )

        content = f"🔨 Auction ending soon: {category.name}"

        if is_profitable:
            content = f"@everyone 🔨🔥 Profitable auction ending soon | {category.name}"

        self.post_to_discord(
            webhook_url=self.webhook_for(category, is_auction=True),
            content=content,
            embed=embed,
        )

    def webhook_for(self, category, is_auction):
        if category.product_type == "ps5":
            return self.ps5_auction_webhook_url if is_auction else self.ps5_webhook_url

        return self.macbook_auction_webhook_url if is_auction else self.macbook_webhook_url

    def footer_for(self, category, is_auction):
        product = "PS5" if category.product_type == "ps5" else "MacBook"
        listing_type = "Auction" if is_auction else "Tracker"
        return f"eBay {product} {listing_type}"

    def build_description(self, listing, category, price_label, include_auction_end):
        if category.product_type == "ps5":
            return self.build_ps5_description(
                listing=listing,
                category=category,
                price_label=price_label,
                include_auction_end=include_auction_end,
            )

        return self.build_macbook_description(
            listing=listing,
            category=category,
            price_label=price_label,
            include_auction_end=include_auction_end,
        )

    def build_macbook_description(self, listing, category, price_label, include_auction_end):
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

        mm_prices = self.get_macbook_resell_prices(listing)

        if mm_prices:
            description, is_profitable = self.add_macbook_resell_section(
                description=description,
                listing=listing,
                mm_prices=mm_prices,
            )
        else:
            description += "\n\n_Resell price unavailable for this model_"
            is_profitable = False

        return description, is_profitable

    def build_ps5_description(self, listing, category, price_label, include_auction_end):
        ps5_specs = listing.ps5_specs

        description = (
            f"**Category:** {category.name}\n"
            f"**{price_label}:** £{listing.price}\n"
            f"**Max Price:** £{category.max_price}\n\n"
            f"**Edition:** {ps5_specs['edition']}\n"
            f"**Controllers:** {ps5_specs['controllers']}"
        )

        if include_auction_end:
            if listing.item_end_date:
                description += f"\n**Ends:** {listing.item_end_date}"
            description += "\n\n⏰ **Auction ending within 24 hours**"

        resell = get_ps5_resell_price(
            edition=ps5_specs["edition"],
            controller_count=ps5_specs["controllers"],
        )

        if not resell:
            description += "\n\n_PS5 resell price unavailable_"
            return description, False

        profit = round(resell["total"] - listing.price, 2)
        is_profitable = profit > 0
        sign = "+" if profit >= 0 else ""

        description += (
            "\n\n**💰 PS5 Resell Estimate:**\n"
            f"Base trade-in: £{resell['base']}\n"
            f"Controller bonus: £{resell['controller_bonus']}\n"
            f"Estimated total: £{resell['total']} ({sign}£{profit})"
        )

        return description, is_profitable

    def build_embed(self, listing, description, color, footer_text):
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

    def get_macbook_resell_prices(self, listing):
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
            print(f"[DiscordNotifier] Could not get MacBook resell price: {error}")
            return None

    def add_macbook_resell_section(self, description, listing, mm_prices):
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