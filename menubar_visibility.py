import sublime
import sublime_plugin


def plugin_loaded():
    preferences().clear_on_change('on_show_menu_changed')
    preferences().add_on_change('on_show_menu_changed', on_show_menu_changed)


def plugin_unloaded():
    preferences().clear_on_change('on_show_menu_changed')


def preferences():
    try:
        return preferences.pref
    except:
        preferences.pref = sublime.load_settings('Preferences.sublime-settings')
        return preferences.pref


def on_show_menu_changed():
    is_menu_visible = preferences().get('show_menu', True)
    for win in sublime.windows():
        win.set_menu_visible(is_menu_visible)


class MenuVisibilityListener(sublime_plugin.EventListener):

    def on_new(self, view):
        self.hide_menu(view.window())

    def on_modified(self, view):
        self.hide_menu(view.window())

    def hide_menu(self, window):
        if isinstance(window, sublime.Window):
            if not preferences().get("show_menu", True):
                window.set_menu_visible(False)
