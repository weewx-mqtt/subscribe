#
#    Copyright (c) 2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

''''
Shim classes to make migrating from MQTTSubscribe.py to mqttsubscribe.py easier.
'''
import argparse

import user.mqttsubscribe

from user.mqttsubscribe import VERSION, Configurator, Parser, Simulator

class MQTTSubscribeDriver(user.mqttsubscribe.MQTTSubscribeDriver):
    ''' The Driver shim class to make migrating from MQTTSubscribe.py to mqttsubscribe.py easier.'''
    # (methods not used) pylint: disable=abstract-method
    def __init__(self, config_dict, engine):
        super().__init__(config_dict, engine)

        self.logger.info(None, "'MQTTSubscribe.py' is deprecated, it has been renamed to 'mqttsubscribe.py'.")

class MQTTSubscribeService(user.mqttsubscribe.MQTTSubscribeService):
    ''' The Service shim class to make migrating from MQTTSubscribe.py to mqttsubscribe.py easier.'''
    def __init__(self, engine, config_dict):
        super().__init__(engine, config_dict)

        self.logger.info(None, "'MQTTSubscribe.py' is deprecated, it has been renamed to 'mqttsubscribe.py'.")

def loader(config_dict, engine):
    """ Load and return the driver. """
    return MQTTSubscribeDriver(config_dict, engine)  # pragma: no cover

#
# This is an 'exact' copy from mqttsubscribe.py
# It is here to make the move from MQTTSubscribe.py to mqttsubscripte.py easier.
if __name__ == '__main__':  # pragma: no cover
    def main():
        """ Run it."""
        print('Deprecated: MQTTSubscribe.py has been renamed to mqttsubscribe.py')

        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('--version', action='version', version=f"MQTTSubscribe version is {VERSION}")

        subparsers = arg_parser.add_subparsers(dest='command')

        parser_subparser = Parser.add_parsers(subparsers)
        simulator_subparser = Simulator.add_parsers(subparsers)
        configurator_subparser = Configurator.add_parsers(subparsers)

        options = arg_parser.parse_args()

        if options.command == 'parse':
            parser = Parser(parser_subparser, options)
            parser.parse()
        elif options.command == 'simulate':
            simulator = Simulator(simulator_subparser, options)
            simulator.init_configuration(simulator_subparser)
            simulator.init_weewx()
            simulator.run()
        elif options.command == 'configure':
            configurator = Configurator(configurator_subparser, options)
            configurator.run()
        else:
            arg_parser.print_help()

    main()
