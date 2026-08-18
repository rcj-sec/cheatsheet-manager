from prompt_toolkit.completion import WordCompleter


class SearchCompleter(WordCompleter):
    def __init__(self, categories, **kwargs):
        self.categories = categories
        super().__init__(categories, **kwargs)

    def get_completions(self, document, complete_event):
        text = document.text.lstrip()

        if text.startswith((":ca ", ":cr ")):
            self.words = self.categories
        elif text.startswith(("/", ":")):
            return
        else:
            self.words = self.categories

        yield from super().get_completions(document, complete_event)
