---
title: Understanding the log
nav_order: 16
---

There are four main sections of the log; `Initialization`, `MQTT Initialization`, and `Processing`.
This example uses the log from MQTTSubscribeDriver, MQTTSubscribeService would be very similar.

## Initialization

### Important information about the environment

This logs basic information like versions of software, the MQTTSubscribe configuration, etc.

```
weewxd[1674906] INFO weewx.engine: Loading station type MQTTSubscribeDriver (user.MQTTSubscribe)
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) Using weewx version 5.0.1
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) Using Python 3.10.13 (main, Oct 23 2023, 11:48:50) [GCC 11.4.0]
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) Platform Linux-5.15.0-92-generic-x86_64-with-glibc2.35
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) Locale is 'en_US.UTF-8'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) Record Augmentation is: None
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) Record Generation is: hardware
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Version is 3.0.0-rc06a
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Log level: 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Log debug setting: 1
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Log console: False
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Log file: None
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Max loop interval is: 0
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) sanitized configuration removed ['password']
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) MQTTSUBscriber sanitized_service_dict is {'driver': 'user.MQTTSubscribe', 'host': 'weather-data.local', 'topics': {'message': {'type': 'individual'}, 'weather/individual/altimeter_inHg': {'name': 'altimeter'}, 'weather/individual/outHumidity': {}, 'weather/individual/barometer_inHg': {'name': 'barometer'}, 'weather/individual/windchill_F': {'name': 'windchill'}, 'weather/individual/dewpoint_F': {'name': 'dewpoint'}, 'weather/individual/rain_in': {'name': 'rain'}, 'weather/individual/pressure_inHg': {'name': 'pressure'}, 'weather/individual/appTemp_F': {'name': 'appTemp_F'}, 'weather/individual/UV': {}, 'weather/individual/outTemp_F': {'name': 'outTemp'}, 'weather/individual/cloudbase_foot': {'name': 'cloudbase_foot'}}}
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) message_callback_provider_name is user.MQTTSubscribe.MessageCallbackProvider
```

### MQTT parameters

This is information used to configure the MQTT connection.

```
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) clientid is MQTTSubscribe-7343
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) client_session is True
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) host is weather-data.local
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) port is 1883
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) keepalive is 60
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) username is None
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) min_delay is 1
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) max_delay is 120
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) password is not set
```

### Final `Topic` configuration

This is the configuration information in the format used by MQTTSubscribe.

```
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager self.collect_wind_across_loops is True
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager self.collect_observations is False
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager single_queue is False
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager single_queue is False
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager self.subscribed_topics is {"weather/individual/altimeter_inHg": {"ignore": false, "subscribe": true, "conversion_func": {"source": "lambda x: to_float(x)", "compiled": "<function <lambda> at 0x7fee6ae7c1f0>"}, "unit_system": 1, "msg_id_field": null, "qos": 0, "topic_tail_is_fieldname": false, "use_server_datetime": false, "datetime_format": null, "offset_format": null, "fields_ignoring_msg_id": [], "fields": {"weather/individual/altimeter_inHg": {"name": "altimeter", "ignore": false, "contains_total": false, "total_wrap_around": false, "conversion_func": {"source": "lambda x: to_float(x)", "compiled": "<function <lambda> at 0x7fee6ae7c160>"}, "conversion_type": "float", "conversion_error_to_none": false}}, "queue": {"name": "weather/individual/altimeter_inHg", "type": "normal", "ignore_start_time": false, "ignore_end_time": false, "adjust_start_time": 0.0, "adjust_end_time": 0.0, "max_size": 9223372036854775807, "data": "deque([])"}, "filters": {}, "message-1707417517.298291": {"type": "individual"}}, "weather/individual/outHumidity": {"ignore": false, "subscribe": true, "conversion_func": {"source": "lambda x: to_float(x)", "compiled": "<function <lambda> at 0x7fee6ae7c310>"}, "unit_system": 1, "msg_id_field": null, "qos": 0, "topic_tail_is_fieldname": false, "use_server_datetime": false, "datetime_format": null, "offset_format": null, "fields_ignoring_msg_id": [], "fields": {}, "queue": {"name": "weather/individual/outHumidity", "type": "normal", "ignore_start_time": false, "ignore_end_time": false, "adjust_start_time": 0.0, "adjust_end_time": 0.0, "max_size": 9223372036854775807, "data": "deque([])"}, "filters": {}, "message-1707417517.298291": {"type": "individual"}}, "weather/individual/barometer_inHg": {"ignore": false, "subscribe": true, "conversion_func": {"source": "lambda x: to_float(x)", "compiled": "<function <lambda> at 0x7fee6ae7c3a0>"}, "unit_system": 1, "msg_id_field": null, "qos": 0, "topic_tail_is_fieldname": false, "use_server_datetime": false, "datetime_format": null, "offset_format": null, "fields_ignoring_msg_id": [], "fields": {"weather/individual/barometer_inHg": {"name": "barometer", "ignore": false, "contains_total": false, "total_wrap_around": false, "conversion_func": {"source": "lambda x: to_float(x)", "compiled": "<function <lambda> at 0x7fee6ae7c430>"}, "conversion_type": "float", "conversion_error_to_none": false}}, "queue": {"name": "weather/individual/barometer_inHg", "type": "normal", "ignore_start_time": false, "ignore_end_time": false, "adjust_start_time": 0.0, "adjust_end_time": 0.0, "max_size": 9223372036854775807, "data": "deque([])"}, "filters": {}, "message-1707417517.298291": {"type": "individual"}}, "weather/individual/windchill_F": {"ignore": false, "subscribe": true, "conversion_func": {"source": "lambda x: to_float(x)", "compiled": "<function <lambda> at 0x7fee6ae7c4c0>"}, "unit_system": 1, "msg_id_field": null, "qos": 0, "topic_tail_is_fieldname": false, "use_server_datetime": false, "datetime_format": null, "offset_format": null, "fields_ignoring_msg_id": [], "fields": {"weather/individual/windchill_F": {"name": "windchill", "ignore": false, "contains_total": false, "total_wrap_around": false, "conversion_func": {"source": "lambda x: to_float(x)", "compiled": "<function <lambda> at 0x7fee6ae7c550>"}, "conversion_type": "float", "conversion_error_to_none": false}}, "queue": {"name": "weather/individual/windchill_F", "type": "normal", "ignore_start_time": false, "ignore_end_time": false, "adjust_start_time": 0.0, "adjust_end_time": 0.0, "max_size": 9223372036854775807, "data": "deque([])"}, "filters": {}, "message-1707417517.298291": {"type": "individual"}}, "weather/individual/dewpoint_F": {"ignore": false, "subscribe": true, "conversion_func": {"source": "lambda x: to_float(x)", "compiled": "<function <lambda> at 0x7fee6ae7c5e0>"}, "unit_system": 1, "msg_id_field": null, "qos": 0, "topic_tail_is_fieldname": false, "use_server_datetime": false, "datetime_format": null, "offset_format": null, "fields_ignoring_msg_id": [], "fields": {"weather/individual/dewpoint_F": {"name": "dewpoint", "ignore": false, "contains_total": false, "total_wrap_around": false, "conversion_func": {"source": "lambda x: to_float(x)", "compiled": "<function <lambda> at 0x7fee6ae7c670>"}, "conversion_type": "float", "conversion_error_to_none": false}}, "queue": {"name": "weather/individual/dewpoint_F", "type": "normal", "ignore_start_time": false, "ignore_end_time": false, "adjust_start_time": 0.0, "adjust_end_time": 0.0, "max_size": 9223372036854775807, "data": "deque([])"}, "filters": {}, "message-1707417517.298291": {"type": "individual"}}, "weather/individual/rain_in": {"ignore": false, "subscribe": true, "conversion_func": {"source": "lambda x: to_float(x)", "compiled": "<function <lambda> at 0x7fee6ae7c700>"}, "unit_system": 1, "msg_id_field": null, "qos": 0, "topic_tail_is_fieldname": false, "use_server_datetime": false, "datetime_format": null, "offset_format": null, "fields_ignoring_msg_id": [], "fields": {"weather/individual/rain_in": {"name": "rain", "ignore": false, "contains_total": false, "total_wrap_around": false, "conversion_func": {"source": "lambda x: to_float(x)", "compiled": "<function <lambda> at 0x7fee6ae7c790>"}, "conversion_type": "float", "conversion_error_to_none": false}}, "queue": {"name": "weather/individual/rain_in", "type": "normal", "ignore_start_time": false, "ignore_end_time": false, "adjust_start_time": 0.0, "adjust_end_time": 0.0, "max_size": 9223372036854775807, "data": "deque([])"}, "filters": {}, "message-1707417517.298291": {"type": "individual"}}, "weather/individual/pressure_inHg": {"ignore": false, "subscribe": true, "conversion_func": {"source": "lambda x: to_float(x)", "compiled": "<function <lambda> at 0x7fee6ae7c820>"}, "unit_system": 1, "msg_id_field": null, "qos": 0, "topic_tail_is_fieldname": false, "use_server_datetime": false, "datetime_format": null, "offset_format": null, "fields_ignoring_msg_id": [], "fields": {"weather/individual/pressure_inHg": {"name": "pressure", "ignore": false, "contains_total": false, "total_wrap_around": false, "conversion_func": {"source": "lambda x: to_float(x)", "compiled": "<function <lambda> at 0x7fee6ae7c8b0>"}, "conversion_type": "float", "conversion_error_to_none": false}}, "queue": {"name": "weather/individual/pressure_inHg", "type": "normal", "ignore_start_time": false, "ignore_end_time": false, "adjust_start_time": 0.0, "adjust_end_time": 0.0, "max_size": 9223372036854775807, "data": "deque([])"}, "filters": {}, "message-1707417517.298291": {"type": "individual"}}, "weather/individual/appTemp_F": {"ignore": false, "subscribe": true, "conversion_func": {"source": "lambda x: to_float(x)", "compiled": "<function <lambda> at 0x7fee6ae7c940>"}, "unit_system": 1, "msg_id_field": null, "qos": 0, "topic_tail_is_fieldname": false, "use_server_datetime": false, "datetime_format": null, "offset_format": null, "fields_ignoring_msg_id": [], "fields": {"weather/individual/appTemp_F": {"name": "appTemp_F", "ignore": false, "contains_total": false, "total_wrap_around": false, "conversion_func": {"source": "lambda x: to_float(x)", "compiled": "<function <lambda> at 0x7fee6ae7c9d0>"}, "conversion_type": "float", "conversion_error_to_none": false}}, "queue": {"name": "weather/individual/appTemp_F", "type": "normal", "ignore_start_time": false, "ignore_end_time": false, "adjust_start_time": 0.0, "adjust_end_time": 0.0, "max_size": 9223372036854775807, "data": "deque([])"}, "filters": {}, "message-1707417517.298291": {"type": "individual"}}, "weather/individual/UV": {"ignore": false, "subscribe": true, "conversion_func": {"source": "lambda x: to_float(x)", "compiled": "<function <lambda> at 0x7fee6ae7ca60>"}, "unit_system": 1, "msg_id_field": null, "qos": 0, "topic_tail_is_fieldname": false, "use_server_datetime": false, "datetime_format": null, "offset_format": null, "fields_ignoring_msg_id": [], "fields": {}, "queue": {"name": "weather/individual/UV", "type": "normal", "ignore_start_ti
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager self.cached_fields is {}
```

## MQTT Initialization

This is the information related to establishing the MQTT connection.

```
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Wait before retry is 2
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) Starting loop
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Waiting for MQTT connection.
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Connected with result code 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Connected flags {'session present': 0}
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribing to weather/individual/altimeter_inHg has a mid 1 and rc 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribing to weather/individual/outHumidity has a mid 2 and rc 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribing to weather/individual/barometer_inHg has a mid 3 and rc 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribing to weather/individual/windchill_F has a mid 4 and rc 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribing to weather/individual/dewpoint_F has a mid 5 and rc 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribing to weather/individual/rain_in has a mid 6 and rc 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribing to weather/individual/pressure_inHg has a mid 7 and rc 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribing to weather/individual/appTemp_F has a mid 8 and rc 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribing to weather/individual/UV has a mid 9 and rc 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribing to weather/individual/outTemp_F has a mid 10 and rc 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribing to weather/individual/cloudbase_foot has a mid 11 and rc 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribed to mid: 1 is size 1 has a QOS of 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribed to mid: 2 is size 1 has a QOS of 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribed to mid: 3 is size 1 has a QOS of 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribed to mid: 4 is size 1 has a QOS of 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribed to mid: 5 is size 1 has a QOS of 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribed to mid: 6 is size 1 has a QOS of 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribed to mid: 7 is size 1 has a QOS of 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribed to mid: 8 is size 1 has a QOS of 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribed to mid: 9 is size 1 has a QOS of 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribed to mid: 10 is size 1 has a QOS of 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) Subscribed to mid: 11 is size 1 has a QOS of 0
weewxd[1674906] INFO user.MQTTSubscribe: (Driver) MQTT initialization complete.
```

## MQTTSubscribeDriver secondary thread processing

The line with the prefix `MessageCallbackProvider data-> incoming` is the 'raw' topic, qos, reatain value, and message received from MQTT.
The line with the prefix `TopicManager data-> incoming` is the data as it is being placed on a queue to be processed in the primary thread.
If necessary, the field has been renamed, converted to the appropriate units, etc.

```
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) MessageCallbackProvider data-> incoming topic: weather/individual/barometer_inHg, QOS: 0, retain: 0, payload: b'29.683'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> incoming weather/individual/barometer_inHg: 'barometer': '29.683'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) MessageCallbackProvider data-> incoming topic: weather/individual/outTemp_F, QOS: 0, retain: 0, payload: b'48.7'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> incoming weather/individual/outTemp_F: 'outTemp': '48.7'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) MessageCallbackProvider data-> incoming topic: weather/individual/outHumidity, QOS: 0, retain: 0, payload: b'44.0'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> incoming weather/individual/outHumidity: 'weather/individual/outHumidity': '44.0'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) MessageCallbackProvider data-> incoming topic: weather/individual/UV, QOS: 0, retain: 0, payload: b'1.3'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> incoming weather/individual/UV: 'weather/individual/UV': '1.3'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) MessageCallbackProvider data-> incoming topic: weather/individual/rain_in, QOS: 0, retain: 0, payload: b'0.0'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> incoming weather/individual/rain_in: 'rain': '0.0'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) MessageCallbackProvider data-> incoming topic: weather/individual/pressure_inHg, QOS: 0, retain: 0, payload: b'29.143693561183845'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> incoming weather/individual/pressure_inHg: 'pressure': '29.143693561183845'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) MessageCallbackProvider data-> incoming topic: weather/individual/altimeter_inHg, QOS: 0, retain: 0, payload: b'29.66874642756049'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> incoming weather/individual/altimeter_inHg: 'altimeter': '29.66874642756049'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) MessageCallbackProvider data-> incoming topic: weather/individual/appTemp_F, QOS: 0, retain: 0, payload: b'44.55262895088905'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> incoming weather/individual/appTemp_F: 'appTemp_F': '44.55262895088905'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) MessageCallbackProvider data-> incoming topic: weather/individual/cloudbase_foot, QOS: 0, retain: 0, payload: b'5245.635859637581'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> incoming weather/individual/cloudbase_foot: 'cloudbase_foot': '5245.635859637581'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) MessageCallbackProvider data-> incoming topic: weather/individual/dewpoint_F, QOS: 0, retain: 0, payload: b'27.775202217594643'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> incoming weather/individual/dewpoint_F: 'dewpoint': '27.775202217594643'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) MessageCallbackProvider data-> incoming topic: weather/individual/windchill_F, QOS: 0, retain: 0, payload: b'48.7'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> incoming weather/individual/windchill_F: 'windchill': '48.7'
```

## MQTTSubscribeDriver primary thread processing

The line with the prefix `TopicManager data->` is the data as its pulled of the queue to be processed.
The line with the prefix `data-> final loop packet is` is the loop packet that is returned to WeeWX to be processed.

```
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> outgoing weather/individual/altimeter_inHg: 'altimeter': '29.66874642756049', 'dateTime': '1707417518.4922678', 'usUnits': '1'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) data-> final loop packet is weather/individual/altimeter_inHg 2024-02-08 13:38:38 EST (1707417518): 'altimeter': '29.66874642756049', 'dateTime': '1707417518.4922678', 'usUnits': '1'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> outgoing weather/individual/outHumidity: 'dateTime': '1707417518.4641457', 'usUnits': '1', 'weather/individual/outHumidity': '44.0'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) data-> final loop packet is weather/individual/outHumidity 2024-02-08 13:38:38 EST (1707417518): 'dateTime': '1707417518.4641457', 'usUnits': '1', 'weather/individual/outHumidity': '44.0'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> outgoing weather/individual/barometer_inHg: 'barometer': '29.683', 'dateTime': '1707417518.4570503', 'usUnits': '1'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) data-> final loop packet is weather/individual/barometer_inHg 2024-02-08 13:38:38 EST (1707417518): 'barometer': '29.683', 'dateTime': '1707417518.4570503', 'usUnits': '1'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> outgoing weather/individual/windchill_F: 'dateTime': '1707417518.5002737', 'usUnits': '1', 'windchill': '48.7'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) data-> final loop packet is weather/individual/windchill_F 2024-02-08 13:38:38 EST (1707417518): 'dateTime': '1707417518.5002737', 'usUnits': '1', 'windchill': '48.7'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> outgoing weather/individual/dewpoint_F: 'dateTime': '1707417518.4973853', 'dewpoint': '27.775202217594643', 'usUnits': '1'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) data-> final loop packet is weather/individual/dewpoint_F 2024-02-08 13:38:38 EST (1707417518): 'dateTime': '1707417518.4973853', 'dewpoint': '27.775202217594643', 'usUnits': '1'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> outgoing weather/individual/rain_in: 'dateTime': '1707417518.4879045', 'rain': '0.0', 'usUnits': '1'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) data-> final loop packet is weather/individual/rain_in 2024-02-08 13:38:38 EST (1707417518): 'dateTime': '1707417518.4879045', 'rain': '0.0', 'usUnits': '1'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> outgoing weather/individual/pressure_inHg: 'dateTime': '1707417518.490155', 'pressure': '29.143693561183845', 'usUnits': '1'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) data-> final loop packet is weather/individual/pressure_inHg 2024-02-08 13:38:38 EST (1707417518): 'dateTime': '1707417518.490155', 'pressure': '29.143693561183845', 'usUnits': '1'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> outgoing weather/individual/appTemp_F: 'appTemp_F': '44.55262895088905', 'dateTime': '1707417518.4928248', 'usUnits': '1'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) data-> final loop packet is weather/individual/appTemp_F 2024-02-08 13:38:38 EST (1707417518): 'appTemp_F': '44.55262895088905', 'dateTime': '1707417518.4928248', 'usUnits': '1'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> outgoing weather/individual/UV: 'dateTime': '1707417518.4684663', 'usUnits': '1', 'weather/individual/UV': '1.3'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) data-> final loop packet is weather/individual/UV 2024-02-08 13:38:38 EST (1707417518): 'dateTime': '1707417518.4684663', 'usUnits': '1', 'weather/individual/UV': '1.3'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> outgoing weather/individual/outTemp_F: 'dateTime': '1707417518.459993', 'outTemp': '48.7', 'usUnits': '1'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) data-> final loop packet is weather/individual/outTemp_F 2024-02-08 13:38:38 EST (1707417518): 'dateTime': '1707417518.459993', 'outTemp': '48.7', 'usUnits': '1'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) TopicManager data-> outgoing weather/individual/cloudbase_foot: 'cloudbase_foot': '5245.635859637581', 'dateTime': '1707417518.4969788', 'usUnits': '1'
weewxd[1674906] DEBUG user.MQTTSubscribe: (Driver) data-> final loop packet is weather/individual/cloudbase_foot 2024-02-08 13:38:38 EST (1707417518): 'cloudbase_foot': '5245.635859637581', 'dateTime': '1707417518.4969788', 'usUnits': '1'
```

## MQTTSubscribeService secondary thread processing

The line with the prefix `MessageCallbackProvider data-> incoming` is the 'raw' topic, qos, reatain value, and message received from MQTT.
The line with the prefix `TopicManager data-> incoming` is the data as it is being placed on a queue to be processed in the primary thread.
If necessary, the field has been renamed, converted to the appropriate units, etc.

```
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) MessageCallbackProvider data-> incoming topic: weather/individual/barometer_inHg, QOS: 0, retain: 0, payload: b'29.412'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> incoming weather/individual/barometer_inHg: 'barometer': '29.412'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) MessageCallbackProvider data-> incoming topic: weather/individual/outTemp_F, QOS: 0, retain: 0, payload: b'22.1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> incoming weather/individual/outTemp_F: 'outTemp': '22.1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) MessageCallbackProvider data-> incoming topic: weather/individual/outHumidity, QOS: 0, retain: 0, payload: b'59.0'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> incoming weather/individual/outHumidity: 'weather/individual/outHumidity': '59.0'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) MessageCallbackProvider data-> incoming topic: weather/individual/UV, QOS: 0, retain: 0, payload: b'0.0'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> incoming weather/individual/UV: 'weather/individual/UV': '0.0'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) MessageCallbackProvider data-> incoming topic: weather/individual/rain_in, QOS: 0, retain: 0, payload: b'0.0'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> incoming weather/individual/rain_in: 'rain': '0.0'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) MessageCallbackProvider data-> incoming topic: weather/individual/pressure_inHg, QOS: 0, retain: 0, payload: b'28.85611449159812'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> incoming weather/individual/pressure_inHg: 'pressure': '28.85611449159812'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) MessageCallbackProvider data-> incoming topic: weather/individual/altimeter_inHg, QOS: 0, retain: 0, payload: b'29.376962790687124'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> incoming weather/individual/altimeter_inHg: 'altimeter': '29.376962790687124'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) MessageCallbackProvider data-> incoming topic: weather/individual/appTemp_F, QOS: 0, retain: 0, payload: b'16.321245990614706'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> incoming weather/individual/appTemp_F: 'appTemp_F': '16.321245990614706'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) MessageCallbackProvider data-> incoming topic: weather/individual/cloudbase_foot, QOS: 0, retain: 0, payload: b'3242.850257526233'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> incoming weather/individual/cloudbase_foot: 'cloudbase': '3242.850257526233'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) MessageCallbackProvider data-> incoming topic: weather/individual/dewpoint_F, QOS: 0, retain: 0, payload: b'9.987458866884577'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> incoming weather/individual/dewpoint_F: 'dewpoint': '9.987458866884577'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) MessageCallbackProvider data-> incoming topic: weather/individual/windchill_F, QOS: 0, retain: 0, payload: b'22.1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> incoming weather/individual/windchill_F: 'windchill': '22.1'
```

## MQTTSubscribeService primary thread processing

The line with the prefix `TopicManager data-> outgoing` is the data as its pulled of the queue to be processed.
If an observation is pulled off the queue more than once, it is 'accumulated' (averaged, summed, etc)
The line with the prefix `TopicManager data-> outgoing accumulated` is the result of this 'accumulation process'.
The line with the prefix `data-> final loop packet is` is the loop packet that is returned to WeeWX to be processed.

```
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing weather/individual/altimeter_inHg: 'altimeter': '29.376962790687124', 'dateTime': '1707942725.706721', 'usUnits': '1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing accumulated weather/individual/altimeter_inHg: 'altimeter': '29.376962790687124', 'dateTime': '1707942727.0', 'usUnits': '1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing weather/individual/outHumidity: 'dateTime': '1707942725.675143', 'usUnits': '1', 'weather/individual/outHumidity': '59.0'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing accumulated weather/individual/outHumidity: 'dateTime': '1707942727.0', 'usUnits': '1', 'weather/individual/outHumidity': '59.0'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing weather/individual/barometer_inHg: 'barometer': '29.412', 'dateTime': '1707942725.6694124', 'usUnits': '1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing accumulated weather/individual/barometer_inHg: 'barometer': '29.412', 'dateTime': '1707942727.0', 'usUnits': '1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing weather/individual/windchill_F: 'dateTime': '1707942725.7109332', 'usUnits': '1', 'windchill': '22.1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing accumulated weather/individual/windchill_F: 'dateTime': '1707942727.0', 'usUnits': '1', 'windchill': '22.1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing weather/individual/dewpoint_F: 'dateTime': '1707942725.7087193', 'dewpoint': '9.987458866884577', 'usUnits': '1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing accumulated weather/individual/dewpoint_F: 'dateTime': '1707942727.0', 'dewpoint': '9.987458866884577', 'usUnits': '1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing weather/individual/rain_in: 'dateTime': '1707942725.7006016', 'rain': '0.0', 'usUnits': '1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing accumulated weather/individual/rain_in: 'dateTime': '1707942727.0', 'rain': '0.0', 'usUnits': '1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing weather/individual/pressure_inHg: 'dateTime': '1707942725.703926', 'pressure': '28.85611449159812', 'usUnits': '1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing accumulated weather/individual/pressure_inHg: 'dateTime': '1707942727.0', 'pressure': '28.85611449159812', 'usUnits': '1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing weather/individual/appTemp_F: 'appTemp_F': '16.321245990614706', 'dateTime': '1707942725.7071662', 'usUnits': '1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing accumulated weather/individual/appTemp_F: 'appTemp_F': '16.321245990614706', 'dateTime': '1707942727.0', 'usUnits': '1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing weather/individual/UV: 'dateTime': '1707942725.6772335', 'usUnits': '1', 'weather/individual/UV': '0.0'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing accumulated weather/individual/UV: 'dateTime': '1707942727.0', 'usUnits': '1', 'weather/individual/UV': '0.0'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing weather/individual/outTemp_F: 'dateTime': '1707942725.6712642', 'outTemp': '22.1', 'usUnits': '1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing accumulated weather/individual/outTemp_F: 'dateTime': '1707942727.0', 'outTemp': '22.1', 'usUnits': '1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing weather/individual/cloudbase_foot: 'cloudbase': '3242.850257526233', 'dateTime': '1707942725.7076175', 'usUnits': '1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) TopicManager data-> outgoing accumulated weather/individual/cloudbase_foot: 'cloudbase': '3242.850257526233', 'dateTime': '1707942727.0', 'usUnits': '1'
weewxd[30829]: DEBUG user.MQTTSubscribe: (Service) data-> final packet is 2024-02-14 15:32:07 EST (1707942727): 'altimeter': '29.376962790687124', 'appTemp_F': '16.321245990614706', 'barometer': '29.412', 'cloudbase': '3242.850257526233', 'dateTime': '1707942727.0', 'dewpoint': '9.987458866884577', 'outTemp': '22.1', 'pressure': '28.85611449159812', 'rain': '0.0', 'usUnits': '1', 'weather/individual/outHumidity': '59.0', 'weather/individual/UV': '0.0', 'windchill': '22.1'
```
