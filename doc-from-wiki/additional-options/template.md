---
title: foo
parent: Additional Options
nav_order: 99
---
# Configuring additional options

## The `[MQTTSubscribeDriver]/[MQTTSubscribeSection]` section

This configures the MQTT connection and any necessary WeeWX options.

### archive_interval

The WeeWX archive interval.

Note, this really should be retrieved from the WeeWX configuration...

*Experimental*:
    When the `archive_topic` is set and MQTTSubscribe is running in 'hardware generation' mode, this is the WeeWX archive interval.

The default is ‘300’.

### binding

Whether to bind to the `loop` or the `archive`.
This is only used by the service.
The default is `loop`.

### clean_session

The clean_session parameter that is passed into the creation of the MQTT client. The default is `true`.

### clean_start

The clean_start parameter that is passed into the creation of the MQTT client.
Valid values are `true`, `false`, and `MQTT_CLEAN_START_FIRST_ONLY`.
The default is `MQTT_CLEAN_START_FIRST_ONLY`.
This option is only valid with a the `protocol` option set to `MQTTv5`.

### clientid

The client id to use when connecting.
When running as a service, the default is MQTTSubscribeService-xxxx.
When running as a driver, the default is MQTTSubscribeDriver-xxxx.
Where xxxx is a random number between 1000 and 9999.

### log

Set to `true` to turn on MQTT logging. The default is `false`.

### protocol

The MQTT protocol version.
Valid values are `MQTTv31`, `MQTTv311`, and `MQTTv5`.
The default is `MQTTv311`.

### wait_before_retry

When the MQTT queue becomes empty, how long in seconds before checking it. This is only used by the driver. The default is `2`.

## The `[[tls]]` section

The TLS options that are passed to tls_set method of the MQTT client. For additional information see, [https://eclipse.org/paho/clients/python/docs/strptime-format-codes](https://eclipse.org/paho/clients/python/docs/strptime-format-codes)

### ca_certs

Path to the Certificate Authority certificate files that are to be treated as trusted by this client.

### certfile

The PEM encoded client certificate and private keys. The default is `None`.

### certs_required

The certificate requirements that the client imposes on the broker. Valid values are, `none`, `optional`, `required`. The default is `required`

### ciphers

The encryption ciphers that are allowable for this connection. Specify `None` to use the defaults. The default is `None`.

### keyfile

The private keys. The default is `None`.

### tls_version

The version of the SSL/TLS protocol to be used. Valid values are,`sslv2`, `sslv23`, `sslv3`, `tls`, `tlsv1`, `tlsv11`, `tlsv12`. The default is `tlsv12`.

## The `[[topics]]` section

This has the the MQTT topics that are to be subscribed to along with options used to control processing of the

### callback_config_name

The name of the MQTT on_message callback configuration section.
This should only be changed if a topic named ‘message’ is being subscribed to.
Default is 'message'.

### datetime_format

The formatting string for converting a timestamp to an epoch datetime.
For additional information see, [https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)
The default is `None`.

### max_queue

The maximum queue size.
When the queue is larger than this value, the oldest element is removed.
In general the queue should not grow large, but it might if the time between the driver creating packets is large and the MQTT broker publishes frequently.
Or if subscribing to 'individual' payloads with wildcards.
This results in many topic in a single queue.
The default is sys.maxsize for python 3 and sys.maxint for python 2.

### offset_format

The formatting string for converting the time offset when converting a timestamp to an epoch datetime.
Example values are, `-hhmm`, `+hhmm`, and `hh:mm`.
The default is `None`.

### qos

The QOS level to subscribe to. The default is `0`.

### subscribe

Controls if an actual subscription request is made to the broker for this topic.
The default is `True`.

### use_server_datetime

When `true`, even if the payload has a dateTime field, ignore it and use the server’s datetime. The default is `false`.

### For each `[[[topic]]]`

### callback_config_name

The name of the MQTT on_message callback configuration section.
This should only be changed if a topic named ‘message’ is being subscribed to.
Overrides the value set for all [[topics]].

#### msg_id_field

Specifies a field name In the MQTT message whose value is appended to every field name in the message.
This enables same formatted messages to map to different WeeWX fields.
The default is `None`.
This option is only used with json payloads.

So if the different messages looked like this,

```
{
  "time":"2020-06-19 11:28:10",
  "model":"Prologue-TH",
  "subtype":9,
  "id":73,
  "channel":1,
  "battery_ok":0,
  "temperature_C":25.300,
  "button":0,
  "humidity":68
}

{
  "time":"2020-06-19 11:28:17",
  "model":"Prologue-TH",
  "subtype":9,
  "id":42,
  "channel":3,
  "battery_ok":0,
  "temperature_C":26.900,
  "button":0,
  "humidity":63
}

{
  "time":"2020-06-19 11:28:44",
  "model":"Prologue-TH",
  "subtype":9,
  "id":207,
  "channel":2,
  "battery_ok":0,
  "temperature_C":29.700,
  "button":0,
  "humidity":57
}
```

Then the configuration would look like this:

```

[[Topics]]
  [[[topic name]]]
  msg_id_field = id
  [[[[temperature_C_73]]]]
    name = extraTemp1
  [[[[temperature_C_42]]]]
    name = extraTemp2
  [[[[temperature_C_207]]]]
    name = extraTemp3
  [[[[time_73]]]]
    name = time_stamp
  [[[[time_42]]]]
    name = time_stamp
  [[[[time_207]]]]
    name = time_stamp
```

#### subscribe

Controls if an actual subscription request is made to the broker for this topic.
The default is `True`.

### For each `[[[[Fieldname]]]`

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

### use_server_datetime

When `true`, even if the payload has a dateTime field, ignore it and use the server’s datetime. The default is `false`.

#### `[[[[[subfields]]]]]`

This is only valid when the fieldname is an array.
Each subsection 'names' the element in the array.

##### For each `[[[[SubFieldname]]]`

Each subfield can be configured like a [field](https://github.com/weewx-mqtt/subscribe/wiki/Configuring#the-field-name-sections) in the json.
