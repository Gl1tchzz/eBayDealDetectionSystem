"""
Extracts MacBook specs from eBay listing titles.

The eBay API does not always provide clean structured specs,
so this parser uses the listing title as the main source.
"""

import re


class SpecParser:
    """
    Parses useful MacBook details from a listing title.
    """

    @staticmethod
    def parse(title):
        """
        Returns a dictionary of extracted specs.
        """

        title_lower = title.lower()

        return {
            "model": SpecParser.extract_model(title_lower),
            "screen_size": SpecParser.extract_screen_size(title_lower),
            "cpu": SpecParser.extract_cpu(title_lower),
            "ram": SpecParser.extract_ram(title_lower),
            "storage": SpecParser.extract_storage(title_lower),
            "year": SpecParser.extract_year(title_lower),
        }

    @staticmethod
    def extract_model(title):
        """
        Determines whether the listing is a MacBook Air or MacBook Pro.

        This is important because a 13-inch M1 MacBook can be either:
        - MacBook Air M1
        - MacBook Pro M1

        Both may share the same size, year, chip and RAM,
        but they have different MusicMagpie barcodes.
        """

        if "macbook air" in title:
            return "Air"

        if "macbook pro" in title:
            return "Pro"

        return "Unknown"

    @staticmethod
    def extract_screen_size(title):
        """
        Extracts the screen size from the listing title.

        Normalises common Apple display sizes:
        - 13.3 -> 13
        - 14.2 -> 14
        - 16.2 -> 16
        """

        match = re.search(
            r"(13|13\.3|14|14\.2|15|16|16\.2)[\s-]?(inch|in|\"|'')?",
            title,
        )

        if match:
            size = match.group(1)

            if size == "13.3":
                size = "13"
            elif size == "14.2":
                size = "14"
            elif size == "16.2":
                size = "16"

            return size + '"'

        return "Unknown"

    @staticmethod
    def extract_cpu(title):
        """
        Extracts the CPU / Apple Silicon chip from the title.
        """

        cpu_patterns = [
            "m3 max",
            "m3 pro",
            "m3",
            "m2 max",
            "m2 pro",
            "m2",
            "m1 max",
            "m1 pro",
            "m1",
            "intel i9",
            "intel i7",
            "intel i5",
            "i9",
            "i7",
            "i5",
        ]

        for cpu in cpu_patterns:
            if cpu in title:
                return cpu.upper()

        return "Unknown"

    @staticmethod
    def extract_ram(title):
        """
        Extracts RAM amount from the listing title.
        """

        match = re.search(
            r"(\d+)\s?(gb)\s?(ram|memory)?",
            title,
        )

        if match:
            return match.group(1) + "GB"

        return "Unknown"

    @staticmethod
    def extract_storage(title):
        """
        Extracts storage size from the listing title.

        Uses all GB/TB matches and skips values that look like RAM.
        """

        matches = re.findall(
            r"(\d+)\s?(tb|gb)\s?(ssd|storage|ram|memory)?",
            title,
        )

        for match in matches:
            size = match[0]
            unit = match[1].upper()
            label = match[2].lower() if match[2] else ""

            if label in ["ram", "memory"]:
                continue

            return size + unit

        return "Unknown"

    @staticmethod
    def extract_year(title):
        """
        Extracts year from title.

        If no year is present, it infers the likely year from the CPU.
        """

        match = re.search(
            r"(2016|2017|2018|2019|2020|2021|2022|2023|2024|2025)",
            title,
        )

        if match:
            return match.group(1)

        if "m1 pro" in title:
            return "2021"

        if "m1 max" in title:
            return "2021"

        if "m1" in title:
            return "2020"

        if "m2 pro" in title:
            return "2023"

        if "m2 max" in title:
            return "2023"

        if "m2" in title:
            return "2022"

        if "m3 pro" in title:
            return "2023"

        if "m3 max" in title:
            return "2023"

        if "m3" in title:
            return "2023"

        if "i9" in title:
            return "2019-2020"

        if "i7" in title:
            return "2016-2020"

        if "i5" in title:
            return "2013-2020"

        return "Unknown"