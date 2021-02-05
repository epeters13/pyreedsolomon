# Original Author    : Edwin G. W. Peters @ epeters
#   Creation date    : Fri Feb  5 18:18:50 2021 (+1100)
#   Email            : edwin.g.w.petersatgmail.com
# ------------------------------------------------------------------------------
# Last-Updated       : Fri Feb  5 18:23:54 2021 (+1100)
#           By       : Edwin G. W. Peters @ epeters
# ------------------------------------------------------------------------------
# File Name          : git_helpers.py
# Description        : 
# ------------------------------------------------------------------------------
# Copyright          : GPLV3
# ------------------------------------------------------------------------------

"""
Snippets borrowed from https://github.com/inducer/pycuda/blob/master/aksetup_helper.py
"""

DASH_SEPARATOR = '------------------------'
count_down_delay = 5
def _run_git_command(cmd):
    git_error = None
    from subprocess import Popen, PIPE
    stdout = None
    try:
        popen = Popen(["git"] + cmd, stdout=PIPE)
        stdout, stderr = popen.communicate()
        if popen.returncode != 0:
            git_error = "git returned error code %d: %s" % (popen.returncode, stderr)
    except OSError:
        git_error = "(OS error, likely git not found)"

    if git_error is not None:
        print(DASH_SEPARATOR)
        print("Trouble invoking git")
        print(DASH_SEPARATOR)
        print("The package directory appears to be a git repository, but I could")
        print("not invoke git to check whether my submodules are up to date.")
        print("")
        print("The error was:")
        print(git_error)
        print("Hit Ctrl-C now if you'd like to think about the situation.")
        print(DASH_SEPARATOR)
    if stdout:
        return stdout.decode("utf-8"), git_error
    else:
        return '', "(subprocess call to git did not succeed)"


def check_git_submodules():
    from os.path import isdir
    if not isdir(".git"):
        # not a git repository
        return
    if isdir("../.repo"):
        # assume repo is in charge and bail
        return

    stdout, git_error = _run_git_command(["submodule", "status"])
    if git_error is not None:
        return

    pkg_warnings = []

    lines = stdout.split("\n")
    for l in lines:
        if not l.strip():
            continue

        status = l[0]
        sha, package = l[1:].split(" ", 1)

        if package == "bpl-subset" or (
                package.startswith("boost") and package.endswith("subset")):
            # treated separately
            continue

        if status == "+":
            pkg_warnings.append("version of '%s' is not what this "
                    "outer package wants" % package)
        elif status == "-":
            pkg_warnings.append("subpackage '%s' is not initialized"
                    % package)
        elif status == " ":
            pass
        else:
            pkg_warnings.append("subpackage '%s' has unrecognized status '%s'"
                    % package)

    if pkg_warnings:
            print(DASH_SEPARATOR)
            print("git submodules are not up-to-date or in odd state")
            print(DASH_SEPARATOR)
            print("If this makes no sense, you probably want to say")
            print("")
            print(" $ git submodule update --init")
            print("")
            print("to fetch what you are presently missing and "
                    "move on with your life.")
            print("If you got this from a distributed package on the "
                    "net, that package is")
            print("broken and should be fixed. Please inform whoever "
                    "gave you this package.")
            print("")
            print("These issues were found:")
            for w in pkg_warnings:
                print("  %s" % w)
            print("")
            print("I will try to initialize the submodules for you "
                    "after a short wait.")
            print(DASH_SEPARATOR)
            print("Hit Ctrl-C now if you'd like to think about the situation.")
            print(DASH_SEPARATOR)

            from os.path import exists
            if not exists(".dirty-git-ok"):
                stdout, git_error = _run_git_command(
                        ["submodule", "update", "--init"])
                if git_error is None:
                    print(DASH_SEPARATOR)
                    print("git submodules initialized successfully")
                    print(DASH_SEPARATOR)
