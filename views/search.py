from prompt_toolkit.buffer import Buffer
from prompt_toolkit.filters import has_focus, is_true
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.layout import CompletionsMenu, Float, FloatContainer, ScrollablePane
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Frame

STYLE_COMMAND_CLASS = "command"
STYLE_SELECTED_CLASS = "selected"

STYLE_SELECTED = "yellow noreverse"
STYLE_COMMAND = "lightgreen bold"

STYLES = Style(
    [(STYLE_COMMAND_CLASS, STYLE_COMMAND), (STYLE_SELECTED_CLASS, STYLE_SELECTED)]
)


class SearchView:
    def __init__(self):
        self.search_buffer = Buffer(complete_while_typing=True)
        self._results_scroll_pane = ScrollablePane(
            content=Window(), show_scrollbar=True
        )
        self._status = FormattedTextControl()
        self._search_buffer_window = Window(
            BufferControl(
                self.search_buffer,
                preview_search=True,
                focusable=True,
            ),
            height=1,
        )

        self.main_container = HSplit(
            [
                Frame(
                    VSplit(
                        [
                            Window(
                                FormattedTextControl(" > "),
                                width=3,
                            ),
                            self._search_buffer_window,
                        ]
                    ),
                    title="Search",
                ),
                Frame(self._results_scroll_pane, title="Results"),
                Frame(Window(self._status, height=1)),
            ]
        )

        self.main_container = FloatContainer(
            content=self.main_container,
            floats=[Float(CompletionsMenu(), xcursor=True, ycursor=True)],
        )

    def build_view(self, commands):
        def format_command(command):
            def format_new_lines(text: str, indent: int):
                return text.replace("\n", "\n" + " " * indent)

            output = FormattedText()

            output.append(
                ("class:command", f"    {format_new_lines(command['cmd'], 4)}\n")
            )
            output.append(
                ("", f"        Desc: {format_new_lines(command['desc'], 8)}\n")
            )

            if command.get("notes"):
                output.append(
                    ("", f"        Notes: {format_new_lines(command['notes'], 8)}\n")
                )

            categories = command.get("categories", [])
            output.append(
                (
                    "",
                    f"        Categories: {format_new_lines(', '.join(categories), 8)}\n",
                )
            )

            return output

        def create_window(command):
            window = Window(
                FormattedTextControl(format_command(command), focusable=True),
                height=5,
                style=lambda: (
                    f"class:{STYLE_SELECTED}" if is_true(has_focus(window)) else ""
                ),
            )

            return window

        if not commands:
            content = [Window(FormattedTextControl(" No matches."))]
            self.results_windows = None
        else:
            content = [create_window(command) for command in commands]
            self.results_windows = content

        self._results_scroll_pane.content = HSplit(content)

    def display_text_in_mid_pane(self, text):
        self._results_scroll_pane.content = Window(
            FormattedTextControl(text), wrap_lines=True
        )
