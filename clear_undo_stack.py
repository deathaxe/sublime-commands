import sublime
import sublime_plugin


class ClearUndoStackCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.active_view().clear_undo_stack()
        sublime.status_message("Undo Stack of the current file has been cleared")
