---
title: Topic Name Section
parent: Topics Section
ancestor: Additional Options
nav_order: 99
---

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
