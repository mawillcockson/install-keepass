import sys
import invoke
from invoke import run
from invoke.exceptions import UnexpectedExit
from time import sleep, monotonic
from subprocess import Popen, _cleanup
from faulthandler import dump_traceback
from queue import SimpleQueue
from threading import Thread
import threading
from tempfile import SpooledTemporaryFile as stp

from unittest.mock import patch

# NOTE: Popen's sys.audithook doesn't print out the correct info on Windows :(
def p(*args):
    if args[0] == "subprocess.Popen":
        print(f"shell: {args[1][0]}\nargs: {args[1][1]}")

#sys.addaudithook(p)

popen_kwargs = {
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
    start = monotonic()
    run("echo test", pty=False, hide="both")
    return monotonic()-start

        
def broken():
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

message_queue = SimpleQueue()
flush = sys.stdout.flush

def reader(q):
    while True:
        if not q.empty():
            tup = q.get()
            if tup[0] in ["get", "set"]:
                print(*tup)
                flush()
            elif tup[0] == "end":
                print("stop")
                break
            else:
                raise NotImplementedError("sorry")

        #sleep(0.0001)

_mswindows = (sys.platform == "win32")

import io
import os
import time
import signal
import builtins
import warnings
import errno
from time import monotonic as _time

# Exception classes used by this module.
class SubprocessError(Exception): pass


class CalledProcessError(SubprocessError):
    """Raised when run() is called with check=True and the process
    returns a non-zero exit status.

    Attributes:
      cmd, returncode, stdout, stderr, output
    """
    def __init__(self, returncode, cmd, output=None, stderr=None):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
        self.stderr = stderr

    def __str__(self):
        if self.returncode and self.returncode < 0:
            try:
                return "Command '%s' died with %r." % (
                        self.cmd, signal.Signals(-self.returncode))
            except ValueError:
                return "Command '%s' died with unknown signal %d." % (
                        self.cmd, -self.returncode)
        else:
            return "Command '%s' returned non-zero exit status %d." % (
                    self.cmd, self.returncode)

    @property
    def stdout(self):
        """Alias for output attribute, to match stderr"""
        return self.output

    @stdout.setter
    def stdout(self, value):
        # There's no obvious reason to set this, but allow it anyway so
        # .stdout is a transparent alias for .output
        self.output = value


class TimeoutExpired(SubprocessError):
    """This exception is raised when the timeout expires while waiting for a
    child process.

    Attributes:
        cmd, output, stdout, stderr, timeout
    """
    def __init__(self, cmd, timeout, output=None, stderr=None):
        self.cmd = cmd
        self.timeout = timeout
        self.output = output
        self.stderr = stderr

    def __str__(self):
        return ("Command '%s' timed out after %s seconds" %
                (self.cmd, self.timeout))

    @property
    def stdout(self):
        return self.output

    @stdout.setter
    def stdout(self, value):
        # There's no obvious reason to set this, but allow it anyway so
        # .stdout is a transparent alias for .output
        self.output = value


if _mswindows:
    import threading
    import msvcrt
    import _winapi
    class STARTUPINFO:
        def __init__(self, *, dwFlags=0, hStdInput=None, hStdOutput=None,
                     hStdError=None, wShowWindow=0, lpAttributeList=None):
            self.dwFlags = dwFlags
            self.hStdInput = hStdInput
            self.hStdOutput = hStdOutput
            self.hStdError = hStdError
            self.wShowWindow = wShowWindow
            self.lpAttributeList = lpAttributeList or {"handle_list": []}

        def _copy(self):
            attr_list = self.lpAttributeList.copy()
            if 'handle_list' in attr_list:
                attr_list['handle_list'] = list(attr_list['handle_list'])

            return STARTUPINFO(dwFlags=self.dwFlags,
                               hStdInput=self.hStdInput,
                               hStdOutput=self.hStdOutput,
                               hStdError=self.hStdError,
                               wShowWindow=self.wShowWindow,
                               lpAttributeList=attr_list)

else:
    import _posixsubprocess
    import select
    import selectors

def set_r(self, value):
    fake = stp()
    real_close = fake.close
    fake.close = lambda *a, **k: None
    dump_traceback(fake)
    fake.seek(0)
    message_queue.put(("set", value, fake.read().decode("utf-8")))
    real_close()
    self.__returncode__ = value
def get_r(self):
    fake = stp()
    real_close = fake.close
    fake.close = lambda *a, **k: None
    dump_traceback(fake)
    fake.seek(0)
    message_queue.put(("get", self.__returncode__, fake.read().decode("utf-8")))
    real_close()
    return self.__returncode__
class Popen_access(Popen):
    
    returncode = property(fget=get_r, fset=set_r)
    def __init__(self, args, bufsize=-1, executable=None,
                 stdin=None, stdout=None, stderr=None,
                 preexec_fn=None, close_fds=True,
                 shell=False, cwd=None, env=None, universal_newlines=None,
                 startupinfo=None, creationflags=0,
                 restore_signals=True, start_new_session=False,
                 pass_fds=(), *, encoding=None, errors=None, text=None, message_queue=message_queue):
        """Create new Popen instance."""
        _cleanup()
        # Held while anything is calling waitpid before returncode has been
        # updated to prevent clobbering returncode if wait() or poll() are
        # called from multiple threads at once.  After acquiring the lock,
        # code must re-check self.returncode to see if another thread just
        # finished a waitpid() call.
        self._waitpid_lock = threading.Lock()

        self._input = None
        self._communication_started = False
        if bufsize is None:
            bufsize = -1  # Restore default
        if not isinstance(bufsize, int):
            raise TypeError("bufsize must be an integer")

        if _mswindows:
            if preexec_fn is not None:
                raise ValueError("preexec_fn is not supported on Windows "
                                 "platforms")
        else:
            # POSIX
            if pass_fds and not close_fds:
                warnings.warn("pass_fds overriding close_fds.", RuntimeWarning)
                close_fds = True
            if startupinfo is not None:
                raise ValueError("startupinfo is only supported on Windows "
                                 "platforms")
            if creationflags != 0:
                raise ValueError("creationflags is only supported on Windows "
                                 "platforms")

        self.args = args
        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.pid = None
        self.returncode = None
        self.__returncode__ = None
        self.encoding = encoding
        self.errors = errors

        # Validate the combinations of text and universal_newlines
        if (text is not None and universal_newlines is not None
            and bool(universal_newlines) != bool(text)):
            raise SubprocessError('Cannot disambiguate when both text '
                                  'and universal_newlines are supplied but '
                                  'different. Pass one or the other.')

        # Input and output objects. The general principle is like
        # this:
        #
        # Parent                   Child
        # ------                   -----
        # p2cwrite   ---stdin--->  p2cread
        # c2pread    <--stdout---  c2pwrite
        # errread    <--stderr---  errwrite
        #
        # On POSIX, the child objects are file descriptors.  On
        # Windows, these are Windows file handles.  The parent objects
        # are file descriptors on both platforms.  The parent objects
        # are -1 when not using PIPEs. The child objects are -1
        # when not redirecting.

        (p2cread, p2cwrite,
         c2pread, c2pwrite,
         errread, errwrite) = self._get_handles(stdin, stdout, stderr)

        # We wrap OS handles *before* launching the child, otherwise a
        # quickly terminating child could make our fds unwrappable
        # (see #8458).

        if _mswindows:
            if p2cwrite != -1:
                p2cwrite = msvcrt.open_osfhandle(p2cwrite.Detach(), 0)
            if c2pread != -1:
                c2pread = msvcrt.open_osfhandle(c2pread.Detach(), 0)
            if errread != -1:
                errread = msvcrt.open_osfhandle(errread.Detach(), 0)

        self.text_mode = encoding or errors or text or universal_newlines

        # How long to resume waiting on a child after the first ^C.
        # There is no right value for this.  The purpose is to be polite
        # yet remain good for interactive users trying to exit a tool.
        self._sigint_wait_secs = 0.25  # 1/xkcd221.getRandomNumber()

        self._closed_child_pipe_fds = False

        try:
            if p2cwrite != -1:
                self.stdin = io.open(p2cwrite, 'wb', bufsize)
                if self.text_mode:
                    self.stdin = io.TextIOWrapper(self.stdin, write_through=True,
                            line_buffering=(bufsize == 1),
                            encoding=encoding, errors=errors)
            if c2pread != -1:
                self.stdout = io.open(c2pread, 'rb', bufsize)
                if self.text_mode:
                    self.stdout = io.TextIOWrapper(self.stdout,
                            encoding=encoding, errors=errors)
            if errread != -1:
                self.stderr = io.open(errread, 'rb', bufsize)
                if self.text_mode:
                    self.stderr = io.TextIOWrapper(self.stderr,
                            encoding=encoding, errors=errors)

            self._execute_child(args, executable, preexec_fn, close_fds,
                                pass_fds, cwd, env,
                                startupinfo, creationflags, shell,
                                p2cread, p2cwrite,
                                c2pread, c2pwrite,
                                errread, errwrite,
                                restore_signals, start_new_session)
        except:
            # Cleanup if the child failed starting.
            for f in filter(None, (self.stdin, self.stdout, self.stderr)):
                try:
                    f.close()
                except OSError:
                    pass  # Ignore EBADF or other errors.

            if not self._closed_child_pipe_fds:
                to_close = []
                if stdin == PIPE:
                    to_close.append(p2cread)
                if stdout == PIPE:
                    to_close.append(c2pwrite)
                if stderr == PIPE:
                    to_close.append(errwrite)
                if hasattr(self, '_devnull'):
                    to_close.append(self._devnull)
                for fd in to_close:
                    try:
                        if _mswindows and isinstance(fd, Handle):
                            fd.Close()
                        else:
                            os.close(fd)
                    except OSError:
                        pass

            raise

if __name__ == "__main__":
    # How long does it take to run invoke.run()?
    #print(sum(s() for x in range(1000))/1000)
    # On my machines, Linux: 0.00082, Windows: 0.009
    # Linux is i3-6100U, Windows i7-6700
    
    # Does my Popen_access work?
    #printer = Thread(target=reader, kwargs={"q":message_queue})
    #printer.start()
    #process = Popen_access(**popen_kwargs)
    #process.wait()
    #print(process.returncode)
    # Appears to

    printer = Thread(target=reader, kwargs={"q":message_queue})
    printer.start()
    with patch("invoke.runners.Popen", new=Popen_access):
        try:
            run("echo test")
        except:
            message_queue.put(("end", "stop"))


    message_queue.put(("end", "stop"))
    printer.join(timeout=0.1)
