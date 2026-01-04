---
title: Message Section
parent: Topics Section
ancestor: Common Options
nav_order: 1
---

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
