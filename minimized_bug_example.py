import sys
from invoke import run
from invoke.exceptions import UnexpectedExit
from time import sleep

assert sys.version_info>=(3,8)

def p(*args):
    if args[0] == "subprocess.Popen":
        print(f"shell: {args[1][0]}\nargs: {args[1][1]}")

sys.addaudithook(p)

while True:
    try:
        run("echo Does work", shell="C:\\WINDOWS\\system32\\cmd.exe")
        run('Write-Host -ForegroundColor Red "Works intermittently"', shell="C:\\WINDOWS\\System32\\WindowsPowerShell\\v1.0\\powershell.exe")
        print("yup")
    except UnexpectedExit:
        print("nope")
    
    sleep(1)