import json
import os


class SeenItemsManager:
    def __init__(self, file_path):
        self.file_path = file_path

        parent_directory = os.path.dirname(file_path)

        if parent_directory:
            os.makedirs(parent_directory, exist_ok=True)

    def load(self):
        if not os.path.exists(self.file_path):
            return set()

        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                return set(json.load(file))

        except (json.JSONDecodeError, OSError) as error:
            print(
                f"[SeenItemsManager] Could not load "
                f"{self.file_path}: {error}"
            )
            return set()

    def save(self, seen_items):
        temporary_path = f"{self.file_path}.tmp"

        with open(temporary_path, "w", encoding="utf-8") as file:
            json.dump(
                sorted(seen_items),
                file,
                indent=2,
            )

        os.replace(temporary_path, self.file_path)