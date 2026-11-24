#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

import helpers
import random
import time

import unittest
import mock

import test_weewx_stubs
from test_weewx_stubs import random_string, BaseTestClass
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()
from user.mqttcommon import Logger
from user.mqttsubscribe import RecordCache


def create_cache():
    """ A RecordCache with a mocked logger. """
    return RecordCache(mock.Mock(spec=Logger))


def create_populated_cache():
    """ A RecordCache holding one observation, plus the values that were cached. """
    cache = create_cache()
    unit_system = random.randint(1, 10)
    key = random_string()
    value = round(random.uniform(1, 100), 2)
    timestamp = time.time()
    cache.update_value(key, value, unit_system, timestamp)
    return cache, key, value, unit_system, timestamp


class Test_clear_cache(unittest.TestCase):
    def test_cache_is_cleared(self):
        SUT, _, _, _, _ = create_populated_cache()

        SUT.clear_cache()
        self.assertEqual(SUT.cached_values, {})

class Test_update_value(BaseTestClass):
    def test_value_is_updated(self):
        SUT, key, value, _, timestamp = create_populated_cache()
        self.assertIn(key, SUT.cached_values)
        self.assertEqual(SUT.cached_values[key]['value'], value)
        self.assertEqual(SUT.cached_values[key]['timestamp'], timestamp)

    def test_mismatch_unit_system(self):
        SUT = create_cache()
        unit_system = random.randint(1, 10)

        key = random_string()

        SUT.update_value(key, unit_system, round(random.uniform(1, 100), 2), time.time())

        value = round(random.uniform(1, 100), 2)
        timestamp = time.time()

        unit_system_mismatch = random.randint(11, 20)
        self.assertRaises(ValueError,
                          SUT.update_value, key, value, unit_system_mismatch, timestamp)

class Test_get_value(BaseTestClass):
    def test_key_not_in_cache(self):
        SUT = create_cache()

        value = SUT.get_value(random_string(), 0, None)

        self.assertIsNone(value)

    def test_get_data_expiration_is_none(self):
        SUT = create_cache()
        unit_system = random.randint(1, 10)

        key = random_string()
        value = round(random.uniform(1, 100), 2)
        SUT.update_value(key, value, unit_system, time.time())

        cached_value = SUT.get_value(key, time.time(), None)
        self.assertEqual(cached_value, value)

    def test_get_data_is_not_expired(self):
        SUT, key, value, _, timestamp = create_populated_cache()

        cached_value = SUT.get_value(key, timestamp, 1)
        self.assertEqual(cached_value, value)

    def test_get_data_is_expired(self):
        SUT, key, _, _, timestamp = create_populated_cache()

        cached_value = SUT.get_value(key, timestamp + 1, 0)
        self.assertIsNone(cached_value)

@unittest.skip("Looking at removing the update_timestamp method on the RecordCache class.")
class Test_update_timestamp(BaseTestClass):
    def test_key_does_not_exist(self):
        # somewhat silly test
        SUT = create_cache()
        unit_system = random.randint(1, 10)
        key = random_string()
        value = round(random.uniform(1, 100), 2)
        SUT.update_value(key, value, unit_system, time.time())

        nonexisting_key = random_string()
        SUT.update_timestamp(nonexisting_key, time.time())
        self.assertNotIn(nonexisting_key, SUT.cached_values)

    def test_key_exists(self):
        SUT = create_cache()
        unit_system = random.randint(1, 10)
        key = random_string()
        value = round(random.uniform(1, 100), 2)
        SUT.update_value(key, value, unit_system, 0)

        new_time = time.time()
        SUT.update_timestamp(key, new_time)
        self.assertEqual(SUT.cached_values[key]['timestamp'], new_time)

class Test_remove_value(BaseTestClass):
    def test_key_does_not_exist(self):
        # somewhat silly test
        SUT = create_cache()
        unit_system = random.randint(1, 10)
        key = random_string()
        value = round(random.uniform(1, 100), 2)
        SUT.update_value(key, value, unit_system, time.time())

        nonexisting_key = random_string()
        SUT.remove_value(nonexisting_key)
        self.assertNotIn(nonexisting_key, SUT.cached_values)

    def test_key_exists(self):
        SUT, key, _, _, _ = create_populated_cache()

        SUT.remove_value(key)
        self.assertNotIn(key, SUT.cached_values)

if __name__ == '__main__':
    helpers.run_tests()
