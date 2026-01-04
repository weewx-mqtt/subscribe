---
title: Configuring pre 1.6.0
parent: Deprecated Documentation
nav_order: 1
---

There are three major pieces to the MQTTSubscribe configuration.

## The `[MQTTSubscribeDriver]/[MQTTSubscribeSection]` section

This configures the MQTT connection and any necessary WeeWX options.

## The `[[topics]]` section

This has the the MQTT topics that are to be subscribed to along with options used to control processing of the messages.
Most of the options control if the message should be ignored due to its timestamp.
See the [Date Time Processing](Date-Time-processing.md) page for a detailed explanation of these.

The `unit_system` is used to set the unit system for messages that do not specify units.

The topics are designated via `[[[topic-name]]]`, with a separate subsection for each topic.

## The `[[message_callback]]` section

This contains the information necessary to parse the MQTT message into a WeeWX name/value dictionary.
Out of the box MQTTSubscribe supports JSON formatted messages, name=value format, or a topic for each individual data element.
Setting `type` to `json`, `keyword`, or `individual` selects the parser to use.

full_topic_fieldname
: Only used when type is ‘individual’.
When True, the full topic (weather/outTemp) is used as the fieldname. When false, the topic furthest to the right is used.

flatten_delimiter
: Only used when type is ‘json’. When the json is nested, the delimiter between the hierarchies.

keyword_delimiter
: Only used when type is ‘keyword’. The delimiter between fieldname and value pairs. (field1=value1, field2=value2).

keyword_separator
: Only used when type is ‘keyword’. The separator between fieldname and value pairs. (field1=value1, field2=value2).

The `[[[fields]]]` subsection is used in place of the `[[[sensor-map]]]` subsection present in other drivers
to configure both the mapping from the field names used by your MQTT publisher to field names used by WeeWX,
and any additional processing required after the data has been parsed into name/value pairs.
Each incoming name that needs additional processing must have a `[[[[fieldname]]]]` subsection, where ‘fieldname’ is the incoming name.

name
: The WeeWX name.

ignore
: Set to 'true' if the field should be ignored.

conversion_type
: The conversion type (bool, float, or int) necessary for WeeWX compatibility.  The default is 'float'.

contains_total
: Set to `true` if the incoming data is cumulative (for example, rain total)

As an example, if a weather station uses JSON format with fields 'model' (which should be ignored) and
'temperature_C' (which should be mapped to outTemp), this section could contain

    [[message_callback]]
        type = json
        [[[fields]]]
            [[[[model]]]]
                ignore = true
            [[[[temperature_C]]]]
                name = outTemp
