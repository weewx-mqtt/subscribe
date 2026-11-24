#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import helpers
import unittest
import mock

import configobj
import copy
import json
import random
import time

import test_weewx_stubs
from test_weewx_stubs import random_string, BaseTestClass
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

import user.mqttsubscribe
from user.mqttcommon import Logger
from user.mqttsubscribe import TopicManager
from user.tests.message_helpers import create_message

# todo - mock?
def to_float(x):
    if isinstance(x, str) and x.lower() == 'none':
        x = None
    return float(x) if x is not None else None


def create_topic_config(message_dict=None, fields=None, **kwargs):
    ''' Build a resolved topic config for mocking TopicManager.get_topic_config. '''
    config = {
        'message': message_dict if message_dict is not None else {'type': 'individual'},
        'fields': fields if fields is not None else {},
        'ignore': False,
        'conversion_func': {
            'source': 'lambda x: to_float(x)',
            'compiled': eval('lambda x: to_float(x)')  # nosec B307 - example expression pylint: disable=eval-used
        },
        'unit_system': 1,
        'filters': {},
        'msg_id_field': None,
        'fields_ignoring_msg_id': [],
    }
    config.update(kwargs)
    return config


def create_provider(topic_config, handler_config):
    """ Build the provider under test plus its logger and manager mocks. """
    mock_logger = mock.Mock(spec=Logger)
    mock_manager = mock.Mock(spec=TopicManager)
    mock_manager.get_topic_config.return_value = topic_config
    mock_manager.message_config_name = 'message'
    mock_manager.subscribed_topics = {}
    sut = user.mqttsubscribe.MessageCallbackProvider(configobj.ConfigObj(handler_config), mock_logger, mock_manager)
    return sut, mock_logger, mock_manager


def create_subscribed_topics(topic, message_config_name, queue_type):
    """ Build the subscribed_topics shape TopicManager hands to the provider at init time. """
    return {
        topic: {
            'queue': {'type': queue_type},
            message_config_name: {},
        }
    }


def create_keyword_payload(payload_dict):
    """ Serialize an observation dict into the keyword wire format. """
    payload_str = ""
    delim = ""
    for key, value in payload_dict.items():
        payload_str = f"{payload_str}{delim}{key}={value:f}"
        delim = ","
    return payload_str.encode('UTF-8')


def create_payload_dict(base, date_time=None, us_units=None, **extra):
    """ Build an observation dict, omitting keys the caller leaves out. """
    payload_dict = dict(base)
    if date_time is not None:
        payload_dict['dateTime'] = date_time
    if us_units is not None:
        payload_dict['usUnits'] = us_units
    payload_dict.update(extra)
    return payload_dict


def assert_str_keys(test_case, mock_manager):
    """ Assert that every field name produced by the handler is a string. """
    call_args_list = mock_manager.append_data.call_args_list
    second_arg = call_args_list[0].args[1]
    for key in second_arg:
        test_case.assertIsInstance(key, str)


class TestInitialization(BaseTestClass):
    @staticmethod
    def test_message_and_message_callback_set():
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        topic = random_string(10)
        message_config_name = random_string()
        queue_type = random_string(10)
        mock_manager.message_config_name = message_config_name
        mock_manager.subscribed_topics = create_subscribed_topics(topic, message_config_name, queue_type)
        mock_manager.subscribed_topics[topic][message_config_name]['type'] = 'json'

        config_dict = {}
        config_dict['type'] = 'barbar'
        config = configobj.ConfigObj(config_dict)

        user.mqttsubscribe.MessageCallbackProvider(config, mock_logger, mock_manager)

        mock_logger.info.assert_called_once_with(42001,
                                                 ("Message configuration found under "
                                                  "[[MessageCallback]] and [[Topic]]. Ignoring [[MessageCallback]]."))

    def test_message_and_message_callback_not_set(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        topic = random_string(10)
        message_config_name = random_string()
        queue_type = random_string(10)
        mock_manager.message_config_name = message_config_name
        mock_manager.subscribed_topics = create_subscribed_topics(topic, message_config_name, queue_type)

        with self.assertRaises(ValueError) as error:
            user.mqttsubscribe.MessageCallbackProvider(None, mock_logger, mock_manager)

        self.assertEqual(error.exception.args[0], f"Topic {topic} is missing its '[[[[message]]]]' section.")

    def test_message_callback_configuration_defaults_not_set(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        topic = random_string(10)
        message_config_name = random_string()
        queue_type = random_string(10)
        flatten_delimiter = random_string(5)
        keyword_delimiter = random_string(5)
        keyword_separator = random_string(5)
        mock_manager.message_config_name = message_config_name
        mock_manager.subscribed_topics = create_subscribed_topics(topic, message_config_name, queue_type)

        config_dict = {}
        config_dict['type'] = 'json'
        config_dict['flatten_delimiter'] = flatten_delimiter
        config_dict['keyword_delimiter'] = keyword_delimiter
        config_dict['keyword_separator'] = keyword_separator
        config = configobj.ConfigObj(config_dict)

        user.mqttsubscribe.MessageCallbackProvider(config, mock_logger, mock_manager)

        self.assertEqual(mock_manager.subscribed_topics[topic][message_config_name]['flatten_delimiter'], flatten_delimiter)
        self.assertEqual(mock_manager.subscribed_topics[topic][message_config_name]['keyword_delimiter'], keyword_delimiter)
        self.assertEqual(mock_manager.subscribed_topics[topic][message_config_name]['keyword_separator'], keyword_separator)

    def test_message_configuration_defaults_set(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        topic = random_string(10)
        message_config_name = random_string()
        queue_type = random_string(10)
        flatten_delimiter = random_string(5)
        keyword_delimiter = random_string(5)
        keyword_separator = random_string(5)
        mock_manager.message_config_name = message_config_name
        mock_manager.subscribed_topics = create_subscribed_topics(topic, message_config_name, queue_type)
        mock_manager.subscribed_topics[topic][message_config_name]['type'] = 'json'
        mock_manager.subscribed_topics[topic][message_config_name]['flatten_delimiter'] = flatten_delimiter
        mock_manager.subscribed_topics[topic][message_config_name]['keyword_delimiter'] = keyword_delimiter
        mock_manager.subscribed_topics[topic][message_config_name]['keyword_separator'] = keyword_separator

        user.mqttsubscribe.MessageCallbackProvider(None, mock_logger, mock_manager)

        self.assertEqual(mock_manager.subscribed_topics[topic][message_config_name]['flatten_delimiter'], flatten_delimiter)
        self.assertEqual(mock_manager.subscribed_topics[topic][message_config_name]['keyword_delimiter'], keyword_delimiter)
        self.assertEqual(mock_manager.subscribed_topics[topic][message_config_name]['keyword_separator'], keyword_separator)

    def test_message_configuration_defaults_not_set(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        topic = random_string(10)
        message_config_name = random_string()
        queue_type = random_string(10)
        mock_manager.message_config_name = message_config_name
        mock_manager.subscribed_topics = create_subscribed_topics(topic, message_config_name, queue_type)
        mock_manager.subscribed_topics[topic][message_config_name]['type'] = 'json'

        user.mqttsubscribe.MessageCallbackProvider(None, mock_logger, mock_manager)

        self.assertEqual(mock_manager.subscribed_topics[topic][message_config_name]['flatten_delimiter'], '_')
        self.assertEqual(mock_manager.subscribed_topics[topic][message_config_name]['keyword_delimiter'], ',')
        self.assertEqual(mock_manager.subscribed_topics[topic][message_config_name]['keyword_separator'], '=')

    def test_message_configuration_invalid_type(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        topic = random_string(10)
        message_config_name = random_string()
        queue_type = random_string(10)
        message_type = random_string(10)
        mock_manager.message_config_name = message_config_name
        mock_manager.subscribed_topics = create_subscribed_topics(topic, message_config_name, queue_type)
        mock_manager.subscribed_topics[topic][message_config_name]['type'] = message_type

        with self.assertRaises(ValueError) as error:
            user.mqttsubscribe.MessageCallbackProvider(None, mock_logger, mock_manager)

        self.assertEqual(error.exception.args[0], f"Invalid type, {message_type}.")

    def test_message_configuration_missing_type(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        topic = random_string(10)
        message_config_name = random_string()
        queue_type = random_string(10)
        config_option = random_string(10)
        config_value = random_string(10)
        mock_manager.message_config_name = message_config_name
        mock_manager.subscribed_topics = create_subscribed_topics(topic, message_config_name, queue_type)
        mock_manager.subscribed_topics[topic][message_config_name][config_option] = config_value

        with self.assertRaises(ValueError) as error:
            user.mqttsubscribe.MessageCallbackProvider(None, mock_logger, mock_manager)

        self.assertEqual(error.exception.args[0], f"Topic {topic} is missing its '[[[[message]]]] type=' section.")

# missing message section? todo
class TestMultiMessageMethod(BaseTestClass):
    @staticmethod
    def test_invalid_type():
        type = random_string()

        topic_config = {'message': {'type': type}}
        config_dict = {}

        SUT, mock_logger, _ = create_provider(topic_config, config_dict)

        payload = random_string()
        payload = payload.encode('UTF-8')
        topic = random_string()

        msg = create_message(topic, payload, 0, 0)

        SUT.on_message_multi(msg)
        mock_logger.error.assert_called_with(44010, f"Unknown message_type={type}. Skipping topic={topic} and payload={payload}.")

    def test_exception_raised(self):
        traceback = random_string()
        user.mqttsubscribe.traceback.format_exc = mock.Mock(return_value=traceback)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)
        mock_manager.get_topic_config = mock.Mock(side_effect=Exception("done"))

        mock_manager.subscribed_topics = {}

        config_dict = {}
        config = configobj.ConfigObj(config_dict)

        SUT = user.mqttsubscribe.MessageCallbackProvider(config, mock_logger, mock_manager)

        payload = random_string()
        payload = payload.encode('UTF-8')
        topic = random_string()

        msg = create_message(topic, payload, 0, 0)

        SUT.on_message_multi(msg)
        self.assertEqual(mock_logger.error.call_count, 3)
        mock_logger.error.assert_has_calls([
            mock.call(44004, "MessageCallbackProvider on_message_multi failed with <class 'Exception'> and reason done."),
            mock.call(44005, f"**** MessageCallbackProvider ignoring topic={topic} and payload={payload}."),
            mock.call(44006, f"**** MessageCallbackProvider {traceback}")
        ])

class TestKeywordload(unittest.TestCase):
    topic = random_string()

    payload_dict = {
        'inTemp': round(random.uniform(10, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config_dict = {}
    message_handler_config_dict['type'] = 'keyword'

    def test_payload_empty(self):
        topic_config = create_topic_config(
            {'type': 'keyword', 'keyword_delimiter': ',', 'keyword_separator': '='})

        SUT, mock_logger, _ = create_provider(topic_config, self.message_handler_config_dict)

        payload = ''
        payload = payload.encode('UTF-8')

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)
        self.assertEqual(mock_logger.error.call_count, 3)

    def test_payload_bad_data(self):
        topic_config = create_topic_config(
            {'type': 'keyword', 'keyword_delimiter': ',', 'keyword_separator': '='}, fields={})

        SUT, mock_logger, _ = create_provider(topic_config, self.message_handler_config_dict)

        payload = 'field=value'
        payload = payload.encode("utf-8")

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)
        self.assertEqual(mock_logger.error.call_count, 3)

    def test_payload_missing_delimiter(self):
        topic_config = create_topic_config(
            {'type': 'keyword', 'keyword_delimiter': ',', 'keyword_separator': '='}, fields={})

        SUT, mock_logger, _ = create_provider(topic_config, self.message_handler_config_dict)

        payload = 'field1=1 field2=2'
        payload = payload.encode("utf-8")

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)
        self.assertEqual(mock_logger.error.call_count, 3)

    def test_payload_missing_separator(self):
        topic_config = create_topic_config(
            {'type': 'keyword', 'keyword_delimiter': ',', 'keyword_separator': '='}, fields={})

        SUT, mock_logger, _ = create_provider(topic_config, self.message_handler_config_dict)

        payload = ' field:1'
        payload = payload.encode('UTF-8')

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)
        self.assertEqual(mock_logger.error.call_count, 3)

    def test_payload_missing_dateTime(self):
        topic_config = create_topic_config(
            {'type': 'keyword', 'keyword_delimiter': ',', 'keyword_separator': '='}, fields={})
        SUT, _, mock_manager = create_provider(topic_config, self.message_handler_config_dict)

        payload_dict = create_payload_dict(self.payload_dict, us_units=random.randint(1, 10))

        payload_str = create_keyword_payload(payload_dict)

        msg = create_message(self.topic, payload_str, 0, 0)

        SUT.on_message_multi(msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)

    def test_payload_missing_units(self):
        topic_config = create_topic_config(
            {'type': 'keyword', 'keyword_delimiter': ',', 'keyword_separator': '='}, fields={})
        SUT, _, mock_manager = create_provider(topic_config, self.message_handler_config_dict)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = round(time.time(), 2)

        payload_str = create_keyword_payload(payload_dict)

        msg = create_message(self.topic, payload_str, 0, 0)

        SUT.on_message_multi(msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)

    def test_payload_good(self):
        topic_config = create_topic_config(
            {'type': 'keyword', 'keyword_delimiter': ',', 'keyword_separator': '='}, fields={})
        SUT, _, mock_manager = create_provider(topic_config, self.message_handler_config_dict)

        payload_dict = create_payload_dict(self.payload_dict, round(time.time(), 2), random.randint(1, 10))

        payload_str = create_keyword_payload(payload_dict)

        msg = create_message(self.topic, payload_str, 0, 0)

        SUT.on_message_multi(msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)

    def test_ignore_default_true(self):
        topic_config = create_topic_config(
            {'type': 'keyword', 'keyword_delimiter': ',', 'keyword_separator': '='}, ignore=True)

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'keyword'

        fields = {}
        fields['ignore'] = True

        message_handler_config_dict['fields'] = fields

        SUT, _, mock_manager = create_provider(topic_config, message_handler_config_dict)

        payload_dict = create_payload_dict(self.payload_dict, round(time.time(), 2), random.randint(1, 10))

        payload_str = create_keyword_payload(payload_dict)

        msg = create_message(self.topic, payload_str, 0, 0)

        SUT.on_message_multi(msg)
        self.assertFalse(mock_manager.append_data.called)

    def test_ignore_default_true_ignore_field_false(self):
        topic_config = create_topic_config(
            {'type': 'keyword', 'keyword_delimiter': ',', 'keyword_separator': '='}, fields={})
        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'keyword'

        fields = {}
        fields['ignore'] = True

        field = {}
        field['ignore'] = False
        fields['dateTime'] = field

        field = {}
        field['ignore'] = False
        fields['usUnits'] = field

        message_handler_config_dict['fields'] = fields
        topic_config['fields'] = fields

        SUT, _, mock_manager = create_provider(topic_config, message_handler_config_dict)

        payload_dict = {}
        payload_dict['dateTime'] = round(time.time(), 2)
        payload_dict['usUnits'] = random.randint(1, 10)

        payload_str = create_keyword_payload(payload_dict)

        msg = create_message(self.topic, payload_str, 0, 0)

        SUT.on_message_multi(msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)

    def test_ignore_field_true(self):
        topic_config = create_topic_config(
            {'type': 'keyword', 'keyword_delimiter': ',', 'keyword_separator': '='}, fields={})
        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'keyword'

        fields = {}

        field = {}
        field['ignore'] = True
        fields['inTemp'] = field

        message_handler_config_dict['fields'] = fields
        topic_config['fields'] = fields

        SUT, _, mock_manager = create_provider(topic_config, message_handler_config_dict)

        payload_dict = {}
        payload_dict['outTemp'] = self.payload_dict['outTemp']
        payload_dict['dateTime'] = round(time.time(), 2)
        payload_dict['usUnits'] = random.randint(1, 10)

        payload_str = create_keyword_payload(payload_dict)

        msg = create_message(self.topic, payload_str, 0, 0)

        SUT.on_message_multi(msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)

class TestJsonPayload(unittest.TestCase):
    topic = random_string()

    payload_dict = {
        'inTemp': round(random.uniform(10, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config_dict = {}
    message_handler_config_dict['type'] = 'json'

    def test_invalid_json(self):
        topic_config = create_topic_config(
            {'type': 'json', 'flatten_delimiter': '_'})

        SUT, mock_logger, _ = create_provider(topic_config, self.message_handler_config_dict)

        msg = create_message(self.topic, random_string())

        SUT.on_message_multi(msg)
        self.assertEqual(mock_logger.error.call_count, 3)

    def test_empty_payload(self):
        topic_config = create_topic_config(
            {'type': 'json', 'flatten_delimiter': '_'})

        SUT, mock_logger, _ = create_provider(topic_config, self.message_handler_config_dict)

        msg = create_message(self.topic, '', 0, 0)

        SUT.on_message_multi(msg)
        self.assertEqual(mock_logger.error.call_count, 3)

    def test_missing_dateTime(self):
        topic_config = create_topic_config(
            {'type': 'json', 'flatten_delimiter': '_'}, fields={}, filters={}, msg_id_field=None, fields_ignoring_msg_id=[])

        SUT, _, mock_manager = create_provider(topic_config, self.message_handler_config_dict)

        payload_dict = create_payload_dict(self.payload_dict, us_units=random.randint(1, 10))

        payload = json.dumps(payload_dict).encode("utf-8")

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)

    def test_missing_units(self):
        topic_config = create_topic_config(
            {'type': 'json', 'flatten_delimiter': '_'}, fields={}, filters={}, msg_id_field=None, fields_ignoring_msg_id=[])

        SUT, _, mock_manager = create_provider(topic_config, self.message_handler_config_dict)

        payload_dict = create_payload_dict(self.payload_dict, time.time())

        payload = json.dumps(payload_dict).encode("utf-8")

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)

    def test_payload_good(self):
        topic_config = create_topic_config(
            {'type': 'json', 'flatten_delimiter': '_'}, fields={}, filters={}, msg_id_field=None, fields_ignoring_msg_id=[])

        SUT, _, mock_manager = create_provider(topic_config, self.message_handler_config_dict)

        payload_dict = create_payload_dict(self.payload_dict, time.time(), random.randint(1, 10))

        payload = json.dumps(payload_dict).encode("utf-8")

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)
        assert_str_keys(self, mock_manager)

    def test_msg_id_set(self):
        msg_id_field = random_string()
        topic_config = create_topic_config(
            {'type': 'json', 'flatten_delimiter': '_'}, fields={}, msg_id_field=msg_id_field, fields_ignoring_msg_id=[])

        SUT, _, mock_manager = create_provider(topic_config, self.message_handler_config_dict)

        payload_dict = create_payload_dict(self.payload_dict, time.time(), random.randint(1, 10))
        msg_id = random.randint(1, 10)
        payload_dict[msg_id_field] = msg_id

        payload = json.dumps(payload_dict).encode("utf-8")

        final_dict = {}
        for key, value in payload_dict.items():
            final_dict[key + '_' + str(msg_id)] = value

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, final_dict)
        assert_str_keys(self, mock_manager)

    def test_ignore_msg_id_field_set(self):
        msg_id_field = random_string()
        topic_config = create_topic_config(
            {'type': 'json', 'flatten_delimiter': '_'}, fields={}, msg_id_field=msg_id_field, fields_ignoring_msg_id=[])

        SUT, _, mock_manager = create_provider(topic_config, self.message_handler_config_dict)

        payload_dict = create_payload_dict(self.payload_dict, time.time(), random.randint(1, 10))
        msg_id = random.randint(1, 10)
        payload_dict[msg_id_field] = msg_id

        payload = json.dumps(payload_dict).encode("utf-8")

        ignore_msg_id_field_fields = [msg_id_field]
        for key in payload_dict:
            if key == msg_id_field:
                continue
            ignore_msg_id_field_fields.append(key)

        topic_config['fields_ignoring_msg_id'] = ignore_msg_id_field_fields

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)
        assert_str_keys(self, mock_manager)

    def test_payload_array_too_large(self):
        topic_config = create_topic_config(
            {'type': 'json', 'flatten_delimiter': '_'}, fields={}, filters={}, msg_id_field=None, fields_ignoring_msg_id=[])

        SUT, _, mock_manager = create_provider(topic_config, self.message_handler_config_dict)

        fields = {}
        fields['extraTemps'] = {}
        fields['extraTemps']['subfields'] = []
        topic_config['fields'] = fields

        payload_dict = create_payload_dict(self.payload_dict, time.time(), random.randint(1, 10))
        output_dict = copy.deepcopy(payload_dict)
        payload_dict['extraTemps'] = [random.randint(1, 10), random.randint(1, 10)]

        payload = json.dumps(payload_dict).encode("utf-8")

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)

        SUT.logger.error.assert_called_once_with(
            44001,
            f"Skipping extraTemps because array data too big. Array={payload_dict['extraTemps']} subfields=[].")
        mock_manager.append_data.assert_called_once_with(msg.topic, output_dict)
        assert_str_keys(self, mock_manager)

    def test_payload_array_too_small(self):
        topic_config = create_topic_config(
            {'type': 'json', 'flatten_delimiter': '_'}, fields={}, filters={}, msg_id_field=None, fields_ignoring_msg_id=[])

        fields = {}
        fields['extraTemps'] = {}
        fields['extraTemps']['subfields'] = ['extraTemp1', 'extraTemp2', 'extraTemp3']
        topic_config['fields'] = fields

        SUT, _, mock_manager = create_provider(topic_config, self.message_handler_config_dict)

        payload_dict = create_payload_dict(self.payload_dict, time.time(), random.randint(1, 10))
        output_dict = copy.deepcopy(payload_dict)
        payload_dict['extraTemps'] = [random.randint(1, 10), random.randint(1, 10)]

        payload = json.dumps(payload_dict).encode("utf-8")

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)

        SUT.logger.error.assert_called_once_with(
            44002,
            f"Skipping extraTemps because array data too small. Array={payload_dict['extraTemps']} "
            f"subfields={fields['extraTemps']['subfields']}.")
        mock_manager.append_data.assert_called_once_with(msg.topic, output_dict)
        assert_str_keys(self, mock_manager)

    def test_payload_array_nit_configured(self):
        topic_config = create_topic_config(
            {'type': 'json', 'flatten_delimiter': '_'}, fields={}, filters={}, msg_id_field=None, fields_ignoring_msg_id=[])

        SUT, mock_logger, _ = create_provider(topic_config, self.message_handler_config_dict)

        fields = {}
        topic_config['fields'] = fields

        payload_dict = create_payload_dict(self.payload_dict, time.time(), random.randint(1, 10))
        output_dict = copy.deepcopy(payload_dict)
        payload_dict['extraTemps'] = [round(random.uniform(1, 100), 2), round(random.uniform(1, 100), 2)]

        payload = json.dumps(payload_dict).encode("utf-8")

        output_dict['extraTemp1'] = payload_dict['extraTemps'][0]
        output_dict['extraTemp2'] = payload_dict['extraTemps'][1]

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)

        self.assertEqual(mock_logger.error.call_count, 1)

    def test_payload_array_good(self):
        topic_config = create_topic_config(
            {'type': 'json', 'flatten_delimiter': '_'}, fields={}, filters={}, msg_id_field=None, fields_ignoring_msg_id=[])

        SUT, _, mock_manager = create_provider(topic_config, self.message_handler_config_dict)

        fields = {}
        fields['extraTemps'] = {}
        fields['extraTemps']['subfields'] = ['extraTemp1', 'extraTemp2']
        fields['extraTemp1'] = {}
        fields['extraTemp2'] = {}
        topic_config['fields'] = fields

        payload_dict = create_payload_dict(self.payload_dict, time.time(), random.randint(1, 10))
        output_dict = copy.deepcopy(payload_dict)
        payload_dict['extraTemps'] = [round(random.uniform(1, 100), 2), round(random.uniform(1, 100), 2)]

        payload = json.dumps(payload_dict).encode("utf-8")

        output_dict['extraTemp1'] = payload_dict['extraTemps'][0]
        output_dict['extraTemp2'] = payload_dict['extraTemps'][1]

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, output_dict)
        assert_str_keys(self, mock_manager)

    def test_payload_nested(self):
        topic_config = create_topic_config(
            {'type': 'json', 'flatten_delimiter': '_'}, fields={}, filters={}, msg_id_field=None, fields_ignoring_msg_id=[])

        SUT, _, mock_manager = create_provider(topic_config, self.message_handler_config_dict)

        payload_dict = {
            'nested01': {
                'inTemp': round(random.uniform(1, 100), 2),
                'outTemp': round(random.uniform(1, 100), 2)
            }
        }

        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        flattened_payload_dict = {
            'nested01_inTemp': payload_dict['nested01']['inTemp'],
            'nested01_outTemp': payload_dict['nested01']['outTemp']
        }
        flattened_payload_dict['dateTime'] = payload_dict['dateTime']
        flattened_payload_dict['usUnits'] = payload_dict['usUnits']

        payload = json.dumps(payload_dict).encode("utf-8")

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, flattened_payload_dict)

    def test_payload_nested_rename(self):
        topic_config = create_topic_config(
            {'type': 'json', 'flatten_delimiter': '_'}, fields={'nested01_inTemp': {'name': 'inTemp'}})

        message_handler_config_dict = copy.deepcopy(self.message_handler_config_dict)
        message_handler_config_dict['fields'] = {}
        message_handler_config_dict['fields']['nested01_inTemp'] = {}
        message_handler_config_dict['fields']['nested01_inTemp']['name'] = 'inTemp'

        SUT, _, mock_manager = create_provider(topic_config, message_handler_config_dict)

        payload_dict = {
            'nested01': {
                'inTemp': round(random.uniform(1, 100), 2),
                'outTemp': round(random.uniform(1, 100), 2)
            }
        }

        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        flattened_payload_dict = {
            'inTemp': payload_dict['nested01']['inTemp'],
            'nested01_outTemp': payload_dict['nested01']['outTemp']
        }
        flattened_payload_dict['dateTime'] = payload_dict['dateTime']
        flattened_payload_dict['usUnits'] = payload_dict['usUnits']

        payload = json.dumps(payload_dict).encode("utf-8")

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, flattened_payload_dict)

    def test_ignore_default_true(self):
        topic_config = create_topic_config(
            {'type': 'json', 'flatten_delimiter': '_'}, fields={}, ignore=True)

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'json'

        fields = {}
        fields['ignore'] = True

        message_handler_config_dict['fields'] = fields

        SUT, _, mock_manager = create_provider(topic_config, message_handler_config_dict)

        payload_dict = create_payload_dict(self.payload_dict, time.time(), random.randint(1, 10))

        payload = json.dumps(payload_dict).encode("utf-8")

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)

        self.assertFalse(mock_manager.append_data.called)

    def test_ignore_default_true_ignore_field_false(self):
        topic_config = create_topic_config(
            {'type': 'json', 'flatten_delimiter': '_'}, fields={}, filters={}, msg_id_field=None, fields_ignoring_msg_id=[])

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'json'

        fields = {}
        fields['ignore'] = True

        field = {}
        field['ignore'] = False
        fields['dateTime'] = field

        field = {}
        field['ignore'] = False
        fields['usUnits'] = field

        message_handler_config_dict['fields'] = fields
        topic_config['fields'] = fields

        SUT, _, mock_manager = create_provider(topic_config, message_handler_config_dict)

        payload_dict = {}
        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        payload = json.dumps(payload_dict).encode("utf-8")

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)
        assert_str_keys(self, mock_manager)

    def test_ignore_field_true(self):
        topic_config = create_topic_config(
            {'type': 'json', 'flatten_delimiter': '_'}, fields={'inTemp': {'ignore': True}})

        SUT, _, mock_manager = create_provider(topic_config, self.message_handler_config_dict)

        payload_dict = {}
        payload_dict['outTemp'] = self.payload_dict['outTemp']
        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        payload = json.dumps(payload_dict).encode("utf-8")

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)
        assert_str_keys(self, mock_manager)

    def test_filter_message(self):
        lookup_key = 'outTemp'
        filters = {lookup_key: [self.payload_dict['outTemp']]}
        topic_config = create_topic_config(
            {'type': 'json', 'flatten_delimiter': '_'}, fields={}, filters=filters)

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'json'

        fields = {}

        field = {}
        field['ignore'] = True
        fields['inTemp'] = field

        message_handler_config_dict['fields'] = fields

        SUT, _, mock_manager = create_provider(topic_config, message_handler_config_dict)

        payload_dict = {}
        payload_dict['outTemp'] = self.payload_dict['outTemp']
        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        payload = json.dumps(payload_dict).encode("utf-8")

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)

        mock_manager.append_data.assert_not_called()
        SUT.logger.info.assert_called_with(42002,
                                           (f"MessageCallbackProvider on_message_json filtered out {msg.topic}: "
                                            f"{msg.payload} with {lookup_key}={filters[lookup_key]}."))

class TestIndividualPayloadSingleTopicFieldName(unittest.TestCase):
    topic_end = random_string()
    topic = random_string()
    topic = topic + '/' + topic_end
    single_topic = topic_end
    multi_topic = random_string()
    multi_topic = multi_topic + '/'
    multi_topic = multi_topic + random_string()
    multi_topic = multi_topic + '/' + topic_end

    payload_dict = {
        'inTemp': round(random.uniform(1, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config_dict = {}
    message_handler_config_dict['type'] = 'individual'

    def test_bad_payload(self):
        topic_config = create_topic_config(
            {'type': 'individual'}, topic_tail_is_fieldname=False)

        SUT, mock_logger, _ = create_provider(topic_config, self.message_handler_config_dict)

        payload = ''
        payload = payload.encode("utf-8")

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)
        self.assertEqual(mock_logger.error.call_count, 3)

    def test_empty_payload(self):
        topic_config = create_topic_config(
            {'type': 'individual'}, topic_tail_is_fieldname=False)

        SUT, mock_logger, _ = create_provider(topic_config, self.message_handler_config_dict)

        payload = ''
        payload = payload.encode("utf-8")

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)
        self.assertEqual(mock_logger.error.call_count, 3)

    def test_None_payload(self):
        topic_config = create_topic_config(
            {'type': 'individual'}, topic_tail_is_fieldname=False)

        SUT, _, mock_manager = create_provider(topic_config, self.message_handler_config_dict)

        payload = None
        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, {msg.topic: None}, msg.topic)

    def test_unicode_topic(self):
        topic_config = create_topic_config(
            {'type': 'individual'}, topic_tail_is_fieldname=False)

        topic = self.topic

        SUT, _, mock_manager = create_provider(topic_config, self.message_handler_config_dict)

        payload = round(random.uniform(1, 100), 2)
        payload_str = str(payload).encode('UTF-8')

        msg = create_message(topic, payload_str, 0, 0)

        SUT.on_message_multi(msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {msg.topic: payload}, msg.topic)

        assert_str_keys(self, mock_manager)

    def test_single_topic(self):
        topic_config = create_topic_config(
            {'type': 'individual'}, topic_tail_is_fieldname=False)

        SUT, _, mock_manager = create_provider(topic_config, self.message_handler_config_dict)

        payload = round(random.uniform(1, 100), 2)
        payload_str = str(payload).encode('UTF-8')

        msg = create_message(self.single_topic, payload_str, 0, 0)

        SUT.on_message_multi(msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {self.topic_end: payload}, self.topic_end)

    def test_multiple_topics(self):
        topic_config = create_topic_config(
            {'type': 'individual'}, topic_tail_is_fieldname=False)

        SUT, _, mock_manager = create_provider(topic_config, self.message_handler_config_dict)

        payload = round(random.uniform(1, 100), 2)
        payload_str = str(payload).encode('UTF-8')

        msg = create_message(self.multi_topic, payload_str)

        SUT.on_message_multi(msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {msg.topic: payload}, msg.topic)

    def test_two_topics(self):
        topic_config = create_topic_config(
            {'type': 'individual'}, topic_tail_is_fieldname=False)

        SUT, _, mock_manager = create_provider(topic_config, self.message_handler_config_dict)

        payload = round(random.uniform(1, 100), 2)
        payload_str = str(payload).encode('UTF-8')

        msg = create_message(self.topic, payload_str)

        SUT.on_message_multi(msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {msg.topic: payload}, msg.topic)

    def test_ignore_default_true(self):
        topic_config = create_topic_config(
            {'type': 'individual'}, topic_tail_is_fieldname=False, ignore=True)

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        fields = {}
        fields['ignore'] = True

        message_handler_config_dict['fields'] = fields

        SUT, _, mock_manager = create_provider(topic_config, message_handler_config_dict)

        payload = round(random.uniform(1, 100), 2)
        payload_str = str(payload).encode('UTF-8')

        msg = create_message(self.single_topic, payload_str, 0, 0)

        SUT.on_message_multi(msg)
        self.assertFalse(mock_manager.append_data.called)

    def test_ignore_default_true_ignore_field_false(self):
        topic_config = create_topic_config(
            {'type': 'individual'}, topic_tail_is_fieldname=False)

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        fields = {}
        fields['ignore'] = True

        field = {}
        field['ignore'] = False
        fields[self.single_topic] = field
        topic_config['fields'] = fields

        message_handler_config_dict['fields'] = fields

        SUT, _, mock_manager = create_provider(topic_config, message_handler_config_dict)

        payload = round(random.uniform(1, 100), 2)
        payload_str = str(payload).encode('UTF-8')

        msg = create_message(self.single_topic, payload_str, 0, 0)

        SUT.on_message_multi(msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {self.topic_end: payload}, self.topic_end)

    def test_ignore_field_true(self):
        topic_config = create_topic_config(
            {'type': 'individual'}, topic_tail_is_fieldname=False)

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        fields = {}

        field = {}
        field['ignore'] = True
        fields[self.single_topic] = field
        topic_config['fields'] = fields
        message_handler_config_dict['fields'] = fields

        SUT, _, mock_manager = create_provider(topic_config, message_handler_config_dict)

        payload = round(random.uniform(1, 100), 2)
        payload_str = str(payload).encode('UTF-8')

        msg = create_message(self.single_topic, payload_str, 0, 0)

        SUT.on_message_multi(msg)
        self.assertFalse(mock_manager.append_data.called)

class TestIndividualPayloadFullTopicFieldName(unittest.TestCase):
    topic_end = random_string()
    topic = random_string()
    topic = topic + '/' + topic_end
    single_topic = topic_end
    multi_topic = random_string()
    multi_topic = multi_topic + '/'
    multi_topic = multi_topic + random_string()
    multi_topic = multi_topic + '/' + topic_end

    payload_dict = {
        'inTemp': round(random.uniform(1, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config_dict = {}
    message_handler_config_dict['type'] = 'individual'

    def test_bad_payload(self):
        topic_config = create_topic_config(
            {'type': 'individual'}, topic_tail_is_fieldname=False)

        SUT, mock_logger, _ = create_provider(topic_config, self.message_handler_config_dict)

        payload = random_string()
        payload = payload.encode("utf-8")

        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)
        self.assertEqual(mock_logger.error.call_count, 3)

    def test_empty_payload(self):
        topic_config = create_topic_config(
            {'type': 'individual'}, topic_tail_is_fieldname=False)

        SUT, mock_logger, _ = create_provider(topic_config, self.message_handler_config_dict)

        payload = ''
        payload = payload.encode("utf-8")
        msg = create_message(self.topic, payload, 0, 0)

        SUT.on_message_multi(msg)
        self.assertEqual(mock_logger.error.call_count, 3)

    def test_None_payload(self):
        topic_config = create_topic_config(
            {'type': 'individual'}, topic_tail_is_fieldname=False)

        message_handler_config_dict = dict(self.message_handler_config_dict)

        SUT, _, mock_manager = create_provider(topic_config, message_handler_config_dict)

        msg = create_message(self.topic, None, 0, 0)

        SUT.on_message_multi(msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {msg.topic: None}, msg.topic)

    def test_single_topic(self):
        topic_config = create_topic_config(
            {'type': 'individual'}, topic_tail_is_fieldname=False)

        SUT, _, mock_manager = create_provider(topic_config, self.message_handler_config_dict)

        payload = round(random.uniform(1, 100), 2)
        payload_str = str(payload).encode('UTF-8')

        msg = create_message(self.single_topic, payload_str, 0, 0)

        SUT.on_message_multi(msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {self.topic_end: payload}, self.topic_end)

if __name__ == '__main__':
    helpers.run_tests()
