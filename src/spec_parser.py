import re


class SpecParser:
    @staticmethod
    def parse(title):
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
        if "macbook air" in title:
            return "Air"

        if "macbook pro" in title:
            return "Pro"

        return "Unknown"

    @staticmethod
    def extract_screen_size(title):
        match = re.search(
            r"(13|13\.3|14|14\.2|15|16|16\.2)[\s-]?(inch|in|\"|'')?",
            title,
        )

        if not match:
            return "Unknown"

        size = match.group(1)

        if size == "13.3":
            size = "13"
        elif size == "14.2":
            size = "14"
        elif size == "16.2":
            size = "16"

        return size + '"'

    @staticmethod
    def extract_cpu(title):
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
        match = re.search(
            r"\b(8|16|24|32|64|96)\s?gb\s?(ram|memory|unified memory)\b",
            title,
        )

        if match:
            return match.group(1) + "GB"

        possible_ram_values = re.findall(
            r"\b(8|16|24|32|64|96)\s?gb\b",
            title,
        )

        if possible_ram_values:
            return possible_ram_values[0] + "GB"

        return "Unknown"

    @staticmethod
    def extract_storage(title):
        explicit_storage = re.findall(
            r"\b(128|256|512|1024|2048|1|2|4|8)\s?(gb|tb)\s?(ssd|storage)\b",
            title,
        )

        if explicit_storage:
            size = explicit_storage[0][0]
            unit = explicit_storage[0][1].upper()

            if unit == "GB":
                return size + "GB"

            return size + "TB"

        generic_storage = re.findall(
            r"\b(128|256|512|1024|2048)\s?gb\b|\b(1|2|4|8)\s?tb\b",
            title,
        )

        for gb_value, tb_value in generic_storage:
            if gb_value:
                return gb_value + "GB"

            if tb_value:
                return tb_value + "TB"

        return "Unknown"

    @staticmethod
    def extract_year(title):
        match = re.search(
            r"(2016|2017|2018|2019|2020|2021|2022|2023|2024|2025|2026)",
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