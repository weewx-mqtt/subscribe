#
#    Copyright (c) 2024-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import helpers
import unittest
import random

import paho

import test_weewx_stubs
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

import user.mqttcommon
from user.tests.unit.callback_test_base import CallbackTestBase


@unittest.skipIf(not hasattr(paho.mqtt.client, 'CallbackAPIVersion'), "paho-mqtt is v1, skipping tests.")
class TestCallbacks(CallbackTestBase):
    __test__ = True
    api = user.mqttcommon.API_V2_MQTT5
    log_base = 82000
    subscribe_results = staticmethod(lambda: [random.randint(0, 1)])


if __name__ == '__main__':
    helpers.run_tests()
