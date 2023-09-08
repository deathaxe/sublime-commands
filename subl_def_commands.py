'''
Purpose:
Compares "Default.sublime-commands" (manually extracted from "Packages/Default.sublime-package")
against the user's file "SublimeText/Data/Packages/Default/Default.sublime-commands"
to ensure the latter one contains all the commands from the standard "Default.sublime-commands".

Output:
Prints commands which are unique for "Default.sublime-commands" from "Packages/Default.sublime-package".
'''


def read_commands_from_file(fname: str):
    cmds = set()
    with open(fname) as f:
        for ln in f.readlines():
            ln = ln.strip()
            if ln:
                n = ln.find('"command"')
                if n >= 0:
                    cmd = ln[n:]
                    cmds.add(cmd)
    return cmds


def run():
    cmds1 = read_commands_from_file("Default.sublime-commands")
    cmds2 = read_commands_from_file("SublimeText/Data/Packages/Default/Default.sublime-commands")
    for cmd in cmds1:
        if cmd not in cmds2:
            print(cmd)


run()
