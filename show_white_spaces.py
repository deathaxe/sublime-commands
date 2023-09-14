import sublime
import sublime_plugin


class ShowWhiteSpacesCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        try:
            options = args["options"]
            self.view.settings().set("draw_white_space", options)
        except KeyError:
            pass
