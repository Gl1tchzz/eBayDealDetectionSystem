"""
Represents a single eBay listing.

Converts raw API JSON into a Python object.
"""

class Listing:
    """
    Stores listing information in a structured format.
    """

    def __init__(self, item):

        # Raw API response
        self.raw = item

        # Unique eBay listing ID
        self.id = item.get("itemId")

        # Listing title
        self.title = item.get("title", "N/A")

        # Listing URL
        self.url = item.get("itemWebUrl", "N/A")

        # Product image
        self.image_url = (
            item.get("image", {})
            .get("imageUrl")
        )

        price_data = item.get("price", {})

        # Listing price
        self.price = float(
            price_data.get("value", 999999)
        )

        self.currency = price_data.get(
            "currency",
            "GBP",
        )

    def title_lower(self):
        """
        Convenience method for case-insensitive filtering.
        """
        return self.title.lower()