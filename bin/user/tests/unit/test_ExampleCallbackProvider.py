#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import helpers
import mock

import random
import xml.etree

import test_weewx_stubs
from test_weewx_stubs import random_ascii_letters, BaseTestClass
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

from user.mqttcommon import Logger
from user.ExampleMessageCallbackProvider import MessageCallbackProvider
from user.tests.message_helpers import create_message

class Test1(BaseTestClass):
    @staticmethod
    def create_observation_dict(size):
        observation_dict = {}

        i = 0
        while i < size:
            observation_dict[random_ascii_letters()] = round(random.uniform(101, 200), 2)
            i += 1

        return observation_dict

    @staticmethod
    def create_observation_xml(parent, observation_dict):
        xml_element = xml.etree.ElementTree.Element(parent)
        for key, value in observation_dict.items():
            child = xml.etree.ElementTree.Element(key)
            child.text = str(value)
            xml_element.append(child)
        return xml_element

    def test_get_observations(self):
        observation_dict = self.create_observation_dict(5)
        root = self.create_observation_xml('observations', observation_dict)

        SUT = MessageCallbackProvider({}, None, None)

        results = SUT.get_observations("topic", root, "", {}, 1)

        self.assertDictEqual(observation_dict, results)

    def test_on_message(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock()
        mock_manager.get_fields.return_value = {}

        observation_dict = self.create_observation_dict(5)
        root = self.create_observation_xml('observations', observation_dict)
        xml_string = xml.etree.ElementTree.tostring(root)
        msg = create_message("topic", xml_string, 0, 0)

        SUT = MessageCallbackProvider({}, mock_logger, mock_manager)

        SUT._on_message(msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, observation_dict)

if __name__ == '__main__':
    helpers.run_tests()
