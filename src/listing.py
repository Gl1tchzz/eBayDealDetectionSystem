from src.ps5_parser import Ps5Parser
from src.spec_parser import SpecParser


class Listing:
    def __init__(self, item):
        self.raw = item

        self.id = item.get("itemId")
        self.title = item.get("title", "N/A")
        self.url = item.get("itemWebUrl", "N/A")
        self.image_url = item.get("image", {}).get("imageUrl")

        price_data = item.get("price", {})
        self.price = float(price_data.get("value", 999999))
        self.currency = price_data.get("currency", "GBP")

        self.item_end_date = item.get("itemEndDate")
        self.buying_options = item.get("buyingOptions", [])

        self.specs = SpecParser.parse(self.title)
        self.ps5_specs = Ps5Parser.parse(self.title)

    def title_lower(self):
        return self.title.lower()