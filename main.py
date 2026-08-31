import argparse
import os

from prompt_toolkit import prompt

from cli.interactive import InteractiveCLI
from controllers.controllerv2 import MainControllerV2
from models.model import CheatSheet
from views.edit import EditView
from views.search import SearchView


def parse_args():
    parser = argparse.ArgumentParser(prog="sheets", description="Cheatsheet manager")

    parser.add_argument(
        "sheet", nargs="?", help="Name of JSON file in default JSON dir. No extension."
    )
    parser.add_argument("-f", "--filename")

    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Run in interactive mode."
    )

    args = parser.parse_args()

    if (args.sheet is None) == (args.filename is None):
        parser.error("Either a sheet or a file with -f must be specified")

    return args


def run_interactive_mode(filepath):
    shell = InteractiveCLI(filepath)
    shell.run()


def run_gui_mode(filepath):
    model = CheatSheet(filepath)
    search_view = SearchView()
    edit_view = EditView()
    controller = MainControllerV2(
        model=model, search_view=search_view, edit_view=edit_view
    )

    controller.run()


def main():
    args = parse_args()

    SHEETS_DIR = "$HOME/dotfiles/cheatsheets/"

    sheet_path = SHEETS_DIR

    if args.sheet:
        sheet_path = os.path.expandvars(sheet_path + args.sheet + ".json")
    if args.filename:
        sheet_path = os.path.realpath(args.filename)

    if args.interactive:
        run_interactive_mode(sheet_path)
    else:
        run_gui_mode(sheet_path)


if __name__ == "__main__":
    main()
