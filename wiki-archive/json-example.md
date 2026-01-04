# json examples

## Simple json message

If the following is published to a topic of `first/topic`.

```
{
  "id": 1,
  "temp1": “26.7“
}
```

And the following to a topic of `second/topic`.

```
{
  "outTemp": 80
}
```
  
Then the configuration would look something like this.

```
[MQTTSubscribeService] or [MQTTSubscribeDriver]
    # The MQTT server.
    # Default is: localhost
    host = localhost

    # The port to connect to.
    # Default is: 1883
    port = 1883

    # Maximum period in seconds allowed between communications with the broker.
    # Default is: 60
    keepalive = 60

    # username for broker authentication.
    # Default is: None
    username = None

    # password for broker authentication.
    # Default is: None
    password = None

    [[topics]]
        # Units for MQTT payloads without unit value.
        # Valid values: US, METRIC, METRICWX
        # For more information see, https://weewx.com/docs/5.0/reference/units/?h=units
        # Default is US
        unit_system = US

        # Configuration for the message callback
        [[[message]]]
            # The format of the MQTT payload.
            # Currently support: individual, json, keyword
            # Must be specified.
            type = json

        # The first topic to subscribe to. 
        [[[first/topic]]]
            # The incoming field name from MQTT.
            [[[[temp1]]]]
                # The WeeWX name.
                # Default is the name from MQTT.
                name = extraTemp1

                # True if the incoming data should not be processed into WeeWX.
                # Valid values: True, False
                # Default is False
                ignore = False

                # True if the incoming data is cumulative.
                # Valid values: True, False
                # Default is False
                contains_total = False

                # The conversion type necessary for WeeWX compatibility
                # Valid values: bool, float, int, none
                # Default is float
                conversion_type = float

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

## 'Nested' json message

If the following is published to a topic of `first/topic`.

```
{
  "wind":
  {
    "direction: 89,
    "speed": 3,
    "gustDirection": 90,
    "gust": 5
  }
}
```

Then the configuration would look something like this.

```
[MQTTSubscribeService] or [MQTTSubscribeDriver]
    # The MQTT server.
    # Default is: localhost
    host = localhost

    # The port to connect to.
    # Default is: 1883
    port = 1883

    # Maximum period in seconds allowed between communications with the broker.
    # Default is: 60
    keepalive = 60

    # username for broker authentication.
    # Default is: None
    username = None

    # password for broker authentication.
    # Default is: None
    password = None


    [[topics]]
        # Units for MQTT payloads without unit value.
        # Valid values: US, METRIC, METRICWX
        # For more information see, https://weewx.com/docs/5.0/reference/units/?h=units
        # Default is US
        unit_system = US

        # Configuration for the message callback.
        [[[message]]
            # The format of the MQTT payload.
            # Currently support: individual, json, keyword
            # Must be specified.
            type = json

            # When the json is nested, the delimiter between the hierarchies.
            # Default is _.
        f   latten_delimiter = "_"

        # The first topic to subscribe to. 
        [[[first/topic]]]
            # The incoming field name from MQTT.
            [[[[wind_speed]]]]
                # The WeeWX name.
                # Default is the name from MQTT.
                name = windSpeed

            [[[[wind_direction]]]]
                # The WeeWX name.
                # Default is the name from MQTT.
                name = windDir

            [[[[wind_gust]]]]
                # The WeeWX name.
                # Default is the name from MQTT.
                name = windGust

            [[[[wind_gustDirection]]]]
                # The WeeWX name.
                # Default is the name from MQTT.
                name = windGustDir                           
```

## json message with array

If the following is published to a topic of `first/topic`.

```
{
    'temps': [
        {
            'temp1': 70,
            'temp2': 60,
        },
    ],
}
```

Then the configuration would look something like this.

```
[MQTTSubscribeService] or [MQTTSubscribeDriver]
    # The MQTT server.
    # Default is: localhost
    host = localhost

    # The port to connect to.
    # Default is: 1883
    port = 1883

    # Maximum period in seconds allowed between communications with the broker.
    # Default is: 60
    keepalive = 60

    # username for broker authentication.
    # Default is: None
    username = None

    # password for broker authentication.
    # Default is: None
    password = None

    [[topics]]
        # Units for MQTT payloads without unit value.
        # Valid values: US, METRIC, METRICWX
        # For more information sehttps://weewx.com/docs/5.0/reference/units/?h=units=units
        # Default is US
        unit_system = US

        [[first/topic]]]
            [[[[message]]]]
                # The format of the MQTT payload.
                # Currently support: individual, json, keyword
                # Must be specified.
                type = json

                # When the json is nested, the delimiter between the hierarchies.
                # Default is _.
                flatten_delimiter = "_"

            # The incoming field name from MQTT.
            [[[[temps]]]]
                # 'temps' is actually array. 
                # 'subfields' will provide a name to each element in the array.
                [[[[[subfields]]]]]
                    # There is only one element in the array.
                    #We will name it 'temp'.
                    [[[[[[temp]]]]]]

            # The single element in the array named 'temp' in object.
            # This object has two properties, 'temp1' and 'temp2'.
            # MQTTSubscribe will take the array element name, 'temp' 
            # and concatenate the object properties to it.
            # This will result in two fields named, 'temp_temp1', and 'temp_temp2'.
            # These fields can configured like any other field i the json.
            [[[[temp_temp1]]]]
                # The WeeWX name.
                # Default is the name from MQTT.
                # In thus case it would have been 'temp_temp1'.         
                name = temp1
            [[[[temp_temp2]]]]
                # The WeeWX name.
                # Default is the name from MQTT. 
                # In thus case it would have been 'temp_temp2'.            
                name = temp2                              
'''
