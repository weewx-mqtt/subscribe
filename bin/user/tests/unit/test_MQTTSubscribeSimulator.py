#
#    Copyright (c) 2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position

import helpers
import unittest
import mock

import argparse
import time

import test_weewx_stubs
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

from user.mqttsubscribe import Simulator


def next_period(now, interval):
    """ The next period boundary after now and the wait until it. """
    current_time = int(now + 0.5)
    end_ts = (int(current_time / interval) + 1) * interval
    return end_ts, end_ts - current_time


def create_simulator_options(sim_type, binding, record_count, **overrides):
    """ Build a Namespace with every Simulator option defaulted to None. """
    options = argparse.Namespace()
    for name in ('type', 'binding', 'record_count', 'console', 'conf', 'logging_level',
                 'logging_file', 'units', 'frequency', 'archive_delay', 'archive_interval'):
        setattr(options, name, None)
    options.type = sim_type
    options.binding = binding
    options.record_count = record_count
    for name, value in overrides.items():
        setattr(options, name, value)
    return options


class TestRunSimulator(unittest.TestCase):
    def test_simulate_service_archive(self):
        data = {}
        data['dateTime'] = 0

        frequency = 10

        now = time.time()
        _, sleep_amount = next_period(now, frequency)

        options = create_simulator_options('service',
                                           'archive',
                                           len(data),
                                           console=None,
                                           conf=None,
                                           logging_level=None,
                                           logging_file=None,
                                           units='US',
                                           frequency=frequency)

        with mock.patch('user.mqttsubscribe.MQTTSubscribeService'):
            with mock.patch('user.mqttsubscribe.time') as mock_time:
                with mock.patch('builtins.print'):
                    mock_time.time.return_value = now

                    SUT = Simulator(None, options)

                    mock_engine = mock.Mock()
                    SUT.engine = mock_engine

                    SUT.simulate_service_archive()

        mock_time.sleep.assert_called_once_with(sleep_amount)
        mock_engine.dispatchEvent.assert_called_once()

    def test_simulate_service_packet(self):
        data = {}
        data['dateTime'] = 0

        frequency = 10

        now = time.time()
        _, sleep_amount = next_period(now, frequency)

        options = create_simulator_options('service',
                                           'loop',
                                           len(data),
                                           console=None,
                                           conf=None,
                                           logging_level=None,
                                           logging_file=None,
                                           units='US',
                                           frequency=frequency)

        with mock.patch('user.mqttsubscribe.MQTTSubscribeService'):
            with mock.patch('user.mqttsubscribe.time') as mock_time:
                with mock.patch('builtins.print'):
                    mock_time.time.return_value = now

                    SUT = Simulator(None, options)

                    mock_engine = mock.Mock()
                    SUT.engine = mock_engine

                    SUT.simulate_service_packet()

        mock_time.sleep.assert_called_once_with(sleep_amount)
        mock_engine.dispatchEvent.assert_called_once()

    def test_simulate_driver_archive(self):
        data = {}
        data['dateTime'] = 0

        archive_delay = 15
        archive_interval = 300
        now = time.time()

        end_period_ts, sleep_amount = next_period(now, archive_interval)
        sleep_amount += archive_delay

        options = create_simulator_options('driver',
                                           'archive',
                                           len(data),
                                           console=None,
                                           conf=None,
                                           logging_level=None,
                                           logging_file=None,
                                           archive_delay=archive_delay,
                                           archive_interval=archive_interval)

        SUT = Simulator(None, options)

        with mock.patch('user.mqttsubscribe.time') as mock_time:
            with mock.patch('builtins.print'):
                mock_time.time.return_value = now

                mock_driver = mock.Mock()
                mock_driver.genArchiveRecords.return_value = [data]

                SUT.simulate_driver_archive(mock_driver)

        mock_time.sleep.assert_called_once_with(sleep_amount)
        mock_driver.genArchiveRecords.assert_called_once_with(end_period_ts)

    def test_simulate_driver_loop(self):
        data = {}
        data['dateTime'] = 0

        options = create_simulator_options('driver',
                                           'loop',
                                           len(data),
                                           console=None,
                                           conf=None,
                                           logging_level=None,
                                           logging_file=None,
                                           archive_delay=None,
                                           archive_interval=None)

        SUT = Simulator(None, options)

        with mock.patch('builtins.print'):
            mock_driver = mock.Mock()
            mock_driver.genLoopPackets.return_value = [data]

            SUT.simulate_driver_packet(mock_driver)

        mock_driver.genLoopPackets.assert_called_once()

if __name__ == '__main__':
    helpers.run_tests()
