class SearchCategory:
    def __init__(
        self,
        name,
        query,
        max_price,
        required_words,
        banned_words=None,
        product_type="macbook",
    ):
        self.name = name
        self.query = query
        self.max_price = max_price
        self.required_words = required_words
        self.banned_words = banned_words or []
        self.product_type = product_type