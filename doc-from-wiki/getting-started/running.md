---
title: Running MQTTSubscribe with WeeWX
parent: Getting Started
nav_order: 6
---

## Running MQTTSubscribe with WeeWX

If running as a driver follow [these instructions]($WEECTL station reconfigure --driver=user.MQTTSubscribe --no-prompt)
to set the driver to `MQTTSubscribe`.

If running as a service, follow [these](https://github.com/weewx-mqtt/subscribe#if-running-as-a-service-enable-it) to enable it.

Then update WeeWX's configuration via [these instructions](https://github.com/weewx-mqtt/subscribe#update-weewx-with-mqttsubscribes-configuration).
