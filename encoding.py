import sublime_plugin


class EncodingInputHandler(sublime_plugin.ListInputHandler):

    def name(self):
        return "encoding"

    def placeholder(self):
        return "text encoding"

    def list_items(self):
        return [
            "UTF-8",
            "UTF-8 with BOM",
            "UTF-16 LE",
            "UTF-16 LE with BOM",
            "UTF-16 BE",
            "UTF-16 BE with BOM",
            "Western (Windows 1252)",
            "Western (ISO 8859-1)",
            "Western (ISO 8859-3)",
            "Western (ISO 8859-15)",
            "Western (Mac Roman)",
            "DOS (CP 437)",
            "Arabic (Windows 1256)",
            "Arabic (ISO 8859-6)",
            "Baltic (Windows 1257)",
            "Baltic (ISO 8859-4)",
            "Celtic (ISO 8859-14)",
            "Central European (Windows 1250)",
            "Central European (ISO 8859-2)",
            "Cyrillic (Windows 1251)",
            "Cyrillic (Windows 866)",
            "Cyrillic (ISO 8859-5)",
            "Cyrillic (KOI8-R)",
            "Cyrillic (KOI8-U)",
            "Estonian (ISO 8859-13)",
            "Greek (Windows 1253)",
            "Greek (ISO 8859-7)",
            "Hebrew (Windows 1255)",
            "Hebrew (ISO 8859-8)",
            "Nordic (ISO 8859-10)",
            "Romanian (ISO 8859-16)",
            "Turkish (Windows 1254)",
            "Turkish (ISO 8859-9)",
            "Vietnamese (Windows 1258)",
            "Hexadecimal"
        ]


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
            return EncodingInputHandler()
        return None

    def run(self, encoding):
        self.window.run_command("save", {"encoding": encoding})


class SetEncodingCommand(sublime_plugin.WindowCommand):

    def input_description(self):
        return "Set Encoding"

    def input(self, args):
        if "encoding" not in args:
            return EncodingInputHandler()
        return None

    def run(self, encoding):
        self.window.run_command("set_encoding", {"encoding": encoding})
