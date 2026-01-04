<!-- markdownlint-disable no-duplicate-heading -->

# Installing and Updating Version 2.X and Earlier

**Note:** It is rare that MQTTSubscribe should be configured to run as both a `service` and `driver`.
If you are augmenting an existing driver's data, run MQTTSubscribe as a `service`. Otherwise, run it as a `driver`.

Because there are multiple methods to install [WeeWX V5](https://weewx.com/docs/5.0/usersguide/installing/), location of files can vary.
[See](https://weewx.com/docs/5.0/usersguide/where/) for the definitive information.
The following symbolic names are used to define the various locations:

* *$WEEWX_REPO*  - For git 'installs', the location of the repository (This is not typically in the WEEWX documentation)
* *$WEEWX_ROOT*  - WeeWX root directory
* *$BIN_ROOT*    - Executables
* *$USER_ROOT*   - User directory
* *$CONFIG_FILE* - The WeeWX configuration file (This is not typically in the WEEWX documentation)
* *$WEECTL*      - The `weectl` program (This is not typically in the WEEWX documentation)

The notation vX.Y.Z designates the version of MQTTSubscribe being installed.

**Prior to making any updates/changes, always make a backup.**

## Prerequisites

* Python 3.7 or higher
* [Paho MQTT Python client](https://pypi.org/project/paho-mqtt/)

## Installing with WeeWX Version 5.x

### For pip and git installs - activate the environment

```
source ~/weewx-venv/bin/activate
```

### Set the file locations

#### For pip installs

```
WEEWX_ROOT=~/weewx-data
export USER_ROOT=$WEEWX_ROOT/bin/user
CONFIG_FILE=$WEEWX_ROOT/weewx.conf
DOWNLOAD_DIR=/tmp
WEECTL=weectl
```

#### For package installs

```
WEEWX_ROOT=/etc/weewx/
export BIN_ROOT=/usr/share/weewx/
export USER_ROOT=$WEEWX_ROOT/bin/user
CONFIG_FILE=$WEEWX_ROOT/weewx.conf
DOWNLOAD_DIR=/tmp
WEECTL=weectl
```

#### For git 'installs'

```
WEEWX_REPO=~/weewx
WEEWX_ROOT=~/weewx-data
export BIN_ROOT=$WEEWX_REPO/src
export USER_ROOT=$WEEWX_ROOT/bin/user
CONFIG_FILE=$WEEWX_ROOT/weewx.conf
DOWNLOAD_DIR=/tmp
WEECTL=$WEEWX_REPO/bin/weectl
```

### Download MQTTSubscribe

```
wget -P $DOWNLOAD_DIR https://github.com/weewx-mqtt/subscribe/archive/vX.Y.Z.tar.gz
```

### Install and Configure MQTTSubscribe

* As a driver

```
$WEECTL extension install $DOWNLOAD_DIR/vX.Y.z.tar.gz
$WEECTL station reconfigure --driver=user.MQTTSubscribe
```

**Note:** By default when installing, the service is installed and configured, but not enabled.
To not install and configure the service (only install the file(s)),
set the environment variable MQTTSubscribe_install_type to DRIVER. For example,

```
MQTTSubscribe_install_type=DRIVER $WEECTL extension install $DOWNLOAD_DIR/vX.Y.z.tar.gz
```

And then configure the driver.

```
$WEECTL station reconfigure --driver=user.MQTTSubscribe
```

* As a service

```
$WEECTL extension install $DOWNLOAD_DIR/vX.Y.z.tar.gz
```

**Note:** By default when installing, the service is installed and configured, but not enabled.
To enable, set the environment variable MQTTSubscribe_install_type to SERVICE. For example,

```
MQTTSubscribe_install_type=SERVICE $WEECTL extension install $DOWNLOAD_DIR/vX.Y.z.tar.gz
```

In either case, **edit the [MQTTSubscribeDriver] or [MQTTSubscribeService] stanza as required**.
At the very least the [\[topics\]] stanza must be configured to the topics to subscribe to.
Other settings such as host and port may need to be changed.
See, [configuring MQTTSubscribe](https://github.com/weewx-mqtt/subscribe/wiki/Configuring).

For example,

```
nano $CONFIG_FILE
```

**Note, for package installs:**  
If you just installed WeeWX, you may need to create a new shell/terminal or logout/login
for the user that installed WeeWX to have permission to update WeeWX.
For more information see [Understanding permissions](https://github.com/weewx/weewx/wiki/Understanding-permissions#the-weewx-user-and-group)

### Restart WeeWX

## Installing with WeeWX Version 4.x

### Set the file locations

#### For package installs

```
BIN_ROOT=/usr/share/weewx
USER_ROOT=/usr/share/weewx/user
CONFIG_FILE=/etc/weewx/weewx.conf
DOWNLOAD_DIR=/tmp
```

#### For setup.py installs

```
BIN_ROOT=/home/weewx/bin
USER_ROOT=/home/weewx/bin/user
CONFIG_FILE=/home/weewx/weewx.conf
DOWNLOAD_DIR=/tmp
```

### Download MQTTSubscribe

```
wget -P $DOWNLOAD_DIR https://github.com/weewx-mqtt/subscribe/archive/vX.Y.Z.tar.gz
```

### Install and Configure MQTTSubscribe

* As a driver

```
$BIN_ROOT/wee_extension --install=$DOWNLOAD_DIR/vX.Y.Z.tar.gz
$BIN_ROOT/wee_config --reconfigure --driver=user.MQTTSubscribe
```

**Note:** By default when installing, the service is installed and configured, but not enabled.
To not install and configure the service (only install the file(s)),
set the environment variable MQTTSubscribe_install_type to DRIVER. For example,

```
MQTTSubscribe_install_type=DRIVER $BIN_ROOT/wee_extension --install=$DOWNLOAD_DIR/vX.Y.Z.tar.gz
```

And then configure the driver.

```
$BIN_ROOT/wee_config --reconfigure --driver=user.MQTTSubscribe
```

* As a service

```
$BIN_ROOT/wee_extension --install=$DOWNLOAD_DIR/vX.Y.Z.tar.gz
```

**Note:** By default when installing, the service is installed and configured, but not enabled.
To enable, set the environment variable MQTTSubscribe_install_type to SERVICE. For example,

```
MQTTSubscribe_install_type=SERVICE $BIN_ROOT/wee_extension --install=$DOWNLOAD_DIR/vX.Y.Z.tar.gz
```

In either case, **edit the [MQTTSubscribeDriver] or [MQTTSubscribeService] stanza as required**.
At the very least the [\[topics\]] stanza must be configured to the topics to subscribe to.
Other settings such as host and port may need to be changed.
See, [configuring MQTTSubscribe](https://github.com/weewx-mqtt/subscribe/wiki/Configuring).

For example,

```
nano $CONFIG_FILE
```

**Note:** For package installs, the above commands needs to be prefixed with `sudo`.

### Restart WeeWX
