from prompt_toolkit import Application
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout

from models.model import CheatSheet
from views.edit import EditView
from views.search import STYLES, SearchView


class MainController:
    def __init__(self, model: CheatSheet, search_view: SearchView, edit_view: EditView):
        self.model = model

        self.focused_index = 0

        self.search_view = search_view
        self.edit_view = edit_view

        self.search_view.search_buffer.on_text_changed.add_handler(
            self.search_buffer_changed
        )

        self.layout = Layout(self.search_view.main_container)

        self.search_view.build_view(model.filtered_commands)

        self.app = Application(
            layout=self.layout,
            key_bindings=self.define_search_bindings(),
            full_screen=True,
            style=STYLES,
        )

    def search_buffer_changed(self, buffer):
        self.model.search(self.search_view.search_buffer.text)
        self.search_view.build_view(self.model.filtered_commands)

    def move_cursor_to_end(self):
        buffer = self.layout.current_buffer
        assert buffer is not None
        buffer.cursor_position = len(buffer.text)

    def go_to_results_view(self):
        self.app.key_bindings = self.define_search_bindings()
        self.app.layout.container = self.search_view.main_container
        self.layout.focus(self.search_view.search_buffer)
        self.search_view.build_view(self.model.filtered_commands)

    def populate_edit_layout(self):
        self.edited_command = self.model.get_filtered_command_data(self.focused_index)
        self.edit_view.edit_cmd_buffer.text = self.edited_command["cmd"]
        self.edit_view.edit_desc_buffer.text = self.edited_command["desc"]
        self.edit_view.edit_notes_buffer.text = self.edited_command["notes"]
        self.edit_view.edit_cats_buffer.text = " ".join(
            self.edited_command["categories"]
        )

    def capture_and_save(self):
        self.edited_command["cmd"] = self.edit_view.edit_cmd_buffer.text
        self.edited_command["desc"] = self.edit_view.edit_desc_buffer.text
        self.edited_command["notes"] = self.edit_view.edit_notes_buffer.text
        self.edited_command["categories"] = self.edit_view.edit_cats_buffer.text.split()

        self.model.save()

    def define_edit_bindings(self):
        binds = KeyBindings()

        @binds.add("escape")
        def search_view(event):
            self.go_to_results_view()

        @binds.add("up")
        def cycle_edit_fields_up(event):
            self.layout.focus_previous()
            self.move_cursor_to_end()

        @binds.add("down")
        def cycle_edit_fields_down(event):
            self.layout.focus_next()
            self.move_cursor_to_end()

        @binds.add("tab")
        def tab(event):
            self.capture_and_save()
            self.go_to_results_view()

        return binds

    def define_search_bindings(self):
        binds = KeyBindings()

        @binds.add("enter")
        def no_buffer_reset(event):
            pass

        @binds.add("e", filter=Condition(lambda: not self.layout.buffer_has_focus))
        def edit_command(event):
            self.app.key_bindings = self.define_edit_bindings()
            self.populate_edit_layout()
            self.app.layout.container = self.edit_view.main_container
            self.layout.focus(self.edit_view.edit_cmd_buffer)
            self.move_cursor_to_end()

        @binds.add("up", filter=Condition(lambda: bool(self.model.filtered_commands)))
        def cycle_focus_up(event):
            self.focused_index = (self.focused_index - 1) % len(
                self.model.filtered_commands
            )
            self.layout.focus_previous()

        @binds.add("down", filter=Condition(lambda: bool(self.model.filtered_commands)))
        def cycle_focus_down(event):
            if not self.layout.buffer_has_focus:
                self.focused_index = (self.focused_index + 1) % len(
                    self.model.filtered_commands
                )

            self.layout.focus_next()

        @binds.add("tab")
        def focus_search(event):
            self.layout.focus(self.search_view.search_buffer)

        @binds.add("escape")
        def exit(event):
            self.app.exit()

        return binds

    def run(self):
        self.app.run()
