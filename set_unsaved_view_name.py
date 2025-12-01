import string
import unicodedata

import sublime
import sublime_plugin

from functools import partial, wraps
from time import time as now


def debounced(delay_in_ms, sync=False):
    """Delay calls to event hooks until they weren't triggered for n ms.

    Performs view-specific tracking and is best suited for the
    `on_modified` and `on_selection_modified` methods
    and their `_async` variants.
    The `view` is taken from the first argument for `EventListener`s
    and from the instance for `ViewEventListener`s.

    Calls are only made when the `view` is still "valid" according to ST's API,
    so it's not necessary to check it in the wrapped function.
    """

    # We assume that locking is not necessary because each function will be called
    # from either the ui or the async thread only.
    set_timeout = sublime.set_timeout if sync else sublime.set_timeout_async

    def decorator(func):
        call_at = {}

        def _debounced_callback(view, callback):
            if not view.is_valid():
                del call_at[view.view_id]
                return
            diff = call_at[view.view_id] - int(now() * 1000)
            if diff > 0:
                set_timeout(partial(_debounced_callback, view, callback), diff)
            else:
                del call_at[view.view_id]
                callback()

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            view = self.view if hasattr(self, 'view') else args[0]
            pending = view.view_id in call_at
            call_at[view.view_id] = int(now() * 1000) + delay_in_ms
            if pending:
                return
            callback = partial(func, self, *args, **kwargs)
            set_timeout(partial(_debounced_callback, view, callback), delay_in_ms)

        return wrapper

    return decorator


class SetUnsavedViewName(sublime_plugin.EventListener):
    @debounced(50, sync=True)
    def on_modified(self, view):
        if view.file_name() or view.is_loading():
            return

        view_settings = view.settings()
        if not view_settings.get('set_unsaved_view_name', True):
            return

        cur_name = view_settings.get('auto_name')
        view_name = view.name()

        # Only set the name for plain text files
        if not view_settings.get('set_unsaved_view_name_for_syntax', True):
            if cur_name:
                # Undo any previous name that was set
                view_settings.erase('auto_name')
                if cur_name == view_name:
                    view.set_name("")
            return

        # Name has been explicitly set, don't override it
        if not cur_name and view_name:
            return

        # Name has been explicitly changed, don't override it
        if cur_name and cur_name != view_name:
            view_settings.erase('auto_name')
            return

        # Don't set the names on widgets, it'll just trigger spurious
        # on_modified callbacks
        if view_settings.get('is_widget'):
            return

        line = view.line(0)
        if line.size() > 50:
            line = sublime.Region(0, 50)

        first_line = view.substr(line).strip(string.whitespace)

        # Filter non-printable characters. Without this the save dialog on
        # windows fails to open.
        first_line = ''.join(c for c in first_line if unicodedata.category(c)[0] != 'C')

        view.set_name(first_line)
        view_settings.set('auto_name', first_line)
