#
#    Copyright (c) 2026 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

"""Configurator test helpers shared by the unit and integration suites."""

import argparse


def create_options(**overrides):
    """ Build a Namespace with every Configurator option defaulted to None. """
    options = argparse.Namespace()
    for name in ('type', 'create_example', 'export', 'print_configspec', 'enable',
                 'validate', 'no_backup', 'add_from', 'remove', 'replace_with',
                 'update_from', 'top_level', 'output', 'conf'):
        setattr(options, name, None)
    for name, value in overrides.items():
        setattr(options, name, value)
    return options


def assert_written_config(test_case, configurator, expected_config):
    """ Compare the configurator's output with the expected config text. """
    config_items = []
    configurator.config_dict.filename = None
    for item in configurator.config_dict.write():
        config_items.append(item.decode('utf-8'))
    test_case.assertEqual(config_items, expected_config.split('\n'))
