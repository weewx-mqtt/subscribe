# Getting started

## Prerequisites

A basic understanding of WeeWX and MQTT is required.

A MQTT broker publishing the desired data to one or more topics.

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

    2. [MQTTSubscribe Simulator](https://github.com/weewx-mqtt/subscribe/wiki/MQTTSubscribe-Simulator-mode)

        The advantage of using MQTTSubscribe Simulator is that it can be used to also test the MQTTSubscribe section of the WeeWX configuration.

        This does require MQTTSubscribe to be [installed](https://github.com/weewx-mqtt/subscribe/wiki#installing-mqttsubscribe) and [configured](https://github.com/weewx-mqtt/subscribe/wiki#installing-mqttsubscribe).

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

## Required WeeWX information

Next up is to determine the necessary information to configure MQTTSubscribe

1. Determine if MQTTSubscribe should be run as a driver or service.

    If you have an existing WeeWX installation running and you want to add/augment with it data from MQTT, run MQTTSubscribe as a service.
    If this will be a new WeeWX installation where the data is being received via MQTT, run MQTTSubscribe as a driver.

2. Determine incoming 'unit system'.

    WeeWX has 3 [unit systems](https://weewx.com/docs/5.0/reference/units/).
    MQTTSubscribe must be configured to use one. The default is `US`
    - US - U.S. Customary
    - METRICWX - Metric, with rain related measurements in mm and speeds in m/s
    - METRIC - Metric, with rain related measurements in cm and speeds in km/hr

3. Determine what data transformation/conversion needs to be done on the incoming data.

    MQTTTSubscribe supports many types of transformations/conversions of the incoming data.
    - Ignore incoming data.
    - Renaming the incoming name of the field/observation.
    - By default incoming data is converted to type float. MQTTSubscribe supports conversion to int and str types.
    - If all of the incoming data does not belong to the same WeeWX unit system, each field can specify its units.
    - WeeWX expects some data (for example, rain) to be an increment from previous 'readings.
    If the MQTT data is a running total, MQTTSubscribe can 'convert' into an increment before passing it to WeeWx.
    - And any other required transformations/conversions...

## Installing MQTTSubscribe

Installing MQTTSubscribe put placeholder sections for both MQTTSubscribeDriver and MQTTSubscribeService.
Until additional configuration updates are made, neither of these will run when WeeWX is restarted.
This allows one to install MQTTSubscribe and not 'break' an existing WeeWX installation.
This allows the running MQTTSubscribe in simulation mode to debug prior to running it under WeeWX.

To install version 3.x with WeeWX 5.x see, [Installing and updating version 3.x with WeeWX 5.x](https://github.com/weewx-mqtt/subscribe/blob/master/README.md#initial-installation).

To install version 3.x with WeeWX 4.x see,
[Installing and updating version 3.x with WeeWX 4.x](https://github.com/weewx-mqtt/subscribe/wiki/Installing-and-updating-version-3.x--with-WeeWX-4.x).

To install version 2.x and prior see,
[Installing and Updating Version 2.X and Earlier](https://github.com/weewx-mqtt/subscribe/wiki/Installing-and-updating-version-2.x-and-earlier).

## Configuring MQTTSubscribe

It is highly recommended that these
[steps](https://github.com/weewx-mqtt/subscribe/blob/master/README.md#configure-mqttsubscribe) are used to configure MQTTSubscribe.
Following these steps configures MQTTSubscribe and tests the configuration without impacting an existing WeeWX installation.

## Running MQTTSubscribe with WeeWX

If running as a driver follow [these instructions]($WEECTL station reconfigure --driver=user.MQTTSubscribe --no-prompt)
to set the driver to `MQTTSubscribe`.

If running as a service, follow [these](https://github.com/weewx-mqtt/subscribe#if-running-as-a-service-enable-it) to enable it.

Then update WeeWX's configuration via [these instructions](https://github.com/weewx-mqtt/subscribe#update-weewx-with-mqttsubscribes-configuration).

## Debugging

See, [debugging](https://github.com/weewx-mqtt/subscribe/wiki/Debugging).
