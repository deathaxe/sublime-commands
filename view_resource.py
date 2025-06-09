import sublime
import sublime_plugin


class ResourceNameInputHandler(sublime_plugin.ListInputHandler):

    def name(self):
        return "name"

    def placeholder(self):
        return "Name"

    def list_items(self):
        settings = sublime.load_settings("Preferences.sublime-settings")
        exclude = settings.get("folder_exclude_patterns", [])
        if not isinstance(exclude, list):
            return

        exclude = set(f + '/' for f in exclude if not f[-1:] != '/')

        PACKAGES = "Packages/"
        start = len(PACKAGES)
        return [
            f[start:] for f in sublime.find_resources('')
            if f.startswith(PACKAGES)
            and not f.endswith('.sublime-package')
            and not any(fe in f for fe in exclude)
        ]


class ViewResourceCommand(sublime_plugin.WindowCommand):
    def run(self, name):
        self.window.run_command("open_file", {"file": "${packages}/" + name})

    def input(self, args):
        if "name" not in args:
            return ResourceNameInputHandler()
        return None
