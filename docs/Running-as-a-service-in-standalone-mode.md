# Running MQTTSubscribeService "standalone"

**Removed in version 3**<br>

The service can be run in "standalone" mode. In this mode, the MQTT data is processed but not written to the database.
This enables one to debug without corrupting the data in the database.
Depending on one's comfort level with python and weewx,
MQTTSubscribe could be run in this mode prior to installation to determine the correct configuration options.

Assuming that MQTTSubscribe has been installed as a service, the typical invocation would be something like

```bash
PYTHONPATH=$BIN_ROOT python $BIN_ROOT/user/MQTTSubscribe.py <options> $CONFIG_ROOT/weewx.conf
```  

where:  
$BIN_ROOT - The directory where WeeWX executables are located.  
$CONFIG_ROOT - The directory where the configuration (typically, weewx.conf) is located.  

Because there are [multiple methods to install WeeWX](https://weewx.com/docs/5.0/usersguide/installing/#installation-methods),
location of files can vary. See [where to find things](https://weewx.com/docs/5.0/usersguide/where/)
in the WeeWX [User's Guide](https://weewx.com/docs/5.0/usersguide/introduction/) for the definitive information.

and \<options\> might be:  

```bash
--type=service --binding=loop --records=2 --interval=5 --delay=0
```  

where:  
--type=service, says to run MQTTSubscribeService.  
--binding=loop, says that MQTTSubscribeService is bound to loop and therefore NEW_LOOP_PACKET events will be created.  
--records=2, says to create 2 NEW_LOOP_PACKET events.  
--interval=5, says to wait 5 seconds between creating events.  
--delay=0, says to create the event immediately after the interval time has passed.  
  
Run MQTTSubscribe.py --help option to see all the command line options.
