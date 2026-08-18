from collections.abc import Callable

from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.filters import Condition, has_focus, is_true
from prompt_toolkit.key_binding import (
    ConditionalKeyBindings,
    KeyBindings,
)
from prompt_toolkit.layout import Layout
from prompt_toolkit.validation import ValidationError, Validator

from models.model import CheatSheet
from views.edit import EditView

STATUS_EDIT = "[󰁅/󰁝] Navigate [Ctrl-s] Save [Esc] Back"


class EditController:
    def __init__(
        self, model: CheatSheet, view: EditView, on_exit: Callable[[int | None], None]
    ):
        self._model = model
        self._view = view
        self._on_exit = on_exit

        self._view.status.text = STATUS_EDIT

        self._view.edit_cats_buffer.completer = WordCompleter(
            self._model.categories, ignore_case=True
        )

        self._view.edit_cats_buffer.validator = CategoriesValidator(
            self._model.categories
        )

        self._view.edit_cmd_buffer.validator = NonEmptyValidator()

        self.define_keybinds()

        self.layout = Layout(self._view.main_container)

    def _move_cursor_to_end(self):
        buffer = self.layout.current_buffer
        assert buffer is not None
        buffer.cursor_position = len(buffer.text)

    def takeover(self, index: int | None):
        self._edited_command = (
            self._model.get_filtered_command_data(index)
            if index is not None
            else self._model.add_empty_command()
        )
        self._edited_index = index
        self._view.edit_cmd_buffer.text = self._edited_command["cmd"]
        self._view.edit_desc_buffer.text = self._edited_command["desc"]
        self._view.edit_notes_buffer.text = self._edited_command["notes"]
        self._view.edit_cats_buffer.text = " ".join(self._edited_command["categories"])
        self.layout.focus(self._view.edit_cmd_buffer)
        self._move_cursor_to_end()

    def _capture_and_save(self):
        self._edited_command["cmd"] = self._view.edit_cmd_buffer.text
        self._edited_command["desc"] = self._view.edit_desc_buffer.text
        self._edited_command["notes"] = self._view.edit_notes_buffer.text
        self._edited_command["categories"] = self._view.edit_cats_buffer.text.split()

        self._model.save()

    def define_keybinds(self):
        self.binds = KeyBindings()

        @self.binds.add("enter")
        def validate(event):
            self._view.edit_cmd_buffer.validate()

        @self.binds.add("escape")
        def search_view(event):
            if self._edited_index is None:
                self._model.delete_last_command()

            self._on_exit(self._edited_index)

        @self.binds.add("up")
        def cycle_edit_fields_up(event):
            self.layout.focus_previous()
            self._move_cursor_to_end()

        @self.binds.add("down")
        def cycle_edit_fields_down(event):
            self.layout.focus_next()
            self._move_cursor_to_end()

        @self.binds.add("c-s")
        def tab(event):
            buffers = [self._view.edit_cmd_buffer, self._view.edit_cats_buffer]

            for buffer in buffers:
                self.layout.focus(buffer)
                if not buffer.validate():
                    return

            self._capture_and_save()
            self._on_exit(self._edited_index)

        self.binds = ConditionalKeyBindings(
            self.binds, Condition(lambda: is_true(has_focus(self._view.main_container)))
        )


class NonEmptyValidator(Validator):
    def validate(self, document):
        if not document.text.strip():
            raise ValidationError(message="This field cannot be empty")


class CategoriesValidator(Validator):
    def __init__(self, categories: list) -> None:
        self.categories = categories
        super().__init__()

    def validate(self, document):
        captured_categories = document.text.strip().split()
        if not captured_categories:
            raise ValidationError(message="Add at least one category")
        else:
            if any(category not in self.categories for category in captured_categories):
                raise ValidationError(message="Category not found")
