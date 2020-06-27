import sublime_plugin


class IndentSelectWholeFirstLineEventListener(sublime_plugin.EventListener):
    """
    This event listener works around the following issue.

    Issue:

    https://github.com/sublimehq/sublime_text/issues/1746

    When indenting a selected block of text, Sublime Text moves the beginning
    of the selection instead of keeping it at the beginning of a line.

    If the selected text is copied and pasted after indenting the result is
    broken then.
    """

    def on_post_text_command(self, view, command_name, args):
        if command_name == 'indent':
            if all(not sel.empty() for sel in view.sel()):
                if all(view.line(sel.begin()) != view.line(sel.end()) for sel in view.sel()):
                    new_selections = []
                    for sel in view.sel():
                        new_selections.append(sel.cover(view.line(sel.begin())))
                    view.sel().clear()
                    view.sel().add_all(new_selections)
