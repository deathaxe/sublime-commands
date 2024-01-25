import sublime_plugin

# dictionary of valid line endings
LINE_ENDINGS = {
    'windows': "Windows\tCRLF",
    'unix': "Unix\tLF",
    'cr': "MacOS\tCR"
}


def description(type):
    return LINE_ENDINGS.get(type.lower(), type)


class TypeInputHandler(sublime_plugin.ListInputHandler):

    def __init__(self, line_endings):
        super().__init__()
        self.old_endings = line_endings

    def placeholder(self):
        return "Select Line Endings"

    def preview(self, new_endings):
        if self.old_endings.lower() == new_endings.lower():
            return "Line endings are set to '{}'.".format(
                description(self.old_endings))
        return "Change line endings from '{}' to '{}'.".format(
            description(self.old_endings), description(new_endings))

    def list_items(self):
        values = list(LINE_ENDINGS.keys())
        return (
            [[LINE_ENDINGS[value], value] for value in values],
            values.index(self.old_endings.lower())
        )


class SetLineEndings(sublime_plugin.TextCommand):
    """A replacement command for the builtin `set_line_ending`.

    This class provides an input handler to list the available line endings
    in the command palette using an `ListInputHanlder` rather then listing all
    the values as separate commands.
    """

    def is_checked(self, type):
        return type.lower() == self.view.line_endings().lower()

    def description(self, type):
        return description(type)

    def input_description(self):
        return "Line Endings:"

    def input(self, args):
        if "type" not in args:
            return TypeInputHandler(self.view.line_endings())
        return None

    def run(self, edit, type):
        self.view.set_line_endings(type)
