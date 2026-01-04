<!-- markdownlint-disable MD024 -->

# Simulating running WeeWX

Note, this function was intoduced in MQTTSubscribe version 3.0.

This runs MQTTSubscribe in an environment that is very close to running MQTTSubscribe with WeeWX.
This serves the following purposes.

1. The MQTTSubscribe configuration can be tested prior to updating the configuration (weewx.conf) being used by WeeWX.
2. The MQTTSubscribe configuration can be debugged without having to update the configuration (weewx.conf) being used by WeeWX.

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
python3 $USER_ROOT/MQTTSubscribe.py simulate $RUN_MODE --help
```

## driver simulation options

### --archive-delay ARCHIVE_DELAY

The simulated archive delay in seconds.

### --archive-interval ARCHIVE_INTERVAL

The simulated archive interval in seconds.

### --binding {archive,loop}

The type of binding.

### --conf CONF

The WeeWX configuration file. Typicall weewx.conf.

### --console

Log to console in addition to syslog.
  
### --logging-file LOGGING_FILE

Log to specified file.

### --logging-level

Specify the level of logging.
Valid values are, DEBUG, INFO, TRACE.

### --records RECORD_COUNT

The number of archive records to create.

## service simulation options

### --binding {archive,loop}

The type of binding.

### --conf CONF

The WeeWX configuration file. Typically weewx.conf.
  
### --console

Log to console in addition to syslog.

### --frequency FREQUENCY

The frequency that the simulated loop packets/archive records arrive.

### --logging-file LOGGING_FILE

Log to specified file.

### --logging-level

Specify the level of logging.
Valid values are, DEBUG, INFO, TRACE.

### --records RECORD_COUNT

The number of archive records to create.
  
### --units {US,METRIC,METRICWX}

The default units if not in MQTT payload.
