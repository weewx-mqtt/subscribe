#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import helpers
import shutil
import unittest

import configobj

import utils

import weewx

from user.mqttsubscribe import MQTTSubscribeDriver

@unittest.skipUnless(shutil.which('mosquitto'), 'mosquitto is not installed.')
class TestDriver(unittest.TestCase):
    def setUp(self):
        self.broker = utils.MosquittoBroker()
        self.broker.start()
        self.addCleanup(self.broker.cleanup)

    def runit(self, payload, file_pointer, check_results=True):
        config_text, testruns = utils.load_test_data(file_pointer)

        config_dict = configobj.ConfigObj(config_text)

        stndict = config_dict['MQTTSubscribeService']
        if 'message_callback' not in config_dict['MQTTSubscribeService']:
            config_dict['MQTTSubscribeService']['message_callback'] = {}
        config_dict['MQTTSubscribeService']['message_callback']['type'] = payload

        cdict = {'MQTTSubscribeDriver': stndict}
        stndict['host'] = utils.BROKER_HOST
        stndict['port'] = self.broker.port

        min_config_dict = utils.create_min_weewx_config()

        engine = weewx.engine.StdEngine(min_config_dict)
        driver = MQTTSubscribeDriver(cdict, engine)

        host = utils.BROKER_HOST
        port = self.broker.port
        keepalive = 60

        userdata = {
            'topics': [],
            'connected_flag': False
        }

        client = utils.create_paho_client(userdata, host, port, keepalive)
        utils.wait_for_connected(self, userdata, "Timed out waiting for connections.")

        userdata2 = {
            'topics': stndict['topics'].sections,
            'connected_flag': False,
            'msg': False,
            'max_msg_wait': 1  # ToDo - configure
        }

        client2 = utils.create_paho_client(userdata2, host, port, keepalive)
        client2.on_message = utils.on_message
        utils.wait_for_connected(self, userdata2, "Timed out waiting for connection 2.")

        max_waits = 10
        for testrun in testruns:
            for topics in testrun['messages']:
                for topic in topics:
                    topic_info = topics[topic]
                    msg_count = utils.send_msg(utils.send_mqtt_msg, payload, client.publish, topic, topic_info, userdata2, self)
                    wait_count = utils.wait_on_queue(driver, msg_count, max_waits, 1)

                    # If queue not filled, fail now
                    # otherwise will end up in 'infinite' loop in genLoopPackets
                    if wait_count >= max_waits:
                        self.fail("Could not fill queue.")

            records = []
            gen = driver.genLoopPackets()

            more_data = False
            # hack to check if there is more data in the queues
            for topics in testrun['messages']:
                for topic in driver.subscriber.manager.subscribed_topics:
                    if driver.subscriber.manager.has_data(topic):
                        more_data = True

            while more_data:
                data = next(gen, None)
                records.append(data)
                more_data = False
                # hack to check if there is more data in the queues
                for topics in testrun['messages']:
                    for topic in driver.subscriber.manager.subscribed_topics:
                        if driver.subscriber.manager.has_data(topic):
                            more_data = True

            if check_results:
                result = utils.find_expected_result(self, testrun, payload, 'driver')

                utils.check(self, payload, records, result['records'])
            else:
                for record in records:
                    print(record)

        driver.closePort()
        client.disconnect()
        client2.disconnect()

class TestAccumulatedRain(TestDriver):
    # @unittest.skip("")
    def test_accumulatedrain_individual(self):
        utils.run_data_file(self, 'individual', 'accumulatedrain.json')

    # @unittest.skip("")
    def test_accumulatedrain_json(self):
        utils.run_data_file(self, 'json', 'accumulatedrain.json')

    # @unittest.skip("")
    def test_accumulatedrain_keyword(self):
        utils.run_data_file(self, 'keyword', 'accumulatedrain.json')

class TestBasic(TestDriver):
    # @unittest.skip("")
    def test_basic_individual(self):
        utils.run_data_file(self, 'individual', 'basic.json')

    # @unittest.skip("")
    def test_basic_json(self):
        utils.run_data_file(self, 'json', 'basic.json')

    # @unittest.skip("")
    def test_basic_keyword(self):
        utils.run_data_file(self, 'keyword', 'basic.json')

class TestEmpty(TestDriver):
    # @unittest.skip("")
    def test_empty_individual(self):
        utils.run_data_file(self, 'individual', 'empty.json')

    # @unittest.skip("")
    def test_empty_json(self):
        utils.run_data_file(self, 'json', 'empty.json')

    # @unittest.skip("")
    def test_empty_keyword(self):
        utils.run_data_file(self, 'keyword', 'empty.json')

class TestWindIndividualTopics(TestDriver):
    # @unittest.skip("")
    def test_wind_individual_topic(self):
        utils.run_data_file(self, 'individual', 'wind-individual.json')

class TestWindIndividualWind(TestDriver):
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
