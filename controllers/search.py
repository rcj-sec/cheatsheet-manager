from collections.abc import Callable

from prompt_toolkit.filters import Condition, has_focus, is_true
from prompt_toolkit.key_binding import (
    ConditionalKeyBindings,
    KeyBindings,
)
from prompt_toolkit.layout import Layout

from controllers.completers import SearchCompleter
from models.model import CheatSheet
from views.search import SearchView

STATUS_SEARCH = " [Tab] Focus search [󰁅/󰁝] Navigate [e] Edit command [DD] Delete [:a] Add command [:h] Help [Esc] Exit"

HELP_MESSAGE = """
Help:

    :h    show this help (search to exit)
    :a    add command to list 
          WARNING: no confirmation and commits changes to file.
    :c    list categories
    :ca   add categories
          Example: :ca category1 category2 etc
    :cr   remove categories
          Example: :cr category1 category2 etc

    Search:
        Default behavior
            Type categories (blank separated) to find commands that belong to all categories.
            Example: "router dns"
                      This will find commands that belong to the "router" AND "dns" category

        Search in command (/ prefix)
            Search input in the command itself rather than in categories
            Example: "/ip a" will find all commands with  "ip a"
"""


class SearchController:
    def __init__(
        self,
        model: CheatSheet,
        view: SearchView,
        on_edit: Callable[[int | None], None],
        on_exit: Callable[[], None],
    ):
        self._model = model
        self._view = view
        self._on_edit = on_edit
        self._on_exit = on_exit

        self.define_keybinds()

        self._focused_index = 0

        self.layout = Layout(self._view.main_container)

        self._view.search_buffer.on_text_changed.add_handler(
            self._on_search_buffer_changed
        )

        self._view.search_buffer.completer = SearchCompleter(
            self._model.categories, ignore_case=True
        )

        self._view._status.text = STATUS_SEARCH

        self._view.build_view(self._model.filtered_commands)

    def takeover(self, index: int | None):
        search = (
            ""
            if self._view.search_buffer.text.startswith(":")
            else self._view.search_buffer.text
        )

        self._model.search(search)
        self._view.build_view(self._model.filtered_commands)

        if index is not None and self._view.results_windows:
            self.layout.focus(self._view.results_windows[index])
        else:
            self._focused_index = 0
            self.layout.focus(self._view.search_buffer)

    def add_command(self):
        self._on_edit(None)

    def _process_built_in_command(self, text):
        if not text or not text.startswith(":"):
            return

        words = text[1:].split()

        if words[0] in ["a", "add"]:
            self._on_edit(None)
        elif words[0] in ["h", "help"]:
            self._view.display_text_in_mid_pane(HELP_MESSAGE)
        elif words[0] in ["c", "categories", "cats"]:
            self._view.display_text_in_mid_pane(
                f"\nCategories:\n\n    {'\n    '.join(self._model.categories)}"
            )
        elif words[0] in ["ca", "add_categories"]:
            self._model.add_categories(words[1:])
            self._model.save()
            self._view.display_text_in_mid_pane(
                f"\nAdded categories:\n\n    {'\n    '.join(words[1:])}"
            )
        elif words[0] in ["cr", "remove_categories"]:
            self._model.remove_categories(words[1:])
            self._model.save()
            self._view.display_text_in_mid_pane(
                f"\nRemoved categories:\n\n    {'\n    '.join(words[1:])}"
            )

    def _on_search_buffer_changed(self, buffer):
        self._view._results_scroll_pane.vertical_scroll = 0
        text = str(buffer.text.strip())
        if not text.startswith(":"):
            self._model.search(buffer.text)
            self._view.build_view(self._model.filtered_commands)

    def define_keybinds(self):
        self.binds = KeyBindings()

        @self.binds.add("enter")
        def no_buffer_reset(event):
            self._process_built_in_command(self._view.search_buffer.text)

        @self.binds.add(
            "D", "D", filter=Condition(lambda: not self.layout.buffer_has_focus)
        )
        def delete_command(event):
            self._model.delete_command(self._focused_index)
            self._model.save()

            if self._focused_index >= len(self._model.filtered_commands):
                self._focused_index = len(self._model.filtered_commands) - 1

            self._view.build_view(self._model.filtered_commands)

            if self._view.results_windows:
                self.layout.focus(self._view.results_windows[self._focused_index])
            else:
                self.layout.focus(self._view.search_buffer)

        @self.binds.add("e", filter=Condition(lambda: not self.layout.buffer_has_focus))
        def edit_command(event):
            self._on_edit(self._focused_index)

        @self.binds.add(
            "up", filter=Condition(lambda: bool(self._model.filtered_commands))
        )
        def cycle_focus_up(event):
            self._focused_index = (self._focused_index - 1) % len(
                self._model.filtered_commands
            )
            self.layout.focus_previous()

        @self.binds.add(
            "down", filter=Condition(lambda: bool(self._model.filtered_commands))
        )
        def cycle_focus_down(event):
            if not self.layout.buffer_has_focus:
                self._focused_index = (self._focused_index + 1) % len(
                    self._model.filtered_commands
                )

            self.layout.focus_next()

        @self.binds.add(
            "tab", filter=Condition(lambda: not self.layout.buffer_has_focus)
        )
        def focus_search(event):
            self._view._results_scroll_pane.vertical_scroll = 0
            self._focused_index = 0
            self.layout.focus(self._view.search_buffer)

        @self.binds.add("escape")
        def exit(event):
            self._on_exit()

        self.binds = ConditionalKeyBindings(
            self.binds, Condition(lambda: is_true(has_focus(self._view.main_container)))
        )
