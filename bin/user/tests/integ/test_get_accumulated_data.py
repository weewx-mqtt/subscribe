#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import helpers
import time
import unittest
import configobj

import utils

import weewx
from user.mqttsubscribe import TopicManager, create_logger as Logger

class TestAccumulatedData(unittest.TestCase):
    def runit(self, payload, file_pointer, check_results=True):
        config_text, testruns = utils.load_test_data(file_pointer)
        config_dict = configobj.ConfigObj(config_text)['MQTTSubscribeService']

        logger = Logger('IntegTest')
        topics_dict = config_dict.get('topics', {})
        manager = TopicManager(None, topics_dict, logger)

        unit_system_name = topics_dict.get('unit_system', 'US').strip().upper()
        if unit_system_name not in weewx.units.unit_constants:
            raise ValueError(f"Unknown unit system, {unit_system_name}.")
        unit_system = weewx.units.unit_constants[unit_system_name]

        on_message = utils.get_callback(payload, config_dict, manager, logger)
        for testrun in testruns:
            start_ts = time.time()
            for topics in testrun['messages']:
                for topic in topics:
                    topic_info = topics[topic]
                    utils.send_msg(utils.send_direct_msg, payload, on_message, topic, topic_info)

            end_ts = time.time()
            records = []
            for queue in sorted(manager.queues, key=lambda i: i['name']):  # todo - dependent on topic names - not great
                data = manager.get_accumulated_data(queue, start_ts, end_ts, unit_system)
                records.append(data)

            if check_results:
                result = utils.find_expected_result(self, testrun, payload, 'accumulate')

                utils.check(self, payload, records, result['records'])
            else:
                for record in records:
                    print(record)

class TestAccumulatedRain(TestAccumulatedData):
    # @unittest.skip("")
    def test_accumulatedrain_individual(self):
        # At WeeWX 4.6.1, the handling of 'sum' accumulators changed.
        # In prior versions if there was no data a 0 was returned. Now None isvreturned.
        utils.run_data_file(self, 'individual', 'accumulatedrain.json')

    # @unittest.skip("")
    def test_accumulatedrain_json(self):
        utils.run_data_file(self, 'json', 'accumulatedrain.json')

    # @unittest.skip("")
    def test_accumulatedrain_keyword(self):
        utils.run_data_file(self, 'keyword', 'accumulatedrain.json')

class TestBasic(TestAccumulatedData):
    # @unittest.skip("")
    def test_basic_individual(self):
        utils.run_data_file(self, 'individual', 'basic.json')

    # @unittest.skip("")
    def test_basic_json(self):
        utils.run_data_file(self, 'json', 'basic.json')

    # @unittest.skip("")
    def test_basic_keyword(self):
        utils.run_data_file(self, 'keyword', 'basic.json')

class TestEmpty(TestAccumulatedData):
    # @unittest.skip("")
    def test_empty_individual(self):
        utils.run_data_file(self, 'individual', 'empty.json')

    # @unittest.skip("")
    def test_empty_json(self):
        utils.run_data_file(self, 'json', 'empty.json')

    # @unittest.skip("")
    def test_empty_keyword(self):
        utils.run_data_file(self, 'keyword', 'empty.json')

class TestWindIndividualTopics(TestAccumulatedData):
    # @unittest.skip("")
    def test_wind_individual_topic(self):
        utils.run_data_file(self, 'individual', 'wind-individual.json')

class TestWind(TestAccumulatedData):
    # @unittest.skip("")
    def test_wind_individual(self):
        utils.run_data_file(self, 'individual', 'wind.json')

    # @unittest.skip("")
    def test_wind_json(self):
        utils.run_data_file(self, 'json', 'wind.json')

    # @unittest.skip("")
    def test_wind_keyword(self):
        utils.run_data_file(self, 'keyword', 'wind.json')

if __name__ == '__main__':
    helpers.run_tests()
