---
title: Supporting Additional Message Types
nav_order: 17
---

Out of the box MQTTSubscribe can handle the following MQTT payload formats:  
Individual - each MQTT message has a single weather obsevation value and the topic is the name of it.  
Keyword - each MQTT message has a set of observations in the form of ```name1=value1,name2=value2```.  
JSON - each MQTT message has a JSON formatted set of observations.  

If a different payload format is needed, MQTTSubscribe can easily be extended to handle it.
An example that parses XML can be found in [ExampleMessageCallbackProvider.py](https://github.com/weewx-mqtt/subscribe/blob/master/bin/user/ExampleMessageCallbackProvider.py)
and some unit tests for it are in [test_ExamoleMessageCallbackProvider.py](https://github.com/weewx-mqtt/subscribe/blob/master/bin/user/tests/unit/test_ExampleCallbackProvider.py)

First, looking at the weewx configuration file. The option, message_callback_provider, is set to the name of the class that will handle the MQTT message.
For this example it would look like this.

```
[MQTTSubscribeService] or [MQTTSubscribeDriver]
    # The message callback provider.
    message_callback_provider = user.ExampleMessageCallbackProvider.MessageCallbackProvider
```

The [[message_callback]] stanza contains any configuation options specific to this program.  In this case no addition configuration is needed.

Next, looking at what the program needs to implement.
First, it should inherit from the AbstractMessageCallbackProviderClass. There are three methods that need to be implemented.

The \_\_init\_\_ method which takes three parameters.  
config: the [[message_callback]] configuration data.  
logger: an instance of the Logger class.
This should be used to keep the logging consistent with MQTTSubscribe.  
topic_manager: an instance of the TopicManager class.
It's append method is called with the reformatted weather data.
It also has a get_fields method which returns the `field` configuration data for the message `topic`.

The get_callback method which returns the MQTT on_message callback routine.  

The MQTT on_message callback. In the example this is on_message.
The parameters correspond to the signature of the MQTT on_message callback.
It is responsible for processing the data into a WeeWx weather observation dictionary and calling the topic_manager append function.

Lastly, the abstract class has a method, _update_data method.
This function takes a fieldname and value and using the field configuration data, converts it into a WeeWX fieldname and value. The parameters are:

Fields configuration:

Input Name:

Input Value:

Output unit_system

Note, the plugin capability is beta and there maybe breakin changes to the interfaces.
