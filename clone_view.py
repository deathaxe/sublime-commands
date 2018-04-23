import sublime_plugin


class CloneFileToNewGroupCommand(sublime_plugin.WindowCommand):
    def run(self):
        if (self.window.num_groups() < 2):
            self.window.run_command('clone_file')

            self.window.set_layout({
                "cols": [0.0, 0.5, 1.0],
                "rows": [0.0, 1.0],
                "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
                })

            self.window.run_command('focus_group', {'group': 0})
            self.window.run_command('move_to_group', {'group': 1})

            self.copy_position_and_selections()
        else:
            view0 = self.window.active_view_in_group(0)
            view1 = self.window.active_view_in_group(1)

            # Same file open in each of the two windows, cull to 1 if possible
            if (view0.file_name() == view1.file_name()):
                self.window.focus_view(view1)

                view1.set_scratch(True)
                view1.close()

                self.window.focus_view(view0)

                # just deleted the only window, fix layout
                if (len(self.window.views_in_group(1)) == 0):
                    self.window.set_layout({
                        "cols": [0.0, 1.0],
                        "rows": [0.0, 1.0],
                        "cells": [[0, 0, 1, 1]]})

            # Two views, but not the same file
            else:
                othergroup = 0
                if (self.window.active_group() == 0): othergroup = 1

                # Check if a copy already exists in 'othergroup' and just
                # focus on it if so
                otherviews = self.window.views_in_group(othergroup)
                for view in otherviews:
                    if (view.file_name() == self.window.active_view().file_name()):
                        self.window.focus_view(view)
                        return

                # No existing views found - make a new one
                self.window.run_command('clone_file')
                self.window.run_command('move_to_group', {'group': othergroup})

                self.copy_position_and_selections()

    def copy_position_and_selections(self):
        view0 = self.window.active_view_in_group(0)
        view1 = self.window.active_view_in_group(1)
        view1.set_viewport_position(view0.viewport_position(), False)
        view1.sel().clear()
        view1.sel().add_all(view0.sel())
