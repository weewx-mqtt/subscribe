# Installing the paho-mqtt package

I am not an expert on packaging, corrections and clarifications welcome!

## Outside any virtual environment

Performing `pip install paho-mqtt` or any of its variants, `pip3`, `python3 -m pip`, etc. performs a 'local install'.
If WeeWX was installed via the OS package manager, `sudo` is required to install MQTTSubscribe.
When `sudo` is used, the local installation of paho-mqtt will not be found.

One way to get around this is to use `sudo pip install paho-mqtt`.
This is discouraged because installing python packages this way may break system dependencies.

The preferred way appears to be,  installing paho-mqtt with the OS package manager.
The package `python3-paho-mqtt` seems to be widely available.
So for exampke on debian flavors of linux it would be `sudo apt install python3-paho-mqtt`.

## Using a virtual environment

Because you are in a virtual environment, `pip install paho-mqtt` installs into that environment and the OS is protected.
