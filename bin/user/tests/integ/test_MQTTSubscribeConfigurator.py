#
#    Copyright (c) 2023-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import helpers
import unittest

from user.mqttsubscribe import Configurator
from user.tests.configurator_helpers import create_options, assert_written_config

class TestUpdateConfig(unittest.TestCase):
    # @unittest.skip("This is really not a unit test, it is testing weeutil.config.conditional_merge")
    def test_add_from(self):
        options = create_options(type='driver',
                                 create_example=None,
                                 export=None,
                                 print_configspec=None,
                                 enable=None,
                                 validate=None,
                                 no_backup=True,
                                 add_from='bin/user/tests/data/mqttsubscribe.conf',
                                 remove=None,
                                 replace_with=None,
                                 update_from=None,
                                 top_level=None,
                                 output='bin/user/tests/data/output.conf',
                                 conf='bin/user/tests/data/weewx.conf')

        expected_config = '''[MQTTSubscribeDriver]
    [[topic]]
        [[[field-1]]]
            name = rename-1a
        [[[field-2]]]
        [[[field-3]]]'''

        SUT = Configurator(None, options)

        SUT.run()

        assert_written_config(self, SUT, expected_config)

    def test_remove(self):
        options = create_options(type='driver',
                                 create_example=None,
                                 export=None,
                                 print_configspec=None,
                                 enable=None,
                                 validate=None,
                                 no_backup=True,
                                 add_from=None,
                                 remove=True,
                                 replace_with=None,
                                 update_from=None,
                                 top_level=None,
                                 output='bin/user/tests/data/output.conf',
                                 conf='bin/user/tests/data/weewx.conf')

        SUT = Configurator(None, options)

        SUT.run()

        SUT.config_dict.filename = None

        self.assertEqual(SUT. config_dict.write(), [])

    # @unittest.skip("This tests uses weeutil.config.deep_copy")
    def test_replace_with(self):
        options = create_options(type='driver',
                                 create_example=None,
                                 export=None,
                                 print_configspec=None,
                                 enable=None,
                                 validate=None,
                                 no_backup=True,
                                 add_from=None,
                                 remove=None,
                                 top_level=None,
                                 replace_with='bin/user/tests/data/mqttsubscribe.conf',
                                 update_from=None,
                                 output='bin/user/tests/data/output.conf',
                                 conf='bin/user/tests/data/weewx.conf')

        expected_config = '''[MQTTSubscribeDriver]
    [[topic]]
        [[[field-1]]]
            name = rename-1b
        [[[field-3]]]'''

        SUT = Configurator(None, options)

        SUT.run()

        assert_written_config(self, SUT, expected_config)

    # @unittest.skip("This is really not a unit test, it is testing weeutil.config.merge_config")
    def test_update_from(self):
        options = create_options(type='driver',
                                 create_example=None,
                                 export=None,
                                 print_configspec=None,
                                 enable=None,
                                 validate=None,
                                 no_backup=True,
                                 add_from=None,
                                 remove=None,
                                 replace_with=None,
                                 top_level=None,
                                 update_from='bin/user/tests/data/mqttsubscribe.conf',
                                 output='bin/user/tests/data/output.conf',
                                 conf='bin/user/tests/data/weewx.conf')

        expected_config = '''[MQTTSubscribeDriver]
    [[topic]]
        [[[field-1]]]
            name = rename-1b
        [[[field-2]]]
        [[[field-3]]]'''

        SUT = Configurator(None, options)

        SUT.run()

        assert_written_config(self, SUT, expected_config)

if __name__ == '__main__':
    helpers.run_tests()
