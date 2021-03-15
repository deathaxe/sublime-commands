import sublime
import sublime_plugin

HAVE_GET_LOG_STATE = int(sublime.version()) >= 4099


class ToggleLogBuiltSystemsCommand(sublime_plugin.ApplicationCommand):

    def __init__(self):
        self.flag = False

    def run(self):
        if HAVE_GET_LOG_STATE:
            self.flag = not sublime.get_log_build_systems()
        else:
            self.flag = not self.flag
        sublime.log_build_systems(self.flag)
        sublime.status_message('log_build_systems -> %s' % str(self.flag))


class ToggleLogCommandsCommand(sublime_plugin.ApplicationCommand):

    def __init__(self):
        self.flag = False

    def run(self):
        if HAVE_GET_LOG_STATE:
            self.flag = not sublime.get_log_commands()
        else:
            self.flag = not self.flag
        sublime.log_commands(self.flag)
        sublime.status_message('log_commands -> %s' % str(self.flag))


class ToggleLogControlTreeCommand(sublime_plugin.ApplicationCommand):

    def __init__(self):
        self.flag = False

    def is_enabled(self):
        return hasattr(sublime, 'log_control_tree')

    def run(self):
        if HAVE_GET_LOG_STATE:
            self.flag = not sublime.get_log_control_tree()
        else:
            self.flag = not self.flag
        sublime.log_control_tree(self.flag)
        sublime.status_message('log_control_tree -> %s' % str(self.flag))


class ToggleLogInputCommand(sublime_plugin.ApplicationCommand):

    def __init__(self):
        self.flag = False

    def run(self):
        if HAVE_GET_LOG_STATE:
            self.flag = not sublime.get_log_input()
        else:
            self.flag = not self.flag
        sublime.log_input(self.flag)
        sublime.status_message('log_input -> %s' % str(self.flag))


class ToggleLogIndexingCommand(sublime_plugin.ApplicationCommand):

    def __init__(self):
        self.flag = False

    def run(self):
        if HAVE_GET_LOG_STATE:
            self.flag = not sublime.get_log_indexing()
        else:
            self.flag = not self.flag
        sublime.log_indexing(self.flag)
        sublime.status_message('log_indexing -> %s' % str(self.flag))


class ToggleLogResultRegexCommand(sublime_plugin.ApplicationCommand):

    def __init__(self):
        self.flag = False

    def run(self):
        if HAVE_GET_LOG_STATE:
            self.flag = not sublime.get_log_result_regex()
        else:
            self.flag = not self.flag
        sublime.log_result_regex(self.flag)
        sublime.status_message('log_result_regex -> %s' % str(self.flag))


class TogglePreferenceCommand(sublime_plugin.ApplicationCommand):

    def run(self, setting, persist=True):
        pref = sublime.load_settings("Preferences.sublime-settings")
        pref.set(setting, not pref.get(setting, False))
        if persist:
            sublime.save_settings("Preferences.sublime-settings")


class ToggleDrawDebug(sublime_plugin.TextCommand):
    def run(self, edit):
        settings = self.view.settings()
        settings.set("draw_debug", not settings.get("draw_debug", False))
