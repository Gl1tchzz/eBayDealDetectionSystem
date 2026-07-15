import os
from pathlib import Path

from dotenv import load_dotenv

from src.search_category import SearchCategory


class Config:
    def __init__(self):
        load_dotenv()

        project_root = Path(__file__).resolve().parent.parent

        default_data_directory = project_root / "data"
        default_data_directory.mkdir(parents=True, exist_ok=True)

        self.ebay_credentials = [
            {
                "client_id": os.getenv("EBAY_CLIENT_ID_1"),
                "client_secret": os.getenv("EBAY_CLIENT_SECRET_1"),
            },
            {
                "client_id": os.getenv("EBAY_CLIENT_ID_2"),
                "client_secret": os.getenv("EBAY_CLIENT_SECRET_2"),
            },
            {
                "client_id": os.getenv("EBAY_CLIENT_ID_3"),
                "client_secret": os.getenv("EBAY_CLIENT_SECRET_3"),
            },
        ]

        self.ebay_credentials = [
            credential
            for credential in self.ebay_credentials
            if credential["client_id"] and credential["client_secret"]
        ]

        self.discord_macbook_webhook_url = (
            os.getenv("DISCORD_MACBOOK_WEBHOOK_URL")
            or os.getenv("DISCORD_WEBHOOK_URL")
        )

        self.discord_macbook_auction_webhook_url = (
            os.getenv("DISCORD_MACBOOK_AUCTION_WEBHOOK_URL")
            or os.getenv("DISCORD_AUCTION_WEBHOOK_URL")
        )

        self.discord_ps5_webhook_url = os.getenv("DISCORD_PS5_WEBHOOK_URL")
        self.discord_ps5_auction_webhook_url = os.getenv("DISCORD_PS5_AUCTION_WEBHOOK_URL")

        self.check_every_seconds = int(os.getenv("CHECK_EVERY_SECONDS", "300"))

        self.seen_file = os.getenv(
            "SEEN_ITEMS_FILE",
            str(default_data_directory / "seen_items.json"),
        )

        self.banned_words = [
            "case",
            "cover",
            "screen protector",
            "keyboard",
            "charger",
            "box only",
            "for parts",
            "for part",
            "spares",
            "repair",
            "faulty",
            "fault",
            "icloud",
            "locked",
            "broken",
            "damaged",
            "cracked",
            "non-working",
            "azerty",
            "qwertz",
            "grade d",
            "smashed screen",
            "display issue",
            "water damage",
            "read description",
            "lines on screen",
            "dead battery",
            "bad battery",
            "screen lines",
            "line on screen",
            "screen replacement",
            "replacement",
            "protector",
        ]

        self.ps5_banned_words = [
            "box only",
            "empty box",
            "repair",
            "parts",
            "spares",
            "broken",
            "faulty",
            "fault",
            "shell",
            "case",
            "cover",
            "controller only",
            "controllers only",
            "pad only",
            "hdmi",
            "cable",
            "stand",
            "skin",
            "account",
            "banned",
            "read description",
            "disc only",
            "game only",
            "bundle games only",
            "portal",
            "safe mode issue",
            "no power",
            "not working",
            "not turning on",
            "PS5 Disc Drive Model CFI ZDD1 SONY",
            "Lumo 2",
            "charging dock",
            "charging station",
            "Demon Slayer",
            "Earthion Deluxe Edition",
            "Bitmap Desk Collection",
            "HONCAM CONSOLE FACEPLATE",
            "Logitech",
            "POWER EJECT BUTTON",
            "PORT",
            "EDL-020",
            "Camera",
            "Not powering on",
            "HORI NOLVA",
            "Rayman 30th Anniversary Edition",
            "Gimmick 2 Collectors Edition",
            "SAROS",
            "Collection",
            "POKÉMON",
            "Spare",
            "Stick",
            "Joystick",
            "Replacement",
            "Connector",
            "SWITCH BOARD",
            "Mortal Kombat",
            "Pannels",
            "Heatsink",
            "Heatshield",
            "Far Cry 6",
            "Bundle",
            "Plates",
            "Japan",
            "Deluxe",
            "PS4",
            "Disk Drive",
            "Light",
            "Box",
            "Plastic",
            "New",
            "Disc Drive",
            "Mount",
            "Creed",
            "Logo",
            "Tablet",
            "Power",
            "Panels",
            "Design",
            "Button",
            "Fan",
            "LED",
            "Board",
            "Professional Baseball Spirits",
            "Unopened",
            "Dock",
            "Remote Player",
            "CONSOLE MANUAL SONY PS5 PLAYSTATION 5 PAL EUR FAT ",
            "THE BOYS",
            "Headset",
            "DC",
            "Wildermyth",
            "Special Edition",
            "GPU BRACE CLAMP",
            "Rare",
            "Edition",
            "Monitor",
            "God of War",
            "Wheel",
            "Spider-man",
            "Motor",
            "Poster",
            "Cooling",
            "Crew",
            "Clamp"
        ]

        self.search_categories = [
            SearchCategory(
                name="PlayStation 5 Disc Edition",
                query="PS5 Console",
                max_price=290,
                required_words=["ps5"],
                banned_words=self.ps5_banned_words + ["digital", "slim", "pro"],
                product_type="ps5",
                category_ids="139971",
            ),
            SearchCategory(
                name="PlayStation 5 Digital Edition",
                query="PS5 Digital Console",
                max_price=290,
                required_words=["ps5", "digital"],
                banned_words=self.ps5_banned_words + ["slim", "pro"],
                product_type="ps5",
                category_ids="139971",
            ),
            SearchCategory(
                name="PlayStation 5 Slim Disc Edition",
                query="PS5 Slim Console",
                max_price=300,
                required_words=["ps5", "slim"],
                banned_words=self.ps5_banned_words + ["digital", "pro"],
                product_type="ps5",
                category_ids="139971",
            ),
            SearchCategory(
                name="PlayStation 5 Slim Digital Edition",
                query="PS5 Slim Digital Console",
                max_price=300,
                required_words=["ps5", "slim", "digital"],
                banned_words=self.ps5_banned_words + ["pro"],
                product_type="ps5",
                category_ids="139971",
            ),
            SearchCategory(
                name="PlayStation 5 Pro",
                query="PS5 Pro Console",
                max_price=500,
                required_words=["ps5", "pro"],
                banned_words=self.ps5_banned_words,
                product_type="ps5",
                category_ids="139971",
            ),
        ]

        # self.search_categories = [
        #     SearchCategory(
        #         name="MacBook Pro M1",
        #         query="MacBook Pro M1",
        #         max_price=450,
        #         required_words=["macbook", "pro", "m1"],
        #         banned_words=self.banned_words + ["m1 pro", "m1 max"],
        #         product_type="macbook",
        #         category_ids="111422",
        #     ),
        #     SearchCategory(
        #         name="MacBook Pro M1 Pro",
        #         query="MacBook Pro M1 Pro",
        #         max_price=600,
        #         required_words=["macbook", "pro", "m1 pro"],
        #         banned_words=self.banned_words,
        #         product_type="macbook",
        #     ),
        #     SearchCategory(
        #         name="MacBook Pro M1 Max",
        #         query="MacBook Pro M1 Max",
        #         max_price=700,
        #         required_words=["macbook", "pro", "m1 max"],
        #         banned_words=self.banned_words,
        #         product_type="macbook",
        #     ),
        #     SearchCategory(
        #         name="MacBook Pro M2 Pro",
        #         query="MacBook Pro M2 Pro",
        #         max_price=850,
        #         required_words=["macbook", "pro", "m2 pro"],
        #         banned_words=self.banned_words,
        #         product_type="macbook",
        #     ),
        #     SearchCategory(
        #         name="MacBook Air M1",
        #         query="MacBook Air M1",
        #         max_price=400,
        #         required_words=["macbook", "air", "m1"],
        #         banned_words=self.banned_words,
        #         product_type="macbook",
        #     ),
        #     SearchCategory(
        #         name="MacBook Air M2",
        #         query="MacBook Air M2",
        #         max_price=600,
        #         required_words=["macbook", "air", "m2"],
        #         banned_words=self.banned_words,
        #         product_type="macbook",
        #     ),
        #     SearchCategory(
        #         name="PlayStation 5 Disc Edition",
        #         query="PlayStation 5 Console Disc",
        #         max_price=280,
        #         required_words=["playstation 5"],
        #         banned_words=self.ps5_banned_words + ["digital", "slim", "pro"],
        #         product_type="ps5",
        #     ),
        #     SearchCategory(
        #         name="PlayStation 5 Digital Edition",
        #         query="PlayStation 5 Digital Edition",
        #         max_price=230,
        #         required_words=["digital"],
        #         banned_words=self.ps5_banned_words + ["slim", "pro"],
        #         product_type="ps5",
        #     ),
        #     SearchCategory(
        #         name="PlayStation 5 Slim Disc Edition",
        #         query="PlayStation 5 Slim Disc",
        #         max_price=320,
        #         required_words=["slim"],
        #         banned_words=self.ps5_banned_words + ["digital", "pro"],
        #         product_type="ps5",
        #     ),
        #     SearchCategory(
        #         name="PlayStation 5 Slim Digital Edition",
        #         query="PlayStation 5 Slim Digital",
        #         max_price=270,
        #         required_words=["slim", "digital"],
        #         banned_words=self.ps5_banned_words + ["pro"],
        #         product_type="ps5",
        #     ),
        #     SearchCategory(
        #         name="PlayStation 5 Pro",
        #         query="PlayStation 5 Pro",
        #         max_price=500,
        #         required_words=["pro"],
        #         banned_words=self.ps5_banned_words,
        #         product_type="ps5",
        #     ),
        # ]

        self.validate()

    def validate(self):
        if not self.ebay_credentials:
            raise ValueError("No eBay API credentials found.")

        if not self.discord_macbook_webhook_url:
            raise ValueError("DISCORD_MACBOOK_WEBHOOK_URL missing")

        if not self.discord_macbook_auction_webhook_url:
            raise ValueError("DISCORD_MACBOOK_AUCTION_WEBHOOK_URL missing")

        if not self.discord_ps5_webhook_url:
            raise ValueError("DISCORD_PS5_WEBHOOK_URL missing")

        if not self.discord_ps5_auction_webhook_url:
            raise ValueError("DISCORD_PS5_AUCTION_WEBHOOK_URL missing")