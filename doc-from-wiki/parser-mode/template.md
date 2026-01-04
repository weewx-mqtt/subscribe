<!-- markdownlint-disable MD024 -->

# Parse MQTT 'message' data

Note, this function was intoduced in MQTTSubscribe version 3.0.

This reads data from a file and attempts to parse it into WeeWX format.

This functionality is useful for people that do not have acces to the live MQTT feed,
such as MQTTSubscribe developers.

## Environment setup

### Set the mode that MQTTSubscribe will be running in

If running as a driver,

```
RUN_MODE=driver
```

If running as a service,

```
RUN_MODE=service
```

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
WEECTL=weectl
```

#### For package installs

```
WEEWX_ROOT=/etc/weewx/
export BIN_ROOT=/usr/share/weewx/
export USER_ROOT=$WEEWX_ROOT/bin/user
CONFIG_FILE=$WEEWX_ROOT/weewx.conf
WEECTL=weectl
```

#### For git 'installs'

```
WEEWX_REPO=~/weewx
WEEWX_ROOT=~/weewx-data
export BIN_ROOT=$WEEWX_REPO/src
export USER_ROOT=$WEEWX_ROOT/bin/user
CONFIG_FILE=$WEEWX_ROOT/weewx.conf
WEECTL=$WEEWX_REPO/bin/weectl
```

## Invocation

```
python3 $USER_ROOT/MQTTSubscribe.py parse $RUN_MODE --help
```

## Options

### --conf CONF

The WeeWX configuration file. Typically weewx.conf.
  
### --console

Log to console in addition to syslog.

### --logging-file LOGGING_FILE

Log to specified file.

### --logging-level

Specify the level of logging.
Valid values are, DEBUG, INFO, TRACE.

### --message-file

The file containing the MQTT message.

### --top-level

Use the complete input configuration as the MQTTSubscribeDriver/MQTTSubscribeService configuration section.

### -- topic

The topic to 'publish' the '--message-file' message.
