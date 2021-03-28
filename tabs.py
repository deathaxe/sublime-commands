import sublime_plugin


class CloseToLeftByIndexCommand(sublime_plugin.WindowCommand):

    def run(self, group = -1, index = -1):
        for view in self.window.views_in_group(group)[:index]:
            view.close()

    def is_enabled(self, group, index):
        return index > 0


class CloseUnmodifiedToLeftByIndexCommand(sublime_plugin.WindowCommand):

    def run(self, group = -1, index = -1):
        for view in self.window.views_in_group(group)[:index]:
            if not view.is_dirty():
                view.close()

    def is_enabled(self, group, index):
        return index > 0
