---
title: Running as a 'standalone' driver
parent: Deprecated Documentation
nav_order: 4
---

**Removed in version 3**

The driver can be run in "standalone" mode.
In this mode, the MQTT data is processed but not written to the database.
This enables one to debug without corrupting the data in the database.
Depending on one's comfort level with python and weewx,
MQTTSubscribe could be run in this mode prior to installation to determine the correct configuration options.

Assuming that MQTTSubscribe has been installed as a driver, the typical invocation would be something like  

```bash
PYTHONPATH=$BIN_ROOT python $BIN_ROOT/user/MQTTSubscribe.py <options> $CONFIG_ROOT/weewx.conf
```  

where:  
$BIN_ROOT - The directory where WeeWX executables are located.  
$CONFIG_ROOT - The directory where the configuration (typically, weewx.conf) is located.  
Because there are [multiple methods to install WeeWX](https://weewx.com/docs/5.0/usersguide/installing/#installation-methods#installation_methods),
location of files can vary. See [where to find things](https://weewx.com/docs/5.0/usersguide/where/)
in the WeeWX [User's Guide](https://weewx.com/docs/5.0/usersguide/introduction/) for the definitive information.

and \<options\> might be:  

```bash
--type=driver --binding=loop --records=2  
```  

where:  
--type=driver, says to run MQTTSubscribeDriver.  
--binding=loop, says that MQTTSubscribeDriver is bound to loop and therefore loop packets will be generated.  
--records=2, says to exit after 2 loop packets have been created.  
  
Run MQTTSubscribe.py with --help to see all the command line options.
