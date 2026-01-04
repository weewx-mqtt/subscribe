---
title: Experimental Options
nav_order: 5
---

These may change or go away.

## The `[MQTTSubscribeDriver]/[MQTTSubscribeSection]` section

This configures the MQTT connection and any necessary WeeWX options.

### archive_topic

Payload in this topic is processed like an archive record.
This means that MQTTSubscribe is running in ‘hardware generation’ mode. The default is `None`. This is only used by the driver.

### console

In addition to any WeeWX logging setup, MQTTSubscribe will also log to the console. The default is `None`.

### logging_filename

In addition to any WeeWX logging setup, MQTTSubscribe will also log to the specified filename. The default is `None`.

### logging_level

Overrides the WeeWX ‘debug’ setting. Valid values are Python’s logging levels, `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, and `NOTSET`.
An additional value `TRACE` is also supported. This logs even more detail than `DEBUG`. The default value is `NOTSET`.
But in this case `NOTSET` means to use the WeeWX ‘debug’ setting.

### max_loop_interval

**Coming soon.**

When no loop packet has been generated in max_loop_interval, MQTTSubscribeDriver will generate an 'empty' packet.
This can be useful to ensure that archive processing regulary happens when the MQTT payload arrives very irregularly.
Only used by the driver.
The default is 0 (off).

### message_callback_provider

Experimental option to specify different message parsers.

## The `[[topics]]` section

### collect_observations = False

With the exception of wind data, by default a packet is created for every MQTT message received.
When this is true, MQTTSubscribe attempts to collect observations across messages into a packet.
Default is False.

### collect_wind_across_loops = True

By default wind data is collected together across generation of loop packets.
Setting to false results in the data only being collected together within a loop packet.
Default is True.

### single_queue = False

With the exception of wind data, by default a queue is created for every MQTT topic.
When this is true, MQTTSubsribe uses a single queue for all non wind data.
This is useful when 'collect_observations = True'.
Default is False.

### The `[[[topic-name]]]` sections

#### topic_tail_is_fieldname = False

When true, the last segment of the topic is used as the fieldname.
Only used for individual payloads.
Default is False.

## The `[[logging]]` section

### The `[[[throttle]]]` section

**Coming soon.**

The configuration to control throttling the logging.
Throttling uses a fixed window rate limit algorithm.
But, every 'max' messages in a 'window' will always be logged.

Throttling logging may result in important log messages being missed.
This may make it hard, to impossible, to debug problems.

EXPERIMENTAL and should be used at your own risk.

#### The `[[[[category]]]]` section

##### The `[[[[[ALL]]]]]` category section

Configuration data for 'every' message that is logged.
This can be overriden for specific logging levels and/or specific messages.

###### max

The maximum number of messages to be logged in the specified interval.

###### duration

The time interval in seconds for which the logged messages will be limited.

##### The `[[[[[ERROR]]]]]` category section

Configuration data for error level messages.
This can be overriden for specific messages.

###### max

The maximum number of messages to be logged in the specified interval.

###### duration

The time interval in seconds for which the logged messages will be limited.

##### The `[[[[[INFO]]]]]` category section

Configuration data for informational level messages.
This can be overriden for specific messages.

###### max

The maximum number of messages to be logged in the specified interval.

###### duration

The time interval in seconds for which the logged messages will be limited.

##### The `[[[[[DEBUG]]]]]` category section

Configuration data for debug level messages.
This can be overriden for specific messages.

###### max

The maximum number of messages to be logged in the specified interval.

###### duration

The time interval in seconds for which the logged messages will be limited.

##### The `[[[[[TRACE]]]]]` category section

Configuration data for trace level messages.
This can be overriden for specific messages.

###### max

The maximum number of messages to be logged in the specified interval.

###### duration

The time interval in seconds for which the logged messages will be limited.

#### The `[[[[messages]]]]` section

Configuration data for specific messages.
Each subsection is a specific message or list of messages.

##### The `[[[[[message-id]]]]] section

###### max

The maximum number of messages to be logged in the specified interval.

###### duration

The time interval in seconds for which the logged messages will be limited.

###### messages

Optional list of messages for which this section is for
If omitted, the section name is used as the message id.

## The `[[weewx]]` section

Used to configure additional observations and units for WeeWX to use.
See, [https://weewx.com/docs/5.0/custom/units/#creating-a-new-unit-group](https://weewx.com/docs/5.0/custom/units/#creating-a-new-unit-group)
This assumes a good knowledge of customizing WeeWX.
An example can be found [here](Customizing-units-and-unit-groups.md).

### The `[[[observations]]]` section

#### observation-name

Used to designate the unit_group the observation belongs to.
For example, `observation-name = unit-group-name`

### The `[[[units]]]` section

#### For each `[[[[unit-name]]]]` section

##### format

The formatting for this unit.

##### group

The unit group this unit belongs to.

##### label

The label for this unit.

##### unit_system

The unit system this unit belongs to.

##### `[[[[[conversion]]]]]` section

###### to-unit-name

The formula to use to convert to this unit.
For example, `to-unit-name = function to convert from unit to to-unit`
