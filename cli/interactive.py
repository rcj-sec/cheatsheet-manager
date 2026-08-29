from pprint import pprint

from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory

from models.model import CheatSheet

SEARCH_KEYWORD_COMMAND = "search "


class InteractiveCLI:
    def __init__(self, filename):
        self._model = CheatSheet(filename)

    def _search(self, search_text):
        self._model.search(search_text)
        pprint(self._model.filtered_commands)

    def _process_user_input(self, text: str):
        match text:
            case "exit" | "quit":
                return 0
            case text if text.startswith(SEARCH_KEYWORD_COMMAND):
                search_text = text.split(SEARCH_KEYWORD_COMMAND)[1]
                self._search(search_text)

        return 1

    def run(self):
        history = InMemoryHistory()
        while True:
            try:
                text = prompt("> ", history=history)
            except KeyboardInterrupt:
                break

            if not self._process_user_input(text):
                break
