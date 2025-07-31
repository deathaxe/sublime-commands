import sublime
import sublime_plugin


class EncodingInputHandler(sublime_plugin.ListInputHandler):

    def name(self):
        return "encoding"

    def placeholder(self):
        return "text encoding"

    def list_items(self):
        return [
            item["args"]["encoding"]
            for item in sublime.decode_value(sublime.load_resource(
                "Packages/Default/Encoding.sublime-menu"))[0]["children"]
            if "args" in item
        ]


class SaveWithEncodingInputHandler(EncodingInputHandler):

    def list_items(self):
        return [
            "utf-8 with bom",
            "utf-16 le",
            "utf-16 le with bom",
            "utf-16 be",
            "utf-16 be with bom",
        ] + super().list_items()


class ReopenEncodingCommand(sublime_plugin.WindowCommand):

    def input_description(self):
        return "Reopen with"

    def input(self, args):
        if "encoding" not in args:
            return EncodingInputHandler()
        return None

    def run(self, encoding):
        self.window.run_command("reopen", {"encoding": encoding})


class SaveEncodingCommand(sublime_plugin.WindowCommand):

    def input_description(self):
        return "Save with"

    def input(self, args):
        if "encoding" not in args:
            return SaveWithEncodingInputHandler()
        return None

    def run(self, encoding):
        self.window.run_command("save", {"async": True, "encoding": encoding})


class SetEncodingCommand(sublime_plugin.WindowCommand):

    def input_description(self):
        return "Set Encoding"

    def input(self, args):
        if "encoding" not in args:
            return EncodingInputHandler()
        return None

    def run(self, encoding):
        self.window.run_command("set_encoding", {"encoding": encoding})
