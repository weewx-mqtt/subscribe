#
#    Copyright (c) 2026 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

"""Shared paho callback tests for the v1, v2-mqtt5 and v2-mqtt3 API variants."""

import mock
import configobj
import random

from test_weewx_stubs import BaseTestClass, random_string

import user.mqttcommon
from user.mqttcommon import Logger
from user.mqttsubscribe import MQTTSubscriber


class CallbackTestBase(BaseTestClass):
    """Exercise the paho callbacks; subclasses supply the API and its log-id block."""

    __test__ = False  # shared base; only the API-specific subclasses are collected

    api = None
    log_base = 0
    subscribe_results = staticmethod(lambda: [])

    def make_config(self, use_topic=False, **overrides):
        config_dict = {
            'message_callback': {},
            'topics': {random_string(): {}} if use_topic else {},
        }
        config_dict.update(overrides)
        return configobj.ConfigObj(config_dict)

    def make_sut(self, config, mock_logger):
        return MQTTSubscriber(config, mock_logger, api=self.api)

    def test_on_connect(self):
        mock_logger = mock.Mock(spec=Logger)
        config = self.make_config()

        flags = random_string()
        rc = random.randint(1, 10)

        with mock.patch('user.mqttsubscribe.TopicManager'):
            with mock.patch('user.mqttsubscribe.mqtt.Client'):
                SUT = self.make_sut(config, mock_logger)

                SUT._on_connect(None, {}, flags, rc, None)

                self.assertEqual(SUT.logger.info.call_count, 17)
                mock_logger.info.assert_any_call(
                    self.log_base + 1, f"Connected with result code {rc}, {user.mqttsubscribe.mqtt.error_string(rc)}")
                mock_logger.info.assert_any_call(self.log_base + 2, f"Connection flags: {flags}.")

    def test_on_disconnect(self):
        mock_logger = mock.Mock(spec=Logger)
        config = self.make_config()

        rc = random.randint(1, 10)

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            with mock.patch('user.mqttsubscribe.TopicManager'):
                with mock.patch('user.mqttsubscribe.mqtt.Client'):
                    SUT = self.make_sut(config, mock_logger)

                    SUT._on_disconnect(None, None, rc, None)

                    # A non-zero result code is an error, and names the error.
                    SUT.logger.error.assert_called_with(
                        self.log_base + 3,
                        f"Disconnected with result code {rc}, {user.mqttsubscribe.mqtt.error_string(rc)}")

    def test_on_subscribe(self):
        mock_logger = mock.Mock(spec=Logger)
        config = self.make_config()

        mid = random.randint(1, 10)
        results = self.subscribe_results()

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            with mock.patch('user.mqttsubscribe.TopicManager'):
                with mock.patch('user.mqttsubscribe.mqtt.Client'):
                    SUT = self.make_sut(config, mock_logger)

                    SUT._on_subscribe(None, None, mid, results, None)

                    SUT.logger.info.assert_called_with(
                        self.log_base + 4,
                        f"Subscription acknowledged, mid {mid}, result code {results[0]}.")

    def test_on_log(self):
        mock_logger = mock.Mock(spec=Logger)
        config = self.make_config()

        level = 1
        msg = random_string()

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            with mock.patch('user.mqttsubscribe.TopicManager'):
                with mock.patch('user.mqttsubscribe.mqtt.Client'):
                    SUT = self.make_sut(config, mock_logger)

                    SUT._on_log(None, None, level, msg)

                    SUT.logger.info.assert_called_with(None, f"MQTTSubscribe MQTT: {msg}")

    def test_mqtt_log_set(self):
        mock_logger = mock.Mock(spec=Logger)
        config = self.make_config(use_topic=True, log=True)

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            with mock.patch('user.mqttsubscribe.TopicManager'):
                with mock.patch('user.mqttsubscribe.mqtt.Client'):
                    SUT = self.make_sut(config, mock_logger)

                    self.assertEqual(SUT.client.on_log, SUT._on_log)

    def test_mqtt_log_not_set(self):
        mock_logger = mock.Mock(spec=Logger)
        config = self.make_config(use_topic=True)

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            with mock.patch('user.mqttsubscribe.TopicManager'):
                with mock.patch('user.mqttsubscribe.mqtt.Client'):
                    SUT = self.make_sut(config, mock_logger)

                    self.assertNotEqual(SUT.client.on_log, SUT._on_log)

    def test_mqtt_log_mqtt_set(self):
        mock_logger = mock.Mock(spec=Logger)
        config = self.make_config(use_topic=True, log_mqtt=True)

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            with mock.patch('user.mqttsubscribe.TopicManager'):
                with mock.patch('user.mqttsubscribe.mqtt.Client'):
                    SUT = self.make_sut(config, mock_logger)

                    self.assertEqual(SUT.client.on_log, SUT._on_log)

    def test_mqtt_log_mqtt_takes_precedence_over_log(self):
        mock_logger = mock.Mock(spec=Logger)
        config = self.make_config(use_topic=True, log=True, log_mqtt=False)

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            with mock.patch('user.mqttsubscribe.TopicManager'):
                with mock.patch('user.mqttsubscribe.mqtt.Client'):
                    SUT = self.make_sut(config, mock_logger)

                    self.assertNotEqual(SUT.client.on_log, SUT._on_log)
