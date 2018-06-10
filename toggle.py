import sublime
import sublime_plugin


class ToggleLogBuiltSystemsCommand(sublime_plugin.ApplicationCommand):

    def __init__(self):
        self.flag = False

    def run(self):
        self.flag = not self.flag
        sublime.log_build_systems(self.flag)


class ToggleLogCommandsCommand(sublime_plugin.ApplicationCommand):

    def __init__(self):
        self.flag = False

    def run(self):
        self.flag = not self.flag
        sublime.log_commands(self.flag)


class ToggleLogInputCommand(sublime_plugin.ApplicationCommand):

    def __init__(self):
        self.flag = False

    def run(self):
        self.flag = not self.flag
        sublime.log_input(self.flag)


class ToggleLogIndexingCommand(sublime_plugin.ApplicationCommand):

    def __init__(self):
        self.flag = False

    def run(self):
        self.flag = not self.flag
        sublime.log_indexing(self.flag)


class ToggleLogResultRegexCommand(sublime_plugin.ApplicationCommand):

    def __init__(self):
        self.flag = False

    def run(self):
        self.flag = not self.flag
        sublime.log_result_regex(self.flag)


class TogglePreferenceCommand(sublime_plugin.ApplicationCommand):

    def run(self, setting, persist=True):
        pref = sublime.load_settings("Preferences.sublime-settings")
        pref.set(setting, not pref.get(setting, False))
        if persist:
            sublime.save_settings("Preferences.sublime-settings")
