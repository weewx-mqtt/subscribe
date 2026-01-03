---
title: Additional Options
has_children: true
has_toc: true
nav_order: 3
---
## The `[MQTTSubscribeDriver]/[MQTTSubscribeSection]` section

This configures the MQTT connection and any necessary WeeWX options.

### enable

Set to `false` to disable the service. This is only used by the service. The default is `true`.

### host

The MQTT server. The default is `localhost`.

### keepalive

Maximum period in seconds allowed between communications with the broker. The default is `60`.

### max_delay

**Coming soon.**
The maximum time in seconds that the client will wait before trying to reconnect.
The default is 120.

### min_delay

**Coming soon.**
The minimum time in seconds that the client will wait before trying to reconnect.
The default is 1.

### password

password for broker authentication. The default is `None`.

### port

The port to connect to. The default  is `1883`.

### stop_on_validation_errors

Controls if validation errors raise an exception (stopping WeeWX from starting) or only logged.
Default is `false`.

### username

username for broker authentication. The default is `None`.
