---
title: Individual Example
nav_order: 9
---

In this example there are 3 topics, `topic/id`, `topic/temp1`, and `topic/outTemp`.

1. On `topic/id`, a single value is published in the message.
It is desired to ignore this data.
This is easily accomplished by not configuring this topic.

2. On `topic/temp1`, a temperature is published in the message.
This tempurature is measured in Celsius, but needs to stored as Farenheit.
This value should be stored in the WeeWX field `extraTemp1`.

3. On `topic/outTemp`, a temperature is published in the message.
This temperature is measured in Fahrenheit, the unit of measurement it should be saved as.
This value should be stored in the WeeWX field `outTemp`.

The configuration below accomplishes this.
This example leverages MQTTSubscribe's default values.
To see a more complete template see,
[https://github.com/weewx-mqtt/subscribe/blob/master/mqttsubscribe.example.conf](https://github.com/weewx-mqtt/subscribe/blob/master/mqttsubscribe.example.conf).

[Common options](https://github.com/weewx-mqtt/subscribe/wiki/Common-Options)
is a reference of the most common options.

```
[MQTTSubscribeService or MQTTSubscribeDriver]
    # The driver to use.
    # Only used by the driver.
    driver = user.MQTTSubscribe
    
    # Turn the service on and off.
    # Default is true.
    # Only used by the service.
    enable = true

    # The MQTT server.
    # Default is: localhost
    host = localhost

    # The port to connect to.
    # Default is: 1883
    port = 1883

    [[topics]]
        # Configuration for the message callback.
        [[[message]]]
            # The format of the MQTT payload.
            # Currently support: individual, json, keyword
            # Must be specified.
            type = individual

        [[[topic/temp1]]]
            # The WeeWX name.
            # Default is the name from MQTT.
            name = extraTemp1

            # The units of the incoming data.
            # Useful if this field's units differ from the topic's unit_system's units.
            # Valid values: see, https://weewx.com/docs/5.0/reference/units/
            # Default is not set
            units = degree_C

        [[[topic/outTemp]]]
```
