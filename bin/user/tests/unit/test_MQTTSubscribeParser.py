#
#    Copyright (c) 2026 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import helpers
import unittest
import mock

import argparse
import os
import sys
import tempfile

import test_weewx_stubs
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

from user.mqttsubscribe import Parser

class TestParserInit(unittest.TestCase):
    def setUp(self):
        # reset stubs for every test
        test_weewx_stubs.setup_stubs()

    def tearDown(self):
        # cleanup stubs
        del sys.modules['weecfg']
        del sys.modules['weeutil']
        del sys.modules['weeutil.config']
        del sys.modules['weeutil.weeutil']
        del sys.modules['weeutil.logger']
        del sys.modules['weewx']
        del sys.modules['weewx.drivers']
        del sys.modules['weewx.engine']

    @staticmethod
    def make_options(config_path, top_level):
        return argparse.Namespace(
            topic='topic1',
            message_file='message.txt',
            conf=config_path,
            type='service',
            top_level=top_level,
            logging_level=None,
            logging_file=None,
            console=False,
        )

    def test_parse_without_top_level(self):
        config_text = '''
[MQTTSubscribeService]
    [[topics]]
        [[[topic1]]]
            [[[[message]]]]
                type = json
'''

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'weewx.conf')
            with open(config_path, 'w', encoding='utf-8') as config_file:
                config_file.write(config_text)

            options = self.make_options(config_path, top_level=False)

            with mock.patch.object(Parser, '_validate'):
                with mock.patch('user.mqttsubscribe.weeutil.config.deep_copy', side_effect=lambda value: value):
                    with mock.patch('user.mqttsubscribe.create_logger'):
                        with mock.patch('user.mqttsubscribe.TopicManager'):
                            with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
                                SUT = Parser(None, options)

        self.assertEqual(SUT.section, 'MQTTSubscribeService')
        self.assertIn('topics', SUT.config_dict)

    def test_parse_top_level_uses_first_section(self):
        config_text = '''
[SomeOtherSection]
    [[topics]]
        [[[topic1]]]
            [[[[message]]]]
                type = json
'''

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'weewx.conf')
            with open(config_path, 'w', encoding='utf-8') as config_file:
                config_file.write(config_text)

            options = self.make_options(config_path, top_level=True)

            with mock.patch.object(Parser, '_validate'):
                with mock.patch('user.mqttsubscribe.weeutil.config.deep_copy', side_effect=lambda value: value):
                    with mock.patch('user.mqttsubscribe.create_logger'):
                        with mock.patch('user.mqttsubscribe.TopicManager'):
                            with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
                                SUT = Parser(None, options)

        self.assertIn('topics', SUT.config_dict)

if __name__ == '__main__':
    helpers.run_tests()
