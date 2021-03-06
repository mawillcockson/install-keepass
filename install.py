#!/usr/bin/env python

import argparse
import importlib.util
import re
import sys
import tempfile
from pathlib import Path
from subprocess import run

try:
    import venv
except ImportError as err:
    print(
        "Cannot find Python venv module\n"
        "If on Debian, please install it with either of:\n"
        "su -c 'apt-get install python3-venv'\n",
        "sudo apt-get install python3-venv",
        "If on Windows, try reinstalling",
        "Python with the standard library",
        file=sys.stderr,
    )
    sys.exit(1)

if sys.platform != "win32":
    print(OSError("Not Windows :("))
    sys.exit(1)
if sys.version_info<(3,7):
    print("Python too old\nNeed 3.7 or newer")
    sys.exit(1)

### Program defaults
# NOTE: Make configurable through arguments/flags/environment variables
default_install_dir: str = "~/projects/dotfiles"
PROG_NAME: str = "install"
TASK_FUNC_PREFIX: str = "atask"

### Tasks to execute with invoke ###


def atask_default(ctx):
    print("Running script...")

def atask_install_scoop(ctx):
    from invoke.watchers import Responder
    breakpoint()
    ctx.run(
        command="Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned",
        watchers=[
            Responder(
                pattern=r".*default is \"N\".*",
                response="A\n",
            )
        ],
    )
    sys.exit(1)
    ctx.run('powershell "iwr -useb https://get.scoop.sh | iex"')
    #ctx.run("""powershell "$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')\"""")
    ctx.run("scoop install git aria2")
    ctx.run("scoop bucket add extras")
    ctx.run("scoop update")

def atask_install_keepass(ctx):
    ctx.run("scoop install keepass keepass-plugin-keeanywhere")

def atask_setup_keepass(ctx):
    # KeePass import triggers
    pass

def atask_schedule_updates(ctx):
    # Schedule task
    pass


### Setup and argument parsing ###


def ensure_invoke() -> tempfile.TemporaryDirectory:
    ## Make a venv
    # Must make a variable to hold the TemopraryDirectory; wrapping it in Path() effectively deletes it,
    # as passing the call to TemporaryDirectory directly to Path() discards it once Path drops a reference to it,
    # and the dir is removed upon deletion of the object
    #temp_dir = tempfile.TemporaryDirectory()
    # NOTE: Change back after testing!
    temp_dir = Path("./temp-venv")
    if temp_dir.exists() and not temp_dir.is_dir():
        raise NotADirectoryError(f"{temp_dir} is not a directory")
    venv_dir = Path(temp_dir.name)
    print(f"Installing virtual environment for Python into '{venv_dir}'")

    if not temp_dir.exists():
        venv.create(
            env_dir=venv_dir,
            clear=False,  # We explicitly want to fail if the dir isn't empty
            with_pip=True,
        )

    # Install invoke
    print(f"Installing invoke module into {venv_dir}")

    venv_python = (venv_dir / "Scripts" / "python.exe").absolute()

    if not venv_python.is_file():  # Also tests for existence
        print(
            f"{venv_dir} exists but cannot find python{'.exe' if sys.platform == 'win32' else ''}",
            file=sys.stderr,
        )
        sys.exit(1)

    ret = run(
        [str(venv_python), "-m", "pip", "install", "invoke"],
        capture_output=True,
        text=True,
    )

    if not ret.returncode == 0:
        print(f"Error installing invoke:\n{ret.stderr}", file=sys.stderr)
        sys.exit(1)

    print(ret.stdout)

    # Find the site-packages folders
    lib_dirs = [
        x
        for x in venv_dir.iterdir()
        if x.is_dir() and x.name in ["Lib", "lib", "lib64"]
    ]
    if len(lib_dirs) < 1:
        print(f"Could not find any lib folders in {venv_dir}", file=sys.stderr)
        sys.exit(1)
    site_folders = [
        (p / "site-packages") for p in lib_dirs if (p / "site-packages").is_dir()
    ]
    # On some platforms, and intermediate "python3.7" folder is used: /tmp/tmp2tcvye33/lib/python3.7/site-packages
    python_ver = f"python{sys.version_info.major}.{sys.version_info.minor}"
    site_folders.extend(
        (p / python_ver / "site-packages")
        for p in lib_dirs
        if (p / python_ver / "site-packages").is_dir()
    )
    sys.path.extend(map(str, site_folders))

    # importlib.util.spec_from_file_location() supposedly can confirm if a module exists at a location,
    # but importlib.util.module_from_spec() loads only a single file, whereas the import statement does more?
    # Anyways, we're going to be importing invoke anyways, so doing the real thing is the best way to test.
    try:
        import invoke
    except ImportError as err:
        print(f"Can't import invoke package:\n{err}", file=sys.stderr)
        print(sys.path)
        sys.exit(1)

    return temp_dir


def main() -> None:
    # This says importlib.util.find_spec() can test if a module is currently importable:
    # https://docs.python.org/3/library/importlib.html#importlib.util.find_spec
    if not importlib.util.find_spec("invoke"):
        ensure_invoke()

    from invoke import task, Program, Config, Collection
    from invoke.config import merge_dicts
    from invoke.watchers import Responder

    namespace = Collection()
    globs = dict(globals())
    namespace.add_task(task(atask_default, post=[
        atask_install_scoop,
        atask_install_keepass,
        atask_setup_keepass,
        atask_schedule_updates,
    ]), default=True)
    for i,name in enumerate(namespace.tasks["atask-default"].post):
        namespace.tasks["atask-default"].post[i] = task(name)
        namespace.add_task(task(name))

    class SetupConfig(Config):
        prefix: str = PROG_NAME

        @staticmethod
        def global_defaults():
            base_defaults = Config.global_defaults()
            overrides = {
                "tasks": {"collection_name": PROG_NAME},
                "run": {
                    "shell": "C:\\WINDOWS\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
                    "echo": True,
                    "debug": True,
                },
            }
            return merge_dicts(base=base_defaults, updates=overrides)

    program = Program(
        name=PROG_NAME, namespace=namespace, config_class=SetupConfig, version="0.0.1"
    )
    # NOTE: Debug
    # This uses the Python auditing framework in Python 3.8+
    if sys.version_info>=(3,8):
        print("auditing enabled")

        def print_popen(*args, **kwargs) -> None:
            if args[0] == "subprocess.Popen":
                # sys.audit("subprocess.Popen", executable, args, cwd, env)
                # ("subprocess.Popen", (executable, args, cwd, env))
                print(f"{args[1][0]} -> {args[1][1]}")

        sys.addaudithook(print_popen)
    program.run()


if __name__ == "__main__":
    main()
