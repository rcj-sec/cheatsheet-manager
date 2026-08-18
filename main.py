import argparse

from controllers.controllerv2 import MainControllerV2
from models.model import CheatSheet
from views.edit import EditView
from views.search import SearchView


def parse_args():
    parser = argparse.ArgumentParser(prog="chsh", description="Cheatsheet manager")

    parser.add_argument(
        "file", nargs="?", default="cheatsheet.json", help="Cheatsheet JSON file"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    model = CheatSheet(args.file)
    search_view = SearchView()
    edit_view = EditView()
    controller = MainControllerV2(
        model=model, search_view=search_view, edit_view=edit_view
    )

    controller.run()


if __name__ == "__main__":
    main()
