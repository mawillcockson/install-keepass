# Installing [KeePass][]

This repository walks through installing [KeePass][] on Windows in a particular way.

It downloads [KeePass][] using [Python][] and [scoop][], and sets a [Scheduled Task][tasksch] to check for updates daily.

Follow this document to get started.

## Getting Started

To begin with, this will only work on recent versions of Windows. Running through the first step will tell us if your version of Windows is recent enough.

We'll install [Python][] first, as that is what this requires. The easiest way to do that would be to open a [PowerShell][] terminal by opening the Start Menu and typing PowerShell. This should look something like this:

![PowerShell in the Sart Menu][pwsh-start]

Select the first one, and a window should open. On some systems, it may take a moment for the terminal to load. Once you see the prompt `> ` with a blinking cursor as below, you're ready.

![PowerShell opened and ready][pwsh-ready]

Simply type `python` and hit <kbd>Enter</kbd>. If this opens the Microsoft Store app, then you are running a recent enough version of Windows to continue with this guide.

If, instead, an error message like below was printed, your version of Windows is not recent enough to work with this guide.

![PowerShell doesn't know about Python][pwsh-error]

From the Microsoft Store, install Python:

![Install Python from the Microsoft Store][msstore-python]

If this doesn't work, an installer can be downloaded from [the Python website here][py-installer]. During installation, the only option that needs to be changed from the default is `Add to PATH`, as in the screenshot below:

![Python.org installer][python-installer]

The above only needs to be done if Python cannot be installed through the Microsoft Store.

Once Python is installed, the Microsoft Store can be closed, and we'll return to the PowerShell terminal. This terminal does not know about the new Python yet, as it was just installed, so we'll update it with the following command. This command can be typed into the terminal, or copied and pasted, and it can be executed by pressing <kbd>Enter</kbd> after it's been typed or pasted:

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

Now, we can make sure Python is working properly by running the following command.

```powershell
python --version
```

Additionally, we can make sure a Python component named `pip` was installed properly by running:

```powershell
python -m pip --version
```

This should print out something like the following:

![pip version][pip-version]

If instead an error like the following is printed out, `pip` was not installed, and this guide can no longer be used.

With Python installed, we can continue to [the next section](#run-script).

## Run script

This repository includes [a script](./install.py) that is used to do the rest of the setup, which we'll now have Python download and run witht he following command. This command can be run from the same PowerShell terminal as the commands we ran in the previous section.

```powershell
python -c "import sys;sys.exit('Python 3.7 or higher required') if sys.version_info<=(3,7) else '';from urllib.request import urlopen as o;r=o('https://raw.githubusercontent.com/mawillcockson/install-keepass/master/install.py').read();f=open('install.py','wb');f.write(r);f.close()"
```

[keepass]: <https://keepass.info/>
[python]: <https://www.python.org/>
[scoop]: <https://github.com/lukesampson/scoop>
[tasksch]: <https://docs.microsoft.com/en-us/windows/win32/taskschd/about-the-task-scheduler>
[powershell]: <https://docs.microsoft.com/powershell/scripting/overview>
[py-installer]: <https://www.python.org/ftp/python/3.8.1/python-3.8.1.exe>
[pwsh-start]: <https://i.imgur.com/VNXBFcJ.png>
[pwsh-ready: <https://i.imgur.com/yhooXCa.png>
[pwsh-error]: <https://i.imgur.com/yY8gNnL.png>
[msstore-python]: <https://i.imgur.com/Uyd4SK3.png>
[python-installer]: <https://i.imgur.com/Ml0DdgU.png>
[pip-version]: <https://i.imgur.com/xgD9A33.png>