---
title: Additional Options
has_children: true
has_toc: true
nav_order: 3
---

## The `[MQTTSubscribeDriver]/[MQTTSubscribeSection]` section

This configures the MQTT connection and any necessary WeeWX options.

### archive_interval

The WeeWX archive interval.

Note, this really should be retrieved from the WeeWX configuration...

*Experimental*:
    When the `archive_topic` is set and MQTTSubscribe is running in 'hardware generation' mode, this is the WeeWX archive interval.

The default is ‘300’.

### binding

Whether to bind to the `loop` or the `archive`.
This is only used by the service.
The default is `loop`.

### clean_session

The clean_session parameter that is passed into the creation of the MQTT client. The default is `true`.

### clean_start

The clean_start parameter that is passed into the creation of the MQTT client.
Valid values are `true`, `false`, and `MQTT_CLEAN_START_FIRST_ONLY`.
The default is `MQTT_CLEAN_START_FIRST_ONLY`.
This option is only valid with a the `protocol` option set to `MQTTv5`.

### clientid

The client id to use when connecting.
When running as a service, the default is MQTTSubscribeService-xxxx.
When running as a driver, the default is MQTTSubscribeDriver-xxxx.
Where xxxx is a random number between 1000 and 9999.

### log

Set to `true` to turn on MQTT logging. The default is `false`.

### protocol

The MQTT protocol version.
Valid values are `MQTTv31`, `MQTTv311`, and `MQTTv5`.
The default is `MQTTv311`.

### wait_before_retry

When the MQTT queue becomes empty, how long in seconds before checking it. This is only used by the driver. The default is `2`.
