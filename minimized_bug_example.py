import sys
from invoke import run
from invoke.exceptions import UnexpectedExit
from time import sleep, monotonic
from subprocess import Popen

def p(*args):
    if args[0] == "subprocess.Popen":
        print(f"shell: {args[1][0]}\nargs: {args[1][1]}")

#sys.addaudithook(p)

kwargs = {
    "args": 'echo test',
    "bufsize": -1,
    "executable": '/bin/bash',
    "stdin": -1,
    "stdout": -1,
    "stderr": -1,
    "preexec_fn": None,
    "close_fds": True,
    "shell": True,
    "cwd": None,
    "universal_newlines": None,
    "startupinfo": None,
    "creationflags": 0,
    "restore_signals": True,
    "start_new_session": False,
    "pass_fds": (),
}
def s():
    poll = Popen(**kwargs).poll
    start = monotonic()
    while poll() is None:
        0
    return monotonic()-start

print(sum(s() for x in range(1000))/1000)
        
sys.exit(0)

while True:
    try:
        breakpoint()
        run("echo test", pty=False)
        #run("echo Does work", shell="C:\\WINDOWS\\system32\\cmd.exe")
        run('Write-Host -ForegroundColor Red "Works intermittently"', shell="C:\\WINDOWS\\System32\\WindowsPowerShell\\v1.0\\powershell.exe")
        print("yup")
    except UnexpectedExit:
        print("nope")
    
    sleep(1)
