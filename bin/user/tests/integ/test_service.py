#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import helpers
import shutil
import time
import unittest
import configobj

import utils

import weewx
from weewx.engine import StdEngine
from user.mqttsubscribe import MQTTSubscribeService

@unittest.skipUnless(shutil.which('mosquitto'), 'mosquitto is not installed.')
class TestService(unittest.TestCase):
    def setUp(self):
        self.broker = utils.MosquittoBroker()
        self.broker.start()
        self.addCleanup(self.broker.cleanup)

    def runit(self, payload, file_pointer, check_results=True):
        config_text, testruns = utils.load_test_data(file_pointer)

        config_dict = configobj.ConfigObj(config_text)

        cdict = config_dict['MQTTSubscribeService']
        cdict['host'] = utils.BROKER_HOST
        cdict['port'] = self.broker.port
        if 'message_callback' not in config_dict['MQTTSubscribeService']:
            config_dict['MQTTSubscribeService']['message_callback'] = {}
        config_dict['MQTTSubscribeService']['message_callback']['type'] = payload

        unit_system_name = cdict['topics'].get('unit_system', 'US').strip().upper()
        if unit_system_name not in weewx.units.unit_constants:
            raise ValueError(f"Unknown unit system, {unit_system_name}.")
        unit_system = weewx.units.unit_constants[unit_system_name]

        min_config_dict = utils.create_min_weewx_config()

        engine = StdEngine(min_config_dict)
        service = MQTTSubscribeService(engine, config_dict)

        host = utils.BROKER_HOST
        port = self.broker.port
        keepalive = 60

        userdata = {
            'topics': [],
            'connected_flag': False,
        }

        client = utils.create_paho_client(userdata, host, port, keepalive)
        utils.wait_for_connected(self, userdata, "Timed out waiting for connections.")

        userdata2 = {
            'topics': cdict['topics'].sections,
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
                    utils.wait_on_queue(service, msg_count, max_waits, 1)

            record = {}
            interval = 300
            current_time = int(time.time() + 0.5)
            end_period_ts = (int(current_time / interval) + 1) * interval

            record['dateTime'] = end_period_ts
            record['usUnits'] = unit_system
            new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET, packet=record)
            service.new_loop_packet(new_loop_packet_event)

            records = [record]

            if check_results:
                result = utils.find_expected_result(self, testrun, payload, 'service')

                utils.check(self, payload, records, result['records'])
            else:
                for record in records:
                    print(record)

        service.shutDown()
        client.disconnect()
        client2.disconnect()

class TestAccumulatedRain(TestService):
    # @unittest.skip("")
    def test_accumulatedrain_individual(self):
        # At WeeWX 4.6.1, the handling of 'sum' accumulators changed.
        # In prior versions if there was no data a 0 was returned. Now None is returned.
        with open("bin/user/tests/integ/data/accumulatedrain.json", encoding="UTF-8") as file_pointer:
            self.runit('individual', file_pointer)

    # @unittest.skip("")
    def test_accumulatedrain_json(self):
        with open("bin/user/tests/integ/data/accumulatedrain.json", encoding="UTF-8") as file_pointer:
            self.runit('json', file_pointer)

    # @unittest.skip("")
    def test_accumulatedrain_keyword(self):
        with open("bin/user/tests/integ/data/accumulatedrain.json", encoding="UTF-8") as file_pointer:
            self.runit('keyword', file_pointer)

class TestBasic(TestService):
    # @unittest.skip("")
    def test_basic_individual(self):
        with open("bin/user/tests/integ/data/basic.json", encoding="UTF-8") as file_pointer:
            self.runit('individual', file_pointer)

    # @unittest.skip("")
    def test_basic_json(self):
        with open("bin/user/tests/integ/data/basic.json", encoding="UTF-8") as file_pointer:
            self.runit('json', file_pointer)

    # @unittest.skip("")
    def test_basic_keyword(self):
        with open("bin/user/tests/integ/data/basic.json", encoding="UTF-8") as file_pointer:
            self.runit('keyword', file_pointer)

class TestEmpty(TestService):
    # @unittest.skip("")
    def test_empty_individual(self):
        with open("bin/user/tests/integ/data/empty.json", encoding="UTF-8") as file_pointer:
            self.runit('individual', file_pointer)

    # @unittest.skip("")
    def test_empty_json(self):
        with open("bin/user/tests/integ/data/empty.json", encoding="UTF-8") as file_pointer:
            self.runit('json', file_pointer)

    # @unittest.skip("")
    def test_empty_keyword(self):
        with open("bin/user/tests/integ/data/empty.json", encoding="UTF-8") as file_pointer:
            self.runit('keyword', file_pointer)

class TestWindIndividualTopics(TestService):
    # @unittest.skip("")
    def test_wind_individual_topic(self):
        with open("bin/user/tests/integ/data/wind-individual.json", encoding="UTF-8") as file_pointer:
            self.runit('individual', file_pointer)

class TestWind(TestService):
    # @unittest.skip("")
    def test_wind_individual(self):
        with open("bin/user/tests/integ/data/wind.json", encoding="UTF-8") as file_pointer:
            self.runit('individual', file_pointer)

    # @unittest.skip("")
    def test_wind_json(self):
        with open("bin/user/tests/integ/data/wind.json", encoding="UTF-8") as file_pointer:
            self.runit('json', file_pointer)

    # @unittest.skip("")
    def test_wind_keyword(self):
        with open("bin/user/tests/integ/data/wind.json", encoding="UTF-8") as file_pointer:
            self.runit('keyword', file_pointer)

if __name__ == '__main__':
    helpers.run_tests()
