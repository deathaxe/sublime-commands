import sublime
import sublime_plugin


class MenuBarVisibilityListener(sublime_plugin.EventListener):
    """Apply menu bar visibility state to new windows.

    The MenuBarVisibilityListener automatically applies the visibility state
    of the menu bar to all new windows as Sublime Text is not able to handle
    that properly. New windows are always created with menu bar visible by
    default.
    """

    def on_post_window_command(self, window, command, args):
        if command == 'new_window':
            is_menu_visible = window.is_menu_visible()
            for win in sublime.windows():
                if win != window:
                    win.set_menu_visible(is_menu_visible)
