import argparse

from cli.interactive import InteractiveCLI
from controllers.controllerv2 import MainControllerV2
from models.model import CheatSheet
from views.edit import EditView
from views.search import SearchView


def parse_args():
    parser = argparse.ArgumentParser(prog="sheets", description="Cheatsheet manager")

    parser.add_argument(
        "file", nargs="?", default="cheatsheet.json", help="Cheatsheet JSON file"
    )

    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Run in interactive mode."
    )

    return parser.parse_args()


def run_interactive_mode(args):
    shell = InteractiveCLI(args.file)
    shell.run()


def run_gui_mode(args):
    model = CheatSheet(args.file)
    search_view = SearchView()
    edit_view = EditView()
    controller = MainControllerV2(
        model=model, search_view=search_view, edit_view=edit_view
    )

    controller.run()


def main():
    args = parse_args()

    if args.interactive:
        run_interactive_mode(args)
    else:
        run_gui_mode(args)


if __name__ == "__main__":
    main()
