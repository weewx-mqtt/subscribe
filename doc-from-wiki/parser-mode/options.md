---
title: Options
parent: Parser Mode
nav_order: 3
---

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
