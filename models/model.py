import json
import sys

from prompt_toolkit import prompt


class CheatSheet:
    def __init__(self, filename="cheatsheet.json"):
        self._filename = filename
        data = self.load() or {}
        self._commands = data["commands"]
        self.categories = data["categories"]
        self.filtered_commands = self._commands.copy()

    def search(self, query: str):
        def search_in_commands():
            nonlocal query
            query = query[1:].strip()
            return [
                command for command in self._commands if query in command["cmd"].lower()
            ]

        def search_in_categories():
            return [
                command
                for command in self._commands
                if all(
                    category in [c.lower() for c in command["categories"]]
                    for category in query.split()
                )
            ]

        query = query.strip().lower()

        self.filtered_commands = (
            search_in_commands() if query.startswith("/") else search_in_categories()
        )

    def delete_last_command(self):
        self._commands.pop()

    def delete_command(self, index):
        target = self.filtered_commands[index]
        self.filtered_commands.remove(target)
        self._commands.remove(target)

    def add_empty_command(self):
        self._commands.append(
            {
                "cmd": "",
                "desc": "",
                "notes": "",
                "categories": [],
            }
        )

        return self._commands[-1]

    def add_command(self, data):
        self._commands.append(data)
        self.save()

    def add_categories(self, items: list):
        self.categories.extend(items)

    def remove_categories(self, items: list):
        for item in items:
            if item in self.categories:
                self.categories.remove(item)

    def get_filtered_command_data(self, index):
        return self.filtered_commands[index]

    def load(self):
        try:
            with open(self._filename, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            if self._filename != "cheatsheet.json":
                print(f"File does not exist: {self._filename}")
                print("It will be created after creating your first command.")
                choice = prompt("Proceed? [y/N]: ")

                if choice not in ["y", "yes"]:
                    sys.exit()

    def save(self):
        with open(self._filename, "w") as file:
            data = {"categories": self.categories, "commands": self._commands}
            json.dump(data, file, indent=4)
