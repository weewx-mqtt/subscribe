---
title: Service Simulation
parent: Simulator Mode
nav_order: 4
---

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
