from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import (
    BufferControl,
    CompletionsMenu,
    Dimension,
    Float,
    FloatContainer,
    FormattedTextControl,
    HSplit,
    VSplit,
    Window,
)
from prompt_toolkit.widgets import Frame, ValidationToolbar


class EditView:
    def __init__(self):
        self.status = FormattedTextControl()

        self.edit_cmd_buffer = Buffer()
        self.edit_desc_buffer = Buffer()
        self.edit_notes_buffer = Buffer()
        self.edit_cats_buffer = Buffer(
            complete_while_typing=True, validate_while_typing=True
        )

        self.main_container = HSplit(
            [
                Frame(
                    VSplit(
                        [
                            Window(BufferControl(self.edit_cmd_buffer), height=1),
                        ]
                    ),
                    title="Command",
                ),
                Frame(
                    VSplit(
                        [
                            Window(BufferControl(self.edit_desc_buffer), height=2),
                        ]
                    ),
                    title="Description",
                ),
                Frame(
                    VSplit(
                        [
                            Window(
                                BufferControl(self.edit_notes_buffer),
                                height=Dimension(weight=1),
                            ),
                        ],
                        height=Dimension(weight=1),
                    ),
                    title="Notes",
                    height=Dimension(weight=1),
                ),
                Frame(
                    VSplit(
                        [
                            Window(
                                BufferControl(self.edit_cats_buffer),
                                height=2,
                            ),
                        ]
                    ),
                    title="Categories",
                ),
                Frame(Window(self.status, height=1)),
            ]
        )

        self.main_container = FloatContainer(
            content=self.main_container,
            floats=[
                Float(CompletionsMenu(), xcursor=True, ycursor=True),
                Float(ValidationToolbar(), bottom=1, right=1),
            ],
        )
