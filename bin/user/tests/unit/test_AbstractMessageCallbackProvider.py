#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import contextlib
import helpers
import mock

import random

import test_weewx_stubs
from test_weewx_stubs import random_string, BaseTestClass
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

from user.mqttcommon import Logger
from user.mqttsubscribe import AbstractMessageCallbackProvider, TopicManager

# todo - mock?
def to_float(x):
    if isinstance(x, str) and x.lower() == 'none':
        x = None
    return float(x) if x is not None else None


def create_conversion_func():
    """ The resolver the provider uses to convert observation values. """
    return {
        'source': 'lambda x: to_float(x)',
        'compiled': eval('lambda x: to_float(x)')  # nosec B307 - example expression pylint: disable=eval-used
    }


@contextlib.contextmanager
def create_provider():
    """ Build a provider with mocked collaborators and patched weewx.units. """
    with mock.patch('user.mqttsubscribe.weewx.units') as mock_weewx_units:
        provider = AbstractMessageCallbackProvider(mock.Mock(spec=Logger), mock.Mock(spec=TopicManager))
        yield provider, mock_weewx_units


class TestTest(BaseTestClass):
    def test_contains_total_invalid_previous_value(self):
        with create_provider() as (SUT, _):
            default_field_conversion_func = create_conversion_func()
            orig_name = random_string()
            topic = random_string()
            previous_value = round(random.uniform(101, 200), 2)
            SUT.previous_values = {
                (topic, orig_name): previous_value
            }
            fields = {
                orig_name: {
                    'contains_total': True
                }
            }
            orig_value = round(random.uniform(10, 100), 2)
            unit_system = random.randint(1, 99)
            (updated_name, updated_value) = SUT._update_data(topic, orig_name, orig_value, fields, default_field_conversion_func, unit_system)
            self.assertEqual(updated_name, orig_name)
            self.assertIsNone(updated_value)
            self.assertEqual(SUT.previous_values[(topic, orig_name)], orig_value)

    def test_contains_total_no_previous_value(self):
        with create_provider() as (SUT, _):
            default_field_conversion_func = create_conversion_func()
            orig_name = random_string()
            topic = random_string()
            fields = {
                orig_name: {
                    'contains_total': True
                }
            }
            orig_value = round(random.uniform(10, 100), 2)
            unit_system = random.randint(1, 99)
            (updated_name, updated_value) = SUT._update_data(topic, orig_name, orig_value, fields, default_field_conversion_func, unit_system)
            self.assertEqual(updated_name, orig_name)
            self.assertIsNone(updated_value)
            self.assertEqual(SUT.previous_values[(topic, orig_name)], orig_value)

    def test_contains_total(self):
        with create_provider() as (SUT, _):
            default_field_conversion_func = create_conversion_func()
            orig_name = random_string()
            topic = random_string()
            previous_value = round(random.uniform(0, 9), 2)
            SUT.previous_values = {
                (topic, orig_name): previous_value
            }
            fields = {
                orig_name: {
                    'contains_total': True
                }
            }
            orig_value = round(random.uniform(10, 100), 2)
            unit_system = random.randint(1, 99)
            (updated_name, updated_value) = SUT._update_data(topic, orig_name, orig_value, fields, default_field_conversion_func, unit_system)
            self.assertEqual(updated_name, orig_name)
            self.assertEqual(updated_value, orig_value - previous_value)
            self.assertEqual(SUT.previous_values[(topic, orig_name)], orig_value)

    def test_contains_total_is_per_topic(self):
        with create_provider() as (SUT, _):
            default_field_conversion_func = create_conversion_func()
            orig_name = random_string()
            topic1 = random_string()
            topic2 = random_string()
            SUT.previous_values = {
                (topic1, orig_name): 10.0,
                (topic2, orig_name): 100.0,
            }
            fields = {
                orig_name: {
                    'contains_total': True
                }
            }
            unit_system = random.randint(1, 99)
            (_, value1) = SUT._update_data(topic1, orig_name, 12.0, fields, default_field_conversion_func, unit_system)
            (_, value2) = SUT._update_data(topic2, orig_name, 105.0, fields, default_field_conversion_func, unit_system)
            (_, value1_again) = SUT._update_data(topic1, orig_name, 15.0, fields, default_field_conversion_func, unit_system)
            self.assertEqual(value1, 2.0)
            self.assertEqual(value2, 5.0)
            self.assertEqual(value1_again, 3.0)
            self.assertEqual(SUT.previous_values[(topic1, orig_name)], 15.0)
            self.assertEqual(SUT.previous_values[(topic2, orig_name)], 105.0)

    def test_wrap_around(self):
        with create_provider() as (SUT, _):
            default_field_conversion_func = create_conversion_func()
            orig_name = random_string()
            topic = random_string()
            previous_value = round(random.uniform(10, 100), 2)
            SUT.previous_values = {
                (topic, orig_name): previous_value
            }
            fields = {
                orig_name: {
                    'contains_total': True,
                    'total_wrap_around': True
                }
            }
            orig_value = round(random.uniform(0, 9), 2)
            unit_system = random.randint(1, 99)
            (updated_name, updated_value) = SUT._update_data(topic, orig_name, orig_value, fields, default_field_conversion_func, unit_system)
            self.assertEqual(updated_name, orig_name)
            self.assertEqual(updated_value, orig_value)
            self.assertEqual(SUT.previous_values[(topic, orig_name)], orig_value)

    def test_converting_value(self):
        with create_provider() as (SUT, mock_weewx_units):
            default_field_conversion_func = create_conversion_func()
            mock_weewx_units.getStandardUnitType.return_value = (random_string(), random_string())
            converted_value = round(random.uniform(10, 100), 2)
            mock_weewx_units.convert.return_value = (converted_value, random_string(), random_string())
            orig_name = random_string()
            topic = random_string()
            fields = {
                orig_name: {
                    'units': random_string(),
                }
            }
            orig_value = round(random.uniform(10, 100), 2)
            unit_system = 99
            (updated_name, updated_value) = SUT._update_data(topic, orig_name, orig_value, fields, default_field_conversion_func, unit_system)
            self.assertEqual(updated_name, orig_name)
            self.assertEqual(updated_value, converted_value)
            self.assertEqual(SUT.previous_values, {})

if __name__ == '__main__':
    helpers.run_tests()
