---
title: Date/Time Processing
nav_order: 4
---

## Ignoring date/time in MQTT message

If the date/time in the MQTT payload is unreliable, it can ignored by setting `use_server_datetime` to true.
When set to true, as the MQTT data is added to the queue its dateTime element is set to the current time.

## MQTTSubscribeService processing

The MQTTSubscribeService assumes that the data arrives via in 'close to' chronological order and
attempts to ensure that the data belongs to the packet/record that is augmenting.
It does this by ignoring queue data that is before a calculated start time and not pulling data from the queue that is after the end time.
For loop packet binding, the start time is the time of the previous packet.
For archive record binding, the start time is the current record's time minus the current record's interval.
For both the packet and record, the end time is the time in the current packet or record respectively.

Due to things such as clock skew, network lag, compute time, etc., this date/time checking is very often too restrictive.
Both the start time and end time can be adjusted via `adjust_start_time` and `adjust_end_time` respectively.
The value of adjust_start_time is used to decrease the start time that many seconds.
And the end time is increased by adjust_end_time seconds.
This increases the window of time that is considered valid. Effectively allowing MQTT data that has earlier or later time to be added to the packet/record.

If increasing the time window is not enough,
the start date/time processing can be ignored by setting `ignore_start_time` to true and
the end date/time processing can be ignored by setting `ignore_end_time` to true.
When ignore_start_time is true, the start time is set to the first queue element's time in the queue.
When ignore_end_time is true, the end time is set to the last queue element's time.

All of these options are in the `[[topics]]` section. For example,

```
    [[topics]
        # Even if the payload has a datetime, ignore it and use the server datetime.
        # Default is False.
        use_server_datetime = True

        # When True, the MQTT datetime will be not be checked that is greater than the last packet processed.
        # Default is False.
        # Only used by the service.
        ignore_start_time = True

        # When the True, the MQTT data will continue to be processed even if its datetime is greater than the packet's datetime.
        # Default is False.
        # Only used by the service.
        ignore_end_time = True

        # Allow MQTT data with a datetime this many seconds prior to the previous packet's datetime.
        # to be added to the current packet.
        # Default is 0.
        # Only used by the service.
        adjust_start_time = 1

        # Allow MQTT data with a datetime this many seconds after the current packet's datetime.
        # to be added to the current packet.
        # Default is 0.
        # Only used by the service.
        adjust_end_time = 1
        
        # The first topic to subscribe to
        [[[first/topic]]]
```
