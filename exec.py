import codecs
import html
import os
import queue
import signal
import subprocess
import sys
import threading
import time

from typing import cast

import sublime
import sublime_plugin

ANNOTATION_TEMPLATE = """
<body>
  <style>
    #annotation-error {{
      background-color: color(var(--background) blend(#fff 95%));
    }}
    html.dark #annotation-error {{
      background-color: color(var(--background) blend(#fff 95%));
    }}
    html.light #annotation-error {{
      background-color: color(var(--background) blend(#000 85%));
    }}
    a {{
      text-decoration: inherit;
    }}
  </style>
  <div class="error" id=annotation-error>
    <span class="content">{content}</span>
  </div>
</body>
"""


class ProcessListener:
    def on_data(self, proc, data):
        pass

    def on_finished(self, proc):
        pass


class AsyncProcess:
    """
    Encapsulates subprocess.Popen, forwarding stdout to a supplied
    ProcessListener (on a separate thread)
    """

    def __init__(self, cmd, shell_cmd, env, listener, path="", shell=False):
        """ "path" and "shell" are options in build systems """

        if not shell_cmd and not cmd:
            raise ValueError("shell_cmd or cmd is required")

        if shell_cmd and not isinstance(shell_cmd, str):
            raise ValueError("shell_cmd must be a string")

        self.listener = listener
        self.killed = False

        self.start_time = time.time()

        try:
            # Set temporary PATH to locate executable in cmd
            if path:
                old_path = os.environ["PATH"]
                # The user decides in the build system whether he wants to append
                # $PATH or tuck it at the front: "$PATH;C:\\new\\path",
                # "C:\\new\\path;$PATH"
                os.environ["PATH"] = os.path.expandvars(path)

            if env:
                proc_env = os.environ.copy()
                for k, v in env.items():
                    proc_env[k] = os.path.expandvars(v)
            else:
                proc_env = None

            if sys.platform == "win32":
                preexec_fn = None
            else:
                preexec_fn = os.setsid

            if shell_cmd:
                if sys.platform == "win32":
                    # Use shell=True on Windows, so shell_cmd is passed through
                    # with the correct escaping
                    cmd = shell_cmd
                    shell = True
                elif sys.platform == "darwin":
                    # Use a login shell on OSX, otherwise the users expected env
                    # vars won't be setup
                    cmd = ["/usr/bin/env", "bash", "-l", "-c", shell_cmd]
                    shell = False
                elif sys.platform == "linux":
                    # Explicitly use /bin/bash on Linux, to keep Linux and OSX as
                    # similar as possible. A login shell is explicitly not used for
                    # linux, as it's not required
                    cmd = ["/usr/bin/env", "bash", "-c", shell_cmd]
                    shell = False

            self.proc = subprocess.Popen(
                cmd,
                bufsize=0,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                env=proc_env,
                preexec_fn=preexec_fn,
                shell=shell)

        finally:
            # Make sure this is always run, otherwise we're leaving the PATH set
            # permanently
            if path:
                os.environ["PATH"] = old_path

        self.stdout_thread = threading.Thread(
            target=self.read_fileno,
            args=(self.proc.stdout, True)
        )

    def start(self):
        self.stdout_thread.start()

    def start_input_thread(self):
        input_queue = queue.SimpleQueue()

        def write():
            while self.poll():
                text = input_queue.get()
                if text is None:
                    break

                self.proc.stdin.write(text)
                self.proc.stdin.flush()

        threading.Thread(target=write).start()

        return input_queue

    def kill(self):
        if not self.killed:
            self.killed = True
            if sys.platform == "win32":
                # terminate would not kill process opened by the shell cmd.exe,
                # it will only kill cmd.exe leaving the child running
                subprocess.Popen(f"taskkill /PID {self.proc.pid} /T /F", shell=True)
            else:
                os.killpg(self.proc.pid, signal.SIGTERM)
                self.proc.terminate()

    def poll(self):
        return self.proc.poll() is None

    def exit_code(self):
        return self.proc.poll()

    def read_fileno(self, file, execute_finished):
        decoder = \
            codecs.getincrementaldecoder(self.listener.encoding)('replace')

        while True:
            data = decoder.decode(file.read(2**16))
            data = data.replace('\r\n', '\n').replace('\r', '\n')

            if len(data) > 0 and not self.killed:
                self.listener.on_data(self, data)
            else:
                if execute_finished:
                    sublime.set_timeout(lambda: self.listener.on_finished(self))
                break


class ExecCommand(sublime_plugin.WindowCommand, ProcessListener):
    OUTPUT_LIMIT = 2 ** 27

    def __init__(self, window):
        super().__init__(window)
        self.proc = None
        self.debug_text = ""
        self.encoding = "utf-8"
        self.quiet = False
        self.errs_by_file = {}
        self.show_errors_inline = True
        self.input_queue = None
        self.input_view = sublime.View(0)
        self.output_size = 0
        self.output_view = sublime.View(0)

    def run(
            self,
            cmd=None,
            shell_cmd=None,
            file_regex="",
            line_regex="",
            working_dir="",
            encoding="utf-8",
            env={},
            quiet=False,
            kill=False,
            kill_previous=False,
            update_annotations_only=False,
            word_wrap=True,
            interactive=False,
            syntax="Packages/Text/Plain text.tmLanguage",
            path="",
            # Catches "shell"
            **kwargs):

        if update_annotations_only:
            if self.show_errors_inline:
                self.update_annotations()
            return

        if kill:
            if self.proc:
                self.proc.kill()
            return

        if kill_previous and self.proc:
            self.proc.kill()

        # Prepare build environment

        merged_env = {}
        if env:
            merged_env.update(env)
        if path:
            merged_env["PATH"] = path
        if (view := self.window.active_view()) and (
            user_env := cast(dict[str, str], view.settings().get("build_env", {}))
        ):
            merged_env.update(user_env)

        # Default the to the current files directory if no working directory
        # was given
        if (
            not working_dir
            and (view := self.window.active_view())
            and (file_name := view.file_name())
        ):
            working_dir = os.path.dirname(file_name)

        # Change to the working dir, rather than spawning the process with it,
        # so that emitted working dir relative path names make sense
        if working_dir:
            os.chdir(working_dir)

        # Prepare output panel

        self.output_view, self.input_view = self.window.create_io_panel(
            "exec", self.on_input if interactive else None)

        output_settings = self.output_view.settings()
        build_settings = {
            "result_base_dir": working_dir,
            "result_file_regex": file_regex,
            "result_line_regex": line_regex,
            "word_wrap": word_wrap,
            "syntax": syntax,
        }

        # Treat output as widget. Maybe also "Build Output Widget.sublime-settings"?
        for k, v in sublime.load_settings("Widget.sublime-settings").to_dict().items():
            if k not in build_settings:
                output_settings.set(k, v)

        for k, v in build_settings.items():
            output_settings.set(k, v)

        self.output_view.set_read_only(True)

        preferences_settings = sublime.load_settings("Preferences.sublime-settings")
        if preferences_settings.get("show_panel_on_build", True):
            self.window.run_command("show_panel", {"panel": "output.exec"})

        self.encoding = encoding
        self.quiet = quiet

        if not self.quiet:
            if shell_cmd:
                print("Running " + shell_cmd)
            elif cmd:
                print("Running " + cmd if isinstance(cmd, str) else " ".join(cmd))
            sublime.status_message("Building")

        # Prepare annotations

        self.hide_annotations()
        self.show_errors_inline = preferences_settings.get("show_errors_inline", True)

        # Prepare debug text

        self.debug_text = ""
        if shell_cmd:
            self.debug_text += f"[shell_cmd: {shell_cmd}]\n"
        else:
            self.debug_text += f"[cmd: {cmd!s}]\n"
        self.debug_text += f"[dir: {os.getcwd()}]\n"
        if "PATH" in merged_env:
            self.debug_text += f"[path: {os.path.expandvars(merged_env["PATH"])}]"
        else:
            self.debug_text += f"[path: {os.environ["PATH"]}]"

        # Run process

        self.output_size = 0

        try:
            self.proc = AsyncProcess(cmd, shell_cmd, merged_env, self, path, **kwargs)
            self.proc.start()

            if interactive:
                self.input_queue = self.proc.start_input_thread()
            else:
                self.input_queue = None

        except Exception as e:
            self.write(f"{e!s}\n{self.debug_text}\n")
            if not self.quiet:
                self.write("[Aborted]")

        if interactive:
            self.window.focus_view(self.input_view)

    def is_enabled(self, kill=False, **kwargs):
        return kill is False or self.proc is not None

    def on_input(self, text):
        if not self.input_queue or not self.proc:
            return

        if text[-1] != '\n':
            text += '\n'

        self.write(text)
        self.input_queue.put(text.encode(self.encoding))

    def on_data(self, proc, data):
        if proc != self.proc:
            return

        # Truncate past the limit
        if self.output_size >= self.OUTPUT_LIMIT:
            return

        self.write(data)
        self.output_size += len(data)

        if self.output_size >= self.OUTPUT_LIMIT:
            self.write('\n[Output Truncated]\n')

    def on_finished(self, proc):
        if proc != self.proc:
            return

        if self.input_queue is not None:
            # This signals shutdown
            self.input_queue.put(None)
            self.input_queue = None

        if proc.killed:
            self.write("\n[Cancelled]")
        elif not self.quiet:
            if (elapsed := time.time() - proc.start_time) < 1:
                msg = f"Finished in {elapsed * 1000:.0f}ms"
            else:
                msg = f"Finished in {elapsed:.1f}s"

            if exit_code := proc.exit_code():
                msg = f"[{msg} with exit code {exit_code}]\n{self.debug_text}"
            else:
                msg = f"[{msg}]"

            self.write(msg)

        if proc.killed:
            sublime.status_message("Build cancelled")
        elif errs := self.output_view.find_all_results():
            sublime.status_message(f"Build finished with {len(errs)} errors")
        else:
            sublime.status_message("Build finished")

        self.proc = None

    def write(self, characters):
        self.output_view.run_command(
            'append',
            {'characters': characters, 'force': True, 'scroll_to_end': True})

        if (
            not self.updating_annotations
            and self.show_errors_inline
            and '\n' in characters
        ):
            self.updating_annotations = True
            sublime.set_timeout(self.check_annotations)

    def check_annotations(self):
        errs_by_file = {}
        for file, line, column, text in self.output_view.find_all_results_with_text():
            errs_by_file.setdefault(file, []).append((line, column, text))
        self.errs_by_file = errs_by_file

        self.update_annotations()

    def update_annotations(self):
        for window in sublime.windows():
            for file, errs in self.errs_by_file.items():
                if view := window.find_open_file(file):
                    selection_set = []
                    content_set = []

                    line_err_set = []

                    for line, column, text in errs:
                        pt = view.text_point(line - 1, column - 1)
                        if (line_err_set and
                                line == line_err_set[len(line_err_set) - 1][0]):
                            line_err_set[len(line_err_set) - 1][1] += (
                                "<br>" + html.escape(text, quote=False))
                        else:
                            pt_b = pt + 1
                            if view.classify(pt) & sublime.CLASS_WORD_START:
                                pt_b = view.find_by_class(
                                    pt,
                                    forward=True,
                                    classes=(sublime.CLASS_WORD_END))
                            if pt_b <= pt:
                                pt_b = pt + 1
                            selection_set.append(
                                sublime.Region(pt, pt_b))
                            line_err_set.append(
                                [line, html.escape(text, quote=False)])

                    for _, text in line_err_set:
                        content_set.append(ANNOTATION_TEMPLATE.format(content=text))

                    # add annotations to all clones in current window
                    for clone in (view, *view.clones()):
                        if clone.window() == window:
                            clone.add_regions(
                                "exec",
                                selection_set,
                                scope="invalid",
                                annotations=content_set,
                                flags=(
                                    sublime.DRAW_SQUIGGLY_UNDERLINE
                                    | sublime.DRAW_NO_FILL
                                    | sublime.DRAW_NO_OUTLINE
                                ),
                                on_close=self.hide_annotations,
                            )

        self.updating_annotations = False

    def hide_annotations(self):
        for window in sublime.windows():
            for file in self.errs_by_file:
                if view := window.find_open_file(file):
                    for clone in (view, *view.clones()):
                        if clone.window() == window:
                            clone.erase_regions("exec")
                            clone.hide_popup()

        if view := sublime.active_window().active_view():
            view.erase_regions("exec")
            view.hide_popup()

        self.errs_by_file = {}
        self.show_errors_inline = False
        self.updating_annotations = False


class ExecEventListener(sublime_plugin.EventListener):
    def on_load(self, view):
        w = view.window()
        if w is not None:
            w.run_command('exec', {'update_annotations_only': True})
