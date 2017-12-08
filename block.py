import sublime
import sublime_plugin


def next_line(view, pt):
    return view.line(pt).b + 1


def prev_line(view, pt):
    return view.line(pt).a - 1


def is_ws(str):
    for ch in str:
        if ch not in ' \t':
            return False
    return True


def indented_block(view, r):
    if r.empty():
        if r.a == view.size():
            return False

        nl = next_line(view, r.a)
        nr = view.indented_region(nl)
        if nr.a < nl:
            nr.a = nl

        this_indent = view.indentation_level(r.a)
        next_indent = view.indentation_level(nl)

        ok = this_indent + 1 <= next_indent

        if not ok:
            prev_indent = view.indentation_level(prev_line(view, r.a))

            # Mostly handle the case where the user has just pressed enter, and the
            # auto indent will update the indentation to something that will trigger
            # the block behavior when { is pressed
            line_str = view.substr(view.line(r.a))
            if is_ws(line_str) and len(view.get_regions("autows")) > 0:
                ok = prev_indent + 1 == this_indent and this_indent == next_indent

        if ok:
            # ensure that every line of nr is indented more than nl
            l = next_line(view, nl)
            while l < nr.b:
                if view.indentation_level(l) < next_indent:
                    return False
                l = next_line(view, l)
            return True

    return False


class BlockContext(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        if key != "indented_block":
            return None

        if operator != sublime.OP_EQUAL and operator != sublime.OP_NOT_EQUAL:
            return False

        is_all = True
        is_any = False

        for r in view.sel():
            if operator == sublime.OP_EQUAL:
                b = (operand == indented_block(view, r))
            else:
                b = (operand != indented_block(view, r))

            if b:
                is_any = True
            else:
                is_all = False

        return is_all if match_all else is_any


class WrapBlockCommand(sublime_plugin.TextCommand):
    def run(self, edit, begin, end):
        view = self.view
        view.run_command('insert', {'characters': begin})

        for r in reversed(view.sel() or []):
            if r.empty():

                nr = view.indented_region(next_line(view, r.a))

                slvl = view.indentation_level(r.a)
                elvl = view.indentation_level(nr.b)

                end_line = view.substr(view.line(nr.b)).strip()

                # Insert `end` if it does not exist at the end of the indented
                # block with the same indention level.
                if slvl != elvl or not end_line.startswith(end):

                    begin_line = view.substr(view.line(r.a))

                    ws = ""
                    for ch in begin_line:
                        if ch not in ' \t':
                            break
                        ws += ch

                    if nr.b == view.size() and view.substr(nr.b - 1) != "\n":
                        view.insert(edit, nr.b, "\n" + ws + end + "\n")
                    else:
                        view.insert(edit, nr.b, ws + end + "\n")
