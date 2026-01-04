# multiple topic types

In this example, some topics will have data in the [individual](individual-example.md) format
and some topics will have data in the [json](json-example.md) format.

1. On `topic/temp1`, a temperature is published in the message.
This tempurature is measured in Celsius, but needs to stored as Farenheit.
This value should be stored in the WeeWX field `extraTemp1`.

2. On `topic/outTemp`, a temperature is published in the message.
This temperature is measured in Fahrenheit, the unit of measurement it should be saved as.
This value should be stored in the WeeWX field `outTemp`.

3. On `topic/json`, the following json is published.
This tempurature is measured in Celsius, but needs to stored as Farenheit.
This value should be stored in the WeeWX field `inTemp`.

```
    {
      "inTemp_C": 21
    }
```

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
            # Must be specified here or at the topic level
            #
            # Since two of the tpoics are type 'indivdual', we set to 'indvidual here abd override the type for the 'json' topic.
            # Note, it could be removed from here ans et on each topic.
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
        
        [[[topic/json]]]
            # Set the 'type' for this topic to json.
            [[[[message]]]]
                type = json
            [[[[inTemp_C]]]]
                # The WeeWX name.
                # Default is the name from MQTT.
                name = inTemp

                # The units of the incoming data.
                # Useful if this field's units differ from the topic's unit_system's units.
                # Valid values: see, https://weewx.com/docs/5.0/reference/units/
                # Default is not set
                units = degree_C        
```
