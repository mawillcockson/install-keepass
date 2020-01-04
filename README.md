# Installing [KeePass][]

This repository walks through installing [KeePass][] on Windows in a particular way.

It downloads [KeePass][] using [Python][] and [scoop][], and sets a [Scheduled Task][tasksch] to check for updates daily.

Follow this document to get started.

## Getting Started

To begin with, this will only work on recent versions of Windows. Performing the first step will tell us if your version of Windows is recent enough.

This guide relies on [Python][], which we'll install now. Open a [PowerShell][] terminal by opening the Start Menu and typing `PowerShell`. This should look something like this:

![PowerShell in the Sart Menu][pwsh-start]

Select the first one, and a window should open. On some systems, it may take a moment for the terminal to load. Once you see the prompt `PS C:\User\user> ` with a blinking cursor as below, you're ready.

![PowerShell opened and ready][pwsh-ready]

Simply type `python` and hit <kbd>Enter</kbd>. If this opens the Microsoft Store app, then you are running a recent enough version of Windows to continue with this guide.

If, instead, an error message like below was printed, your version of Windows is not recent enough to work with this guide.

![PowerShell doesn't know about Python][pwsh-error]

From the Microsoft Store, install Python:

![Install Python from the Microsoft Store][msstore-python]

Once Python is installed, we'll return to the PowerShell terminal. This terminal does not know about the new Python yet, as it was just installed, so we'll close it and then reopen PowerShell.

Now, we can make sure Python is working properly by running the following command in our refreshed terminal.

```powershell
python --version
```

Additionally, we can make sure a Python component named `pip` was installed properly, by running:

```powershell
python -m pip --version
```

This should print out something like the following:

![pip version][pip-version]

If instead an error is printed out, `pip` was not installed, and this guide can no longer be used.

With Python installed, we can continue to [the next section](#run-script).

## Run script

This repository includes [a script](./install.py) that is used to do the rest of the setup, which we'll now have Python download and run with the following command. This command can be run from the same PowerShell terminal as the commands we ran in the previous section.

```powershell
python -c "import sys;sys.exit('Python 3.7 or higher required') if sys.version_info<(3,7) else '';from urllib.request import urlopen as o;r=o('https://raw.githubusercontent.com/mawillcockson/install-keepass/master/install.py').read();f=open('install.py','wb');f.write(r);f.close();exec(r)"
```

The above command will download and save [the script](./install.py) as `install.py`. To restart the installation, run the above command again, or if it has been run once:

```powrshell
python install.py
```

The script will print out information on its progress, and will report any errors as the second to last line of output in the terminal. If all goes well, KeePass should open, ready to be used.

[keepass]: <https://keepass.info/>
[python]: <https://www.python.org/>
[scoop]: <https://github.com/lukesampson/scoop>
[tasksch]: <https://docs.microsoft.com/en-us/windows/win32/taskschd/about-the-task-scheduler>
[powershell]: <https://docs.microsoft.com/powershell/scripting/overview>
[py-installer]: <https://www.python.org/downloads/>
[pwsh-start]: <https://i.imgur.com/VNXBFcJ.png>
[pwsh-ready]: <https://i.imgur.com/yhooXCa.png>
[pwsh-error]: <https://i.imgur.com/yY8gNnL.png>
[msstore-python]: <https://i.imgur.com/Uyd4SK3.png>
[python-installer]: <https://i.imgur.com/Ml0DdgU.png>
[pip-version]: <https://i.imgur.com/xgD9A33.png>
