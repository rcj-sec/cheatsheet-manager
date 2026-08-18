from prompt_toolkit import Application
from prompt_toolkit.key_binding import (
    merge_key_bindings,
)

from controllers.edit import EditController
from controllers.search import SearchController
from models.model import CheatSheet
from views.edit import EditView
from views.search import STYLES, SearchView


class MainControllerV2:
    def __init__(self, model: CheatSheet, search_view: SearchView, edit_view: EditView):
        self._search_controller = SearchController(
            model, search_view, on_edit=self._go_to_edit_view, on_exit=self._exit
        )
        self._edit_controller = EditController(
            model, edit_view, on_exit=self._go_to_search_view
        )

        self._app = Application(
            layout=self._search_controller.layout,
            key_bindings=merge_key_bindings(
                [self._search_controller.binds, self._edit_controller.binds]
            ),
            full_screen=True,
            style=STYLES,
        )

    def _go_to_edit_view(self, index: int | None):
        self._app.layout = self._edit_controller.layout
        self._edit_controller.takeover(index)

    def _go_to_search_view(self, index: int | None):
        self._app.layout = self._search_controller.layout
        self._search_controller.takeover(index)

    def _exit(self):
        self._app.exit()

    def run(self):
        self._app.run()
