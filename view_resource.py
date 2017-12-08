import sublime
import sublime_plugin


class ResourceNameInputHandler(sublime_plugin.ListInputHandler):
    def name(self):
        return "name"

    def placeholder(self):
        return "Name"

    def list_items(self):
        settings = sublime.load_settings("Preferences.sublime-settings")
        exclude = set(f + '/' for f in settings.get("folder_exclude_patterns", []))

        PACKAGES = "Packages/"
        start = len(PACKAGES)
        return [
            f[start:] for f in sublime.find_resources('')
            if f.startswith(PACKAGES) and not any(fe in f for fe in exclude)
        ]


class ViewResourceCommand(sublime_plugin.WindowCommand):
    def run(self, name):
        self.window.run_command("open_file", {"file": "${packages}/" + name})

    def input(self, args):
        if "name" not in args:
            return ResourceNameInputHandler()
        return None
