#
#    Copyright (c) 2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

''''
Shim classes to make migrating from MQTTSubscribe.py to mqttsubscribe.py easier.
'''
import user.mqttsubscribe

class MQTTSubscribeDriver(user.mqttsubscribe.MQTTSubscribeDriver):
    ''' The Driver shim class to make migrating from MQTTSubscribe.py to mqttsubscribe.py easier.'''
    # (methods not used) pylint: disable=abstract-method
    def __init__(self, config_dict, engine):
        super().__init__(config_dict, engine)

        self.logger.info(None, 'Deprecated: MQTTSubscribe.py has been renamed to mqttsubscribe.py')

class MQTTSubscribeService(user.mqttsubscribe.MQTTSubscribeService):
    ''' The Service shim class to make migrating from MQTTSubscribe.py to mqttsubscribe.py easier.'''
    def __init__(self, engine, config_dict):
        super().__init__(engine, config_dict)

        self.logger.info(None, 'Deprecated: MQTTSubscribe.py has been renamed to mqttsubscribe.py')

def loader(config_dict, engine):
    """ Load and return the driver. """
    return MQTTSubscribeDriver(config_dict, engine)  # pragma: no cover
