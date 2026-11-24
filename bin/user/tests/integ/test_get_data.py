#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import helpers
import unittest
import configobj

import utils

from user.mqttsubscribe import TopicManager, create_logger as Logger

class TestGetData(unittest.TestCase):
    def runit(self, payload, file_pointer, check_results=True):
        config_text, testruns = utils.load_test_data(file_pointer)
        config_dict = configobj.ConfigObj(config_text)['MQTTSubscribeService']

        logger = Logger('IntegTest')
        topics_dict = config_dict.get('topics', {})
        manager = TopicManager(None, topics_dict, logger)

        on_message = utils.get_callback(payload, config_dict, manager, logger)

        for testrun in testruns:
            for topics in testrun['messages']:
                for topic in topics:
                    topic_info = topics[topic]
                    utils.send_msg(utils.send_direct_msg, payload, on_message, topic, topic_info)

            records = []
            for queue in manager.queues:
                for data in manager.get_data(queue):
                    if data:
                        records.append(data)
                    else:
                        break

            if check_results:
                result = utils.find_expected_result(self, testrun, payload, 'single')

                utils.check(self, payload, records, result['records'])
            else:
                for record in records:
                    print(record)

class TestAccumulatedRain(TestGetData):
    # @unittest.skip("")
    def test_accumulatedrain_individual(self):
        utils.run_data_file(self, 'individual', 'accumulatedrain.json')

    # @unittest.skip("")
    def test_accumulatedrain_json(self):
        utils.run_data_file(self, 'json', 'accumulatedrain.json')

    # @unittest.skip("")
    def test_accumulatedrain_keyword(self):
        utils.run_data_file(self, 'keyword', 'accumulatedrain.json')

class TestBasic(TestGetData):
    # @unittest.skip("")
    def test_basic_individual(self):
        utils.run_data_file(self, 'individual', 'basic.json')

    # @unittest.skip("")
    def test_basic_json(self):
        utils.run_data_file(self, 'json', 'basic.json')

    # @unittest.skip("")
    def test_basic_keyword(self):
        utils.run_data_file(self, 'keyword', 'basic.json')

class TestEmpty(TestGetData):
    # @unittest.skip("")
    def test_empty_individual(self):
        utils.run_data_file(self, 'individual', 'empty.json')

    # @unittest.skip("")
    def test_empty_json(self):
        utils.run_data_file(self, 'json', 'empty.json')

    # @unittest.skip("")
    def test_empty_keyword(self):
        utils.run_data_file(self, 'keyword', 'empty.json')

class TestIndividualWindTopics(TestGetData):
    # @unittest.skip("")
    def test_wind_individual_topic(self):
        utils.run_data_file(self, 'individual', 'wind-individual.json')

class TestWind(TestGetData):
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
