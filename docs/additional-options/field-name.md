---
title: Field Name Section
parent: Topic Name Section
ancestor: Additional Options
nav_order: 1
---

### For each `[[[[Fieldname]]]]`

#### conversion_error_to_none

Controls what to do when an error occurs converting the data to the desired type.
When set to `True`, if there is an exception converting the data type, the value is set to None.
When set to `False` if there is an exception converting the data type, an error is logged and the MQTT msg is skipped.
Valid values are `True` and `False`.
The default is `False`.

#### conversion_func

A Python expression that when evaluated returns a valid value.
Example, `conversion_func = lambda x: True if x == 'ON' else False`
This takes precedence over the `conversion_type` option.
The default is not set.

#### expires_after

Controls the ‘archive record cache’.
The ‘archive record cache’ caches values that may not be published in every archive interval.
This specifies in seconds how long the cache is valid. A value of `0` means the cache is always expired.
This is useful if the missing field should have a value of `None` instead of the previous value’.
Setting `expires_after` to `None` means the cache never expires.
The default is not set

#### filter_out_message_when

When the field has any of the listed values, the MQTT message is not processed.
Any set of values separated by a comma is valid. For example: v1, v2, v3.
The default is empty.
Only used for json payloads.
Note, conversion_type will most likely have to be set.

#### ignore_msg_id_field

When `True`, the value in the field specified in msg_id_field is not appended to the fieldname in the mqtt message. The default is `false`.

#### units

The units for this field.
This is useful if this field's units differ from the topic's unit_system's units.
For valid values see, [https://weewx.com/docs/5.0/reference/units/](https://weewx.com/docs/5.0/reference/units/)
The default is not set.

#### use_server_datetime

When `true`, even if the payload has a dateTime field, ignore it and use the server’s datetime. The default is `false`.

##### `[[[[[subfields]]]]]`

This is only valid when the fieldname is an array.
Each subsection 'names' the element in the array.

###### For each `[[[[SubFieldname]]]`

Each subfield can be configured like a [field]({% link common-options/field-name.md %}) in the json.
