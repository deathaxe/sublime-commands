import re
import os

import sublime
import sublime_plugin

PACKAGES = "${packages}/"

# The pattern to extract the path and basename of a file without OS pattern.
SETTINGS_RE = re.compile(
    r"(?i)Packages/(.+?)/(.+/)?(.+?)(\.sublime-settings)")


class BaseFileInputHandler(sublime_plugin.ListInputHandler):

    def name(self):
        return "base_file"

    def placeholder(self):
        return "Settings File"

    def list_items(self):

        # create filter for syntax-specific settings
        syntaxes = set()
        for f in sublime.find_resources('*.sublime-syntax'):
            name, _ = os.path.splitext(os.path.basename(f))
            syntaxes.add(name)

        items = []
        names = set()
        for f in sublime.find_resources('*.sublime-settings'):
            package, path, name, ext = SETTINGS_RE.match(f).groups()
            if package is not 'User' and name not in names and name not in syntaxes:
                item = "".join((package, "/", path or "", name, ext))
                items.append((item, PACKAGES + item))
                names.add(name)

        items.sort()
        return items


class EditPackageSettingsCommand(sublime_plugin.WindowCommand):

    def input_description(self):
        return "Preferences"

    def input(self, args):
        if "base_file" not in args:
            if "user_file" in args:
                del args["user_file"]
            return BaseFileInputHandler()
        return None

    def run(self, base_file):
        self.window.run_command(
            "edit_settings", {
                "base_file": base_file,
                'default': (
                    '// These settings override Default settings '
                    'for the package\n{\n\t$0\n}\n')
            })


class SyntaxSettingsInputHandler(sublime_plugin.ListInputHandler):

    def __init__(self, syntax):
        self.syntax = syntax

    def name(self):
        return "syntax"

    def placeholder(self):
        return "Syntax Name"

    def list_items(self):
        items = set()
        selected = None
        for f in sublime.find_resources('*.sublime-syntax'):
            name, _ = os.path.splitext(os.path.basename(f))
            if name == self.syntax:
                item = (name + " (this view)", name)
                selected = item
            else:
                item = (name, name)
            items.add(item)

        items = list(items)
        items.sort()
        return (items, items.index(selected)) if selected else items


class EditSyntaxSettingsCommand(sublime_plugin.WindowCommand):

    def input_description(self):
        return "Syntax Settings"

    def input(self, args):
        if "syntax" not in args:
            try:
                settings = self.window.active_view().settings()
                syntax, _ = os.path.splitext(os.path.basename(settings.get('syntax')))
            except:
                syntax = None
            return SyntaxSettingsInputHandler(syntax)
        return None

    def run(self, syntax):
        self.window.run_command(
            'edit_settings',
            {
                'base_file': '${packages}/Default/Preferences.sublime-settings',
                'user_file': os.path.join(sublime.packages_path(), 'User', syntax + '.sublime-settings'),
                'default': (
                    '// These settings override both User and Default settings '
                    'for the %s syntax\n{\n\t$0\n}\n') % syntax
            })

    def is_enabled(self):
        return True
