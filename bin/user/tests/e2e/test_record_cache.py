#
#    Copyright (c) 2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import contextlib
import helpers
import unittest
import mock

import configobj
from io import StringIO

import weewx.engine

config_dict = f"""

WEEWX_ROOT = tmp

[Station]
    altitude = 495, foot
    latitude = 0.0
    longitude = 0.0
    station_type = Simulator

[Simulator]
    driver = user.tests.e2e.simulator

[StdReport]

[StdArchive]
    archive_interval = 60
    archive_delay = 1

[DataBindings]
    [[wx_binding]]
        database = archive_sqlite
        table_name = archive
        manager = weewx.manager.DaySummaryManager
        schema = schemas.wview_extended.schema

[Databases]
    [[archive_sqlite]]
        database_name = :memory:
        database_type = SQLite

[DatabaseTypes]
    [[SQLite]]
        driver = weedb.sqlite
        # Directory in which database files are located, relative to WEEWX_ROOT
        SQLITE_ROOT = archive

[Engine]
    [[Services]]
        prep_services = weewx.engine.StdTimeSynch
        data_services = user.mqttsubscribe.MQTTSubscribeService
        process_services = weewx.engine.StdConvert, weewx.engine.StdCalibrate, weewx.engine.StdQC, weewx.wxservices.StdWXCalculate
        xtype_services = weewx.wxxtypes.StdWXXTypes, weewx.wxxtypes.StdPressureCooker, weewx.wxxtypes.StdRainRater, weewx.wxxtypes.StdDelta
        archive_services = weewx.engine.StdArchive
        restful_services = weewx.restx.StdStationRegistry, weewx.restx.StdWunderground, weewx.restx.StdPWSweather, weewx.restx.StdCWOP, weewx.restx.StdWOW, weewx.restx.StdAWEKAS
        report_services = weewx.engine.StdReport

[MQTTSubscribeService]
    [[topics]]
        [[[message]]]
            type = individual
        [[[{helpers.random_string()}]]]
            ignore_start_time = True # at least while developing
            ignore_end_time = True # at least while developing
            adjust_start_time = 1 # at least while developing
            [[[[outTemp]]]]
                name = outTemp
                expires_after = 0

""" # noqa


@contextlib.contextmanager
def engine_with_cache(max_archive_records, simulator_options=None, topic=None):
    """ Build a simulator engine with a mocked RecordCache; yield (engine, cache). """
    with mock.patch('user.mqttsubscribe.RecordCache') as mock_cache:
        config = configobj.ConfigObj(StringIO(config_dict))
        config['Simulator']['max_archive_records'] = max_archive_records
        for option, value in (simulator_options or {}).items():
            config['Simulator'][option] = value
        if topic:
            config['MQTTSubscribeService']['topics'][topic] = {}
        yield weewx.engine.StdEngine(config), mock_cache.return_value


def assert_loop_count(test_case, engine, mock_cache_instance):
    """ Every loop packet must invalidate the cached observation. """
    mock_cache_instance.invalidate_value.assert_called()
    test_case.assertEqual(mock_cache_instance.invalidate_value.call_count, engine.console.count_loop_packets)


class test_record_cache(unittest.TestCase):
    def test_new_loop_packet(self):
        with engine_with_cache(0, topic=helpers.random_string()) as (SUT, mock_cache_instance):
            with self.assertRaises(Exception):
                SUT.run()
                print("exception")

            assert_loop_count(self, SUT, mock_cache_instance)

    def test_observation_not_in_archive_record(self):
        max_archive_records = 1
        options = {'remove_fields_from_archive_record': 'outTemp'}
        with engine_with_cache(max_archive_records, simulator_options=options) as (SUT, mock_cache_instance):
            mock_cache_instance.get_value.return_value = 0

            with self.assertRaises(Exception):
                SUT.run()
                print("exception")

            assert_loop_count(self, SUT, mock_cache_instance)

            mock_cache_instance.update_value.assert_not_called()

            mock_cache_instance.get_value.assert_called()
            self.assertEqual(mock_cache_instance.get_value.call_count, max_archive_records)

    def test_observation_in_archive_record(self):
        max_archive_records = 1
        with engine_with_cache(max_archive_records) as (SUT, mock_cache_instance):
            with self.assertRaises(Exception):
                SUT.run()

            assert_loop_count(self, SUT, mock_cache_instance)

            mock_cache_instance.update_value.assert_called()
            self.assertEqual(mock_cache_instance.update_value.call_count, max_archive_records)

            mock_cache_instance.get_value.assert_not_called()


if __name__ == '__main__':
    helpers.run_tests()
