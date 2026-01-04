---
title: Keyword Example 
nav_order: 11
---

In this example there are 2 topics, `first/topic` and `second/topic`.

1. On `first/topic` the message consists of two keyword/value pairs, `id` and `temp1`.
The `id` value should be ignored.
The `temp1` value should be converted from Celsius to Farenheit and stored in WeeWX field, `extraTemp1`.
The message would look something like this.

    ```
    id=1,temp1=26.7
    ```

2. On `second/topic` the message consists of a single keyword/value, `outTemp`.
The `outTemp` value does not need to be converted and should be stored in WeeWX field, `outTemp`.
The message would look something like this.

    ```
        {
        outTemp=80
        }
    ```
  
The configuration below accomplishes this.
This example leverages MQTTSubscribe's default values.
To see a more complete template see,
[https://github.com/weewx-mqtt/subscribe/blob/master/mqttsubscribe.example.conf](https://github.com/weewx-mqtt/subscribe/blob/master/mqttsubscribe.example.conf).

[Common options]({{site.baseurl}}/common-options)
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
            type = keyword

        # The first topic to subscribe to.
        [[[first/topic]]]
            # The incoming field name from MQTT.
            [[[[temp1]]]]
                # The WeeWX name.
                # Default is the name from MQTT.
                name = extraTemp1

                # The units of the incoming data.
                # Useful if this field's units differ from the topic's unit_system's units.
                # Valid values: see, https://weewx.com/docs/5.0/reference/units/
                # Default is not set
                units = degree_C
        
            [[[[id]]]]
                # True if the incoming data should not be processed into WeeWX.
                # Valid values: True, False
                # Default is False
                ignore = True

        # The second topic to subscribe to
        [[[second/topic]]]
```
