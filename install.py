#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
""" Installer for MTTQSubscribe driver and service. """

from io import StringIO

import configobj

import weeutil

from weecfg.extension import ExtensionInstaller

VERSION = '3.2.0-rc01a'

MQTTSUBSCRIBE_CONFIG = """

[MQTTSubscribeDriver]
    # This section is for the MQTTSubscribe driver.

    # The driver to use.
    # Only used by the driver.
    driver = user.mqttsubscribe

    # Controls if validation errors raise an exception (stopping WeeWX from starting) or only logged.
    # Default is false
    stop_on_validation_errors = true

[MQTTSubscribeService]
    # This section is for the MQTTSubscribe service.

    # Turn the service on and off.
    # Default is: true
    # Only used by the service.
    enable = false

    # Controls if validation errors raise an exception (stopping WeeWX from starting) or only logged.
    # Default is false
    stop_on_validation_errors = true

"""

def loader():
    """ Load and return the extension installer. """
    return MQTTSubscribeServiceInstaller()


class MQTTSubscribeServiceInstaller(ExtensionInstaller):
    """ The extension installer. """
    def __init__(self):
        install_dict = {
            'version': VERSION,
            'name': 'MQTTSubscribe',
            'description': 'Source WeeWX data from MQTT.',
            'author': "Rich Bell",
            'author_email': "bellrichm@gmail.com",
            'files': [('bin/user', ['bin/user/mqttsubscribe.py'])]
        }

        MQTTSubscribe_dict = configobj.ConfigObj(StringIO(MQTTSUBSCRIBE_CONFIG))  # pylint: disable = invalid-name
        install_dict['config'] = MQTTSubscribe_dict
        install_dict['data_services'] = 'user.mqttsubscribe.MQTTSubscribeService'

        super().__init__(install_dict)

    def configure(self, engine):
        self.fix_deprecated_file_name(engine)
        return True

    def fix_deprecated_file_name(self, engine):
        """ Update old configuration data from the olde filename, MQTTSubscribe.py, to the new name, mqttsubscribe.py."""
        deprecated_service_name = 'user.MQTTSubscribe.MQTTSubscribeService'
        deprecated_driver_name = 'user.MQTTSubscribe'

        if deprecated_service_name in weeutil.weeutil.option_as_list(engine.config_dict['Engine']['Services']['data_services']):
            engine.printer.out(f"Removing deprecated service name, {deprecated_service_name}.")
            engine.config_dict['Engine']['Services']['data_services'].remove(deprecated_service_name)

        if 'MQTTSubscribeDriver' in engine.config_dict and engine.config_dict['MQTTSubscribeDriver'].get('driver') == deprecated_driver_name:
            engine.printer.out(f"Renaming deprecated driver name, {deprecated_driver_name} to user.mqttsubscribe.")
            engine.config_dict['MQTTSubscribeDriver']['driver'] = 'user.mqttsubscribe'
