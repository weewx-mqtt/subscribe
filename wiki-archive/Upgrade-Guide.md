# Upgrade Guide

When a version upgrade requires specific steps, it will be documented below.

## Upgrading to v3+ from v2

The release can be found [here](https://github.com/weewx-mqtt/subscribe/releases/tag/v3.0.0)

### Breaking Changes

Python 3.7 or higher is now required. Active support ended June 2020 and security updates stopped in June 2023.

WeeWX 4 or higher is required. Support for Python 3 was introduced in WeeWX 4 in April 2020.

MQTTSubscribe now validates the MQTTSubscribe configuration on startup.
The default behavior is to log any errors and continue, allowing WeeWX to startup.
Ideally errors would stop WeeWX from starting. 
But to make V3 more backward compatible, it was decided to just log the errors by default.
Note, some of these errors were silently ignored in previous versions.
Note, new installs will have the [stop_on_validation_errors=true](https://github.com/weewx-mqtt/subscribe/wiki/Common-Options#stop_on_validation_errors)

### Upgrade Steps

While one could use [weectl](http://www.weewx.com/docs/5.0/utilities/weectl-extension/) (or even just copy the new MQTTSubscribe.py), it is recommended that these [steps](https://github.com/weewx-mqtt/subscribe?tab=readme-ov-file#updating-mqttsubscribe) be followed.
Following the steps include running MQTTSubscribe in [configuration mode](https://github.com/weewx-mqtt/subscribe/wiki/Configurator-Mode) to [validate](https://github.com/weewx-mqtt/subscribe/wiki/Configurator-Mode#--validate) the configuration prior to restarting WeeWX.
If any errors are found, they can be corrected or [stop_on_validation_errors](https://github.com/weewx-mqtt/subscribe/wiki/Common-Options#stop_on_validation_errors--true) can be set to `false`.


