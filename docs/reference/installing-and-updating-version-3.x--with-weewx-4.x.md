---
title: Installing version 3.x with WeeWX version 4.x
nav_exclude: true
---

**Note:**, without workarounds WeeWX 4.x does not support python 3.12 and higher.
See this [discussion](https://groups.google.com/g/weewx-user/c/PLYefyx2Pnw) for additional information.

**Note:**, in 4.6.1 WeeWX fixed [737](https://github.com/weewx/weewx/issues/737).
This resulted in different test results and therefore technically MQTTSubscribe only supports WeeWX 4.6.1+.

## Prerequisites

* Python 3.7 or higher
* [Paho MQTT Python client](https://pypi.org/project/paho-mqtt/)

Because there are multiple methods to install [WeeWX V5](https://weewx.com/docs/5.0/usersguide/installing/), location of files can vary.
[See](https://weewx.com/docs/5.0/usersguide/where/) for the definitive information.
The following symbolic names are used to define the various locations:

* *$BIN_ROOT*    - Executables
* *$USER_ROOT*   - User directory
* *$CONFIG_FILE* - The WeeWX configuration file (This is not typically in the WEEWX documentation)

The notation vX.Y.Z designates the version of MQTTSubscribe being installed.

**Prior to making any updates/changes, always make a backup.**

## Set the mode that MQTTSubscribe will be running in

If running as a driver,

```
RUN_MODE=driver
```

If running as a service,

```
RUN_MODE=service
```

## Set the file locations

### For package installs

```
BIN_ROOT=/usr/share/weewx
USER_ROOT=/usr/share/weewx/user
CONFIG_FILE=/etc/weewx/weewx.conf
DOWNLOAD_DIR=/tmp
```

### For setup.py installs

```
BIN_ROOT=/home/weewx/bin
USER_ROOT=/home/weewx/bin/user
CONFIG_FILE=/home/weewx/weewx.conf
DOWNLOAD_DIR=/tmp
```

## Install MQTTSubscribe

```
$BIN_ROOT/wee_extension --install=$DOWNLOAD_DIR/vX.Y.Z.tar.gz
```

**Note:** For package installs, the above command needs to be prefixed with `sudo` (sudo $BIN_ROOT/wee_extension ...)

## Create an example configuration

```
PYTHONPATH=$BIN_ROOT python3 $USER_ROOT/MQTTSubscribe.py configure --create-example mqttsubscribe.template.conf
```

### Configure MQTTSubscribe

Note, MQTTSubscribeDriver can also be configured and weewx.conf updated interactively via
[weectl station](https://weewx.com/docs/5.0/utilities/weectl-about/). This method has the following disadvantages:

* The options that can be configured are limited.
* The configuration options can not be validated and tested before restarting WeeWX.

1. Edit the `mqttsubscribe.template.conf` file

    For example,

    ```
    nano mqttsubscribe.template.conf
    ```

2. Validate and test the `mqttsubscribe.template.conf` file

    ```
    PYTHONPATH=$BIN_ROOT python3 $USER_ROOT/MQTTSubscribe.py configure $RUN_MODE --validate --conf mqttsubscribe.template.conf
    ```

    ```
    PYTHONPATH=$BIN_ROOT python3 $USER_ROOT/MQTTSubscribe.py simulate $RUN_MODE --conf mqttsubscribe.template.conf
    ```

  Additional information on running MQTTSubscribe in configuration mode can be found at this [wiki page]({{site.baseurl}}/configurator-mode).
  
  Additional information on running MQTTSubscribe in simulation mode can be found at this [wiki page]({{site.baseurl}}/simulator-mode).

## If running as a driver, set driver to MQTTSubcribe

```
$BIN_ROOT/wee_config --reconfigure --driver=user.MQTTSubscribe --no-prompt
```

**Note:** For package installs, the above command needs to be prefixed with `sudo` (sudo $BIN_ROOT/wee_config ...)

## Update WeeWX with MQTTSubscribe's configuration

```
PYTHONPATH=$BIN_ROOT python3 $USER_ROOT/MQTTSubscribe.py configure $RUN_MODE --replace-with mqttsubscribe.template.conf --conf $CONFIG_FILE
```

**Note:** For package installs, the above command needs to be prefixed with `sudo` (sudo PYTHONPATH=$BIN_ROOT python3 ...)
