import re


class Ps5Parser:
    @staticmethod
    def parse(title):
        title_lower = title.lower()

        return {
            "edition": Ps5Parser.extract_edition(title_lower),
            "controllers": Ps5Parser.extract_controller_count(title_lower),
        }

    @staticmethod
    def extract_edition(title):
        if "pro" in title:
            return "PlayStation 5 Pro"

        if "slim" in title and "digital" in title:
            return "PlayStation 5 Slim Digital Edition"

        if "slim" in title:
            return "PlayStation 5 Slim Disc Edition"

        if "digital" in title:
            return "PlayStation 5 Digital Edition"

        return "PlayStation 5 Disc Edition"

    @staticmethod
    def extract_controller_count(title):
        if "no controller" in title or "without controller" in title:
            return 0

        match = re.search(r"\b([2-4])\s?(controllers?|pads?)\b", title)
        if match:
            return int(match.group(1))

        if "two controller" in title or "two pad" in title:
            return 2

        if "three controller" in title or "three pad" in title:
            return 3

        return 1