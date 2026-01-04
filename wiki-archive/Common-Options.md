<!-- markdownlint-disable no-duplicate-heading  -->
# Introduction to configuring MQTTSubscribe

There are three major pieces to the MQTTSubscribe configuration.

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

## The `[[topics]]` section

This has the the MQTT topics that are to be subscribed to along with options used to control processing of the messages.
Most of the options control if the message should be ignored due to its timestamp.
See the [Date Time Processing](Date-Time-processing.md) page for a detailed explanation of these.

### ignore

Set to `true` if the field should be ignored. The default is `false`.

### unit_system

used to set the unit system. The default is `US`.

### `[[[message]]]`

This contains the information necessary to parse the MQTT message into a WeeWX name/value dictionary.
Out of the box MQTTSubscribe supports JSON formatted messages, name=value format, or a topic for each individual data element.

#### flatten_delimiter

Only used when type is `json`. When the json is nested, the delimiter between the hierarchies. The default is `_`.

#### keyword_delimiter

Only used when type is `keyword`. The delimiter between fieldname and value pairs. (field1=value1, field2=value2). The default is `=`.

#### keyword_separator

Only used when type is `keyword`. The separator between fieldname and value pairs. (field1=value1, field2=value2). The default is `,`.

#### type

Selects the parser to use. valid values are, `json`, `keyword`, or `individual`.

### The `[[[topic-name]]]` sections

Each topic to subscribe to has its own section that is the name of the topic to subscribe to.

#### ignore

Set to `true` if the field should be ignored. The default is `false`.

### The `[[[[message]]]]` sections

Overrides the [`[[topics]] [[[message]]]`](https://github.com/weewx-mqtt/subscribe/wiki/Common-Options#message) settings for this specific topic.

### The `[[[[field-name]]]]` sections

Under each `[[[topic-name]]]` any fields that need configuring are designated via a `[[[[field-name]]]]` section.
This information maybe in a `sensor-map`, `label-map`, etc. in other drivers or services.

Some common configuration options for a field are:

#### contains_total

Set to `true` if the incoming data is cumulative value (for example, rain total) and the WeeWX field expects an increment value.. The default is `false`.

#### conversion_type

The conversion type (bool, float, or int) necessary for WeeWX compatibility.  The default is `float`.

#### ignore

Set to `true` if the field should be ignored. The default is `false`.

#### name

The WeeWX name.

#### total_wrap_around

To be used in conjunction with `contains_total`.

Set to `true` if the incoming cumulative value can wrap around (yearly rain for example). The default is `false`.

## Additional information

- Information on configuring the less common options can be found [here](https://github.com/weewx-mqtt/subscribe/wiki/Configuring-additional-options).
- Complete examples for [json](https://github.com/weewx-mqtt/subscribe/wiki/json-example),
[keyword](https://github.com/weewx-mqtt/subscribe/wiki/keyword-example),
and [individual](https://github.com/weewx-mqtt/subscribe/wiki/individual-example) payloads.
- An in depth explaination of date/time 'filtering' is [here](https://github.com/weewx-mqtt/subscribe/wiki/Date-Time-processing).
