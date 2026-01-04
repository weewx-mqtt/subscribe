---
title: Required WeeWX information
parent: Getting Started
nav_order: 3
---

## Required MQTT information

First up is to ensure that you can subscribe to the MQTT topics independent of WeeWX and obtain a basic understanding of the data being published.

1. Determine the information is required to subscribe to the MQTT topic(s). Some of the questions to answer are:
    - What is the broker/server name?
    - What is the port to connect to?
    - Is a username/password required?
    - What topics is the data being published to?
    - etc.

2. Test that you can subscribe to the MQTT topic(s). A couple of options are:

    1. [mosquitto_sub](https://mosquitto.org/man/mosquitto_sub-1.html)

        The advantage of using mosquitto_sub, it is a widely used utility and therefore a lot of information can be found on the web.

    2. [MQTTSubscribe Simulator]({{site.baseurl}}/simulator-mode)

        The advantage of using MQTTSubscribe Simulator is that it can be used to also test the MQTTSubscribe section of the WeeWX configuration.

        This does require MQTTSubscribe to be [installed]({{site.baseurl}}/getting-started/installing) and [configured]({{site.baseurl}}/getting-started/configuring).

3. Determine the MQTT message 'type'.

    Currently three message 'types' are supported.

    1. 'individual' - Each field is its own topic and the MQTT message is the value.
    For example,

        The value `1` is published to a topic of `topic/id`
        and the value `26.7` is published to a topic of `topic/temp1`.

    2. 'json' - The MQTT message is json.
    The json field/values in the message map to field/values in WeeWx.
    An example message is,

        ```
        {
         "id": 1,
         "temp1": “26.7“
        }
        ```

    3. 'keyword' - The MQTT message is delimited data of keywords and values.
    The json field/values in the message map to field/values in WeeWx.
    An example message is,

        ```
        id=1,temp1=26.7
        ```
