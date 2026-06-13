import json
import os


class SeenItemsManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def load(self):
        if not os.path.exists(self.file_path):
            return set()

        try:
            with open(self.file_path, "r") as file:
                return set(json.load(file))

        except json.JSONDecodeError:
            print("[SeenItemsManager] seen_items.json was invalid. Starting fresh.")
            return set()

    def save(self, seen_items):
        with open(self.file_path, "w") as file:
            json.dump(sorted(list(seen_items)), file, indent=2)