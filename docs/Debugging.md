# Debugging

It is highly recommended that when debugging, MQTTSubscribe is run in [simulator mode](https://github.com/weewx-mqtt/subscribe/wiki/Simulator-mode).
This has the following advantages.

- It does not impact a running WeeWX installation.
- It is easy to increase logging to the `debug` level.
- Logging can easily be redirected to a different location.

After [initializing MQTTSubscribes context](https://github.com/weewx-mqtt/subscribe?tab=readme-ov-file#initialize-mqttsubscribes-runtime),
the invocation would look something like this.

```
python3 $USER_ROOT/MQTTSubscribe.py simulate $RUN_MODE --conf mqttsubscribe.template.conf --verbose --logging-file=log.txt
```

Below is information that one can use to debugging.
But, feel free to [open an issue](https://github.com/weewx-mqtt/subscribe/issues/new),
[start a discussion in github](https://github.com/weewx-mqtt/subscribe/discussions/new),
or [post on WeeWX google group](https://groups.google.com/g/weewx-user).

## MQTTSubscribeDriver

In order to debug, one needs to have an understanding of the processing performed by MQTTSubscribeDriver.
At a high level there are three main areas as outlined below.

```
Initialize MQTTSubscribe
Initialize MQTT
    connect
    subscribe
    start secondary thread

MQTTSubscribeDriver secondary thread processing
   receive message, 
   transform data as necessary
   put data on a queue (each topic has its own queue)

MQTTSubscribeDriver primary thread
    For each queue
        take data off
        create loop packet
        yield packet to WeeWX
```

### Initialize MQTTSubscribe

Most of the information logged for this processing will not be ueful to the average use of MQTTSubscribe.
But this information can be **very** useful to the developers of MQTTSubscribe.
Information related to configuring the MQTT connection is logged and should be reviewed for correctness.
Example of information logged is [here](https://github.com/weewx-mqtt/subscribe/wiki/Understanding-the-log#mqtt-parameters).

### Initialize MQTT

This has information about establishing the MQTT connection and subscriptions.
It should be reviewed to ensure the connection was established and the expected topics were subscribed to.
Example of information logged is [here](https://github.com/weewx-mqtt/subscribe/wiki/Understanding-the-log#mqtt-initialization)

### MQTTSubscribeDriver secondary thread processing

This is information about the data received from MQTT and its transformed value.
Searching on`MessageCallbackProvider data-> incoming`, will display the raw data received from MQTT.
It should be reviewed to ensure the expected data is being received.
Searching on `TopicManager data-> incoming`, will display the data after the configured transformations have happened.
It is the data that will be in the WeeWX loop packet.
Example of information logged is [here](https://github.com/weewx-mqtt/subscribe/wiki/Understanding-the-log#mqttsubscribedriver-secondary-thread-processing)

### MQTTSubscribeDriver primary thread

This information about the data as it is pulled off the queue and 'sent' to WeeWX.
Searching on`TopicManager data->`, will display the data pulled from the queue.
It should match the data displayed when searching on `TopicManager data-> incoming`.
Because of the asynchronous nature of the two threads, it can be a bit of a challenge finding the matching pairs.
Searching on `data-> final loop packet is` is the data that is 'sent' to WeeWx.
If this data is correct, any problems are most likely not with WeeWX.
Otherwise, it is most likely a MQTTSubscribe problem and rhe previous processing logs need to be looked at closer.
It might even be necessary to set `debug = 2` and generate new logs.
Example of information logged is [here](https://github.com/weewx-mqtt/subscribe/wiki/Understanding-the-log#mqttsubscribedriver-primary-thread-processing)

## MQTTSubscribeService

```
Initialize MQTTSubscribe
Initialize MQTT
    connect
    subscribe
    start secondary thread

MQTTSubscribeService secondary thread processing
   receive message, 
   transform data as necessary
   put data on a queue (each topic has its own queue)
   
MQTTSubscribeService primary thread
    Called by WeeWX to augment loop packet
    For each queue
        take data off
        'accumulate' the data for a given observation into a single value (average, sum, first, last, etc)
        update the loop packet
```

### MQTTSubscribeService secondary thread processing

This is information about the data received from MQTT and its transformed value.
Searching on`MessageCallbackProvider data-> incoming`, will display the raw data received from MQTT.
It should be reviewed to ensure the expected data is being received.
Searching on `TopicManager data-> incoming`, will display the data after the configured transformations have happened.
If necessary, this data will be 'accumulated' in the primary thread.
Example of information logged is [here](https://github.com/weewx-mqtt/subscribe/wiki/Understanding-the-log#mqttsubscribeservice-secondary-thread-processing)

### MQTTSubscribeService  primary thread

This information about the data as it is pulled off the queue and 'sent' to WeeWX.
Searching on`TopicManager data->`, will display the data pulled from the queue.
It should match the data displayed when searching on `TopicManager data-> incoming`.
Because of the asynchronous nature of the two threads, it can be a bit of a challenge finding the matching pairs.
If an observation is pulled off the queue more than once, it is 'accumulated' (averaged, summed, etc.).
The line with the prefix TopicManager data-> outgoing accumulated is the result of this 'accumulation process'.
Searching on `data-> final loop packet is` is the data that is 'sent' to WeeWx.
If this data is correct, any problems are most likely not with WeeWX.
Otherwise, it is most likely a MQTTSubscribe problem and rhe previous processing logs need to be looked at closer.
It might even be necessary to set `debug = 2` and generate new logs.
Example of information logged is [here](https://github.com/weewx-mqtt/subscribe/wiki/Understanding-the-log#mqttsubscribeservice-primary-thread-processing)
