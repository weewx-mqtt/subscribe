# The mqtt_test.py utility

**Deprecated in version 3.0, use [simulation mode](https://github.com/weewx-mqtt/subscribe/wiki/MQTTSubscribe-Simulator-mode).**

This can be retrieved via the command, `wget https://github.com/weewx-mqtt/subscribe/blob/master/mqtt_test.py`

This is a small utility that can help debug problems when running MQTTSubscribe.
It reads the WeeWX configuration file (typically weewx.conf) for the necessary MQTT options to connect and subscribe to the topics.
As the topic data is received it is written to the console.

The configuration file can actually be stripped down to just the MQTTSubscribeDriver or MQTTSubscribeService stanzas.
This allows one to get the MQTT configuration correct prior to configuring WeeWX.

Optionally, the MQTT options can be passed in as parameters.
These will override the options in the configuration file.
This enables one to quickly and easily determine the correct MQTT options needed.

A few key parameters are `--type`, `--records`, and `--quiet`.
The --type controls which stanza, `[MQTTSubscribeDriver]` or [`MQTTSubscribeService]` is read.
The default us to read from the `[MQTTSubscribeDriver]` section.
The --records controls how many MQTT 'records' are processed.
The default is to loop forever.
The `--quiet` option turns off MQTT logging.

Invoke the utility with --help to see all the parameters.

**Note:** when using the plugin as a service, be sure to pass the commandline option `--type=service` when invoking the test script.
 This ensures that the configuration options are parsed from the `[MQTTSubscribeService]` section.
