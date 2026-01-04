---
title: Topics Section
parent: Additional Options
nav_order: 2
---
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
