"""
Handles persistence of seen listing IDs.

Prevents duplicate Discord alerts.
"""

import json
import os


class SeenItemsManager:

    def __init__(self, file_path):
        self.file_path = file_path

    def load(self):
        """
        Loads previously-seen listing IDs.
        """

        if not os.path.exists(
            self.file_path
        ):
            return set()

        with open(
            self.file_path,
            "r",
        ) as file:

            return set(
                json.load(file)
            )

    def save(self, seen_items):
        """
        Saves listing IDs to disk.
        """

        with open(
            self.file_path,
            "w",
        ) as file:

            json.dump(
                list(seen_items),
                file,
            )