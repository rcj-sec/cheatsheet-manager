import json
import re
import sys

from prompt_toolkit import prompt

DEFAULT_JSON_FILE = "cheatsheet.json"


class CheatSheet:
    def __init__(self, filename=DEFAULT_JSON_FILE):
        self._filename = filename
        data = self.load() or {}
        self._commands = data["commands"]
        self.categories = data["categories"]
        self.filtered_commands = self._commands.copy()

    def search(self, query: str):
        query = query.strip().lower()

        query_parts = re.split(r"(?=/)", query)

        self.filtered_commands = self._commands.copy()

        for part in query_parts:
            if part.startswith("/"):
                query = part[1:].strip()
                self.filtered_commands = [
                    command
                    for command in self.filtered_commands
                    if query in command["cmd"].lower()
                ]
            else:
                categories = part.split()
                self.filtered_commands = [
                    command
                    for command in self.filtered_commands
                    if all(
                        category in [cat.lower() for cat in command["categories"]]
                        for category in categories
                    )
                ]

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
            print(f"File does not exist: {self._filename}")
            print("It will be created after creating your first command.")
            choice = prompt("Proceed? [y/N]: ")

            if choice not in ["y", "yes"]:
                sys.exit()

    def save(self):
        with open(self._filename, "w") as file:
            data = {"categories": self.categories, "commands": self._commands}
            json.dump(data, file, indent=4)
