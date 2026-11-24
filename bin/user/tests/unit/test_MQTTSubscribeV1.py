#
#    Copyright (c) 2024-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import helpers
import mock

import configobj
import random

import test_weewx_stubs
from test_weewx_stubs import random_string
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

import user.mqttcommon
from user.mqttcommon import Logger
from user.mqttsubscribe import MQTTSubscriber
from user.tests.unit.callback_test_base import CallbackTestBase


class TestCallbacks(CallbackTestBase):
    __test__ = True
    api = user.mqttcommon.API_V1
    log_base = 62000
    subscribe_results = staticmethod(lambda: [random.randint(1, 10)])

    def test_protocol_not_found(self):
        mock_logger = mock.Mock(spec=Logger)

        protocol = random_string()
        config = configobj.ConfigObj({'protocol': protocol})

        with self.assertRaises(ValueError) as error:
            MQTTSubscriber(config, mock_logger, api=self.api)

        self.assertEqual(error.exception.args[0], f"Invalid protocol, {protocol}.")

    def test_on_disconnect_no_error(self):
        mock_logger = mock.Mock(spec=Logger)
        config = self.make_config()

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            with mock.patch('user.mqttsubscribe.TopicManager'):
                with mock.patch('user.mqttsubscribe.mqtt.Client'):
                    SUT = self.make_sut(config, mock_logger)

                    SUT._on_disconnect(None, None, 0, None)

                    # A requested disconnect is informational.
                    SUT.logger.info.assert_called_with(self.log_base + 3, "Disconnected with result code 0, No error.")
                    SUT.logger.error.assert_not_called()


if __name__ == '__main__':
    helpers.run_tests()
