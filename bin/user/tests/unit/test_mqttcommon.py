#
#    Copyright (c) 2026 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
""" Tests for the common paho mqtt code. """
import copy
import queue
import random
import ssl
import threading
import time
import unittest

import configobj
import mock

import paho.mqtt.client as mqtt

import user.mqttcommon


def random_string():
    """ Return a string that is unique enough for test fixtures. """
    return f"string-{random.randint(100000, 999999)}"


class TestSelectApi(unittest.TestCase):
    def test_v1_api_when_paho_v1(self):
        paho_v1 = mock.MagicMock(spec=['MQTTv31', 'MQTTv311', 'MQTTv5', 'Client'])

        with mock.patch('user.mqttcommon.mqtt', paho_v1):
            self.assertFalse(user.mqttcommon.has_v2_api())
            self.assertEqual(user.mqttcommon.select_api(mqtt.MQTTv311), user.mqttcommon.API_V1)

    def test_v2_mqtt3_api(self):
        paho_v2 = mock.MagicMock()

        with mock.patch('user.mqttcommon.mqtt', paho_v2):
            self.assertTrue(user.mqttcommon.has_v2_api())
            self.assertEqual(user.mqttcommon.select_api(mqtt.MQTTv31), user.mqttcommon.API_V2_MQTT3)
            self.assertEqual(user.mqttcommon.select_api(mqtt.MQTTv311), user.mqttcommon.API_V2_MQTT3)

    def test_v2_mqtt5_api(self):
        paho_v2 = mock.MagicMock()

        with mock.patch('user.mqttcommon.mqtt', paho_v2):
            self.assertEqual(user.mqttcommon.select_api(mqtt.MQTTv5), user.mqttcommon.API_V2_MQTT5)

    def test_unknown_protocol_selects_v2_mqtt5(self):
        paho_v2 = mock.MagicMock()

        with mock.patch('user.mqttcommon.mqtt', paho_v2):
            self.assertEqual(user.mqttcommon.select_api(0), user.mqttcommon.API_V2_MQTT5)


class TestParseProtocol(unittest.TestCase):
    def test_parse_protocol(self):
        self.assertEqual(user.mqttcommon.parse_protocol('MQTTv31'), mqtt.MQTTv31)
        self.assertEqual(user.mqttcommon.parse_protocol('MQTTv311'), mqtt.MQTTv311)
        self.assertEqual(user.mqttcommon.parse_protocol('MQTTv5'), mqtt.MQTTv5)

    def test_unknown_protocol_string(self):
        self.assertEqual(user.mqttcommon.parse_protocol('invalid'), 0)


class TestCreateClient(unittest.TestCase):
    @staticmethod
    def test_v1():
        paho_v1 = mock.MagicMock()

        with mock.patch('user.mqttcommon.mqtt', paho_v1):
            user.mqttcommon.create_client(user.mqttcommon.API_V1,
                                          client_id='id',
                                          protocol=mqtt.MQTTv311,
                                          userdata={},
                                          clean_session=True)

        paho_v1.Client.assert_called_once_with(protocol=mqtt.MQTTv311,
                                               client_id='id',
                                               userdata={},
                                               clean_session=True)

    @staticmethod
    def test_v1_defaults():
        paho_v1 = mock.MagicMock()

        with mock.patch('user.mqttcommon.mqtt', paho_v1):
            user.mqttcommon.create_client(user.mqttcommon.API_V1,
                                          client_id='id',
                                          protocol=mqtt.MQTTv31)

        paho_v1.Client.assert_called_once_with(protocol=mqtt.MQTTv31,
                                               client_id='id',
                                               userdata=None,
                                               clean_session=None)

    @staticmethod
    def test_v2_mqtt3():
        paho_v2 = mock.MagicMock()

        with mock.patch('user.mqttcommon.mqtt', paho_v2):
            user.mqttcommon.create_client(user.mqttcommon.API_V2_MQTT3,
                                          client_id='id',
                                          protocol=mqtt.MQTTv311,
                                          userdata={},
                                          clean_session=False)

        paho_v2.Client.assert_called_once_with(callback_api_version=paho_v2.CallbackAPIVersion.VERSION2,
                                               protocol=mqtt.MQTTv311,
                                               client_id='id',
                                               userdata={},
                                               clean_session=False)

    @staticmethod
    def test_v2_mqtt5_excludes_clean_session():
        paho_v2 = mock.MagicMock()
        paho_v2.MQTTv5 = mqtt.MQTTv5

        with mock.patch('user.mqttcommon.mqtt', paho_v2):
            user.mqttcommon.create_client(user.mqttcommon.API_V2_MQTT5,
                                          client_id='id',
                                          protocol=mqtt.MQTTv5,
                                          userdata={})

        paho_v2.Client.assert_called_once_with(callback_api_version=paho_v2.CallbackAPIVersion.VERSION2,
                                               protocol=mqtt.MQTTv5,
                                               client_id='id',
                                               userdata={})

    def test_invalid_api(self):
        with self.assertRaises(ValueError) as error:
            user.mqttcommon.create_client('invalid', client_id='id', protocol=mqtt.MQTTv311)

        self.assertEqual(error.exception.args[0], 'Invalid api, invalid.')


class TestConnect(unittest.TestCase):
    @staticmethod
    def test_v1():
        client = mock.Mock()

        user.mqttcommon.connect(client, user.mqttcommon.API_V1, host='host', port=1883, keepalive=60)

        client.connect.assert_called_once_with('host', 1883, 60)

    @staticmethod
    def test_v2_mqtt3():
        client = mock.Mock()

        user.mqttcommon.connect(client, user.mqttcommon.API_V2_MQTT3, host='host', port=1883, keepalive=60)

        client.connect.assert_called_once_with('host', 1883, 60)

    @staticmethod
    def test_v2_mqtt5():
        client = mock.Mock()

        user.mqttcommon.connect(client, user.mqttcommon.API_V2_MQTT5, host='host', port=1883,
                                keepalive=60, clean_start=True)

        client.connect.assert_called_once_with(host='host', port=1883, keepalive=60, clean_start=True)

    @staticmethod
    def test_v2_mqtt5_without_clean_start():
        client = mock.Mock()

        user.mqttcommon.connect(client, user.mqttcommon.API_V2_MQTT5, host='host', port=1883, keepalive=60)

        client.connect.assert_called_once_with(host='host', port=1883, keepalive=60, clean_start=None)

    def test_invalid_api(self):
        with self.assertRaises(ValueError) as error:
            user.mqttcommon.connect(mock.Mock(), 'invalid', host='host', port=1883, keepalive=60)

        self.assertEqual(error.exception.args[0], 'Invalid api, invalid.')


class TestConfigureReconnectDelay(unittest.TestCase):
    @staticmethod
    def test_configure_reconnect_delay():
        client = mock.Mock()

        user.mqttcommon.configure_reconnect_delay(client, min_delay=1, max_delay=120)

        client.reconnect_delay_set.assert_called_once_with(min_delay=1, max_delay=120)


class ReasonCodeStub:
    """ Mimics paho mqtt v2's ReasonCode, which is all the adapters rely on. """
    def __init__(self, value):
        self.value = value


class TestAdaptCallback(unittest.TestCase):
    @staticmethod
    def test_v1_on_connect():
        callback = mock.Mock()

        adapted = user.mqttcommon.adapt_callback(user.mqttcommon.API_V1, 'on_connect', callback)
        adapted('client', 'userdata', 'flags', 5)

        callback.assert_called_once_with('client', 'userdata', 'flags', 5, None)

    @staticmethod
    def test_v2_on_connect():
        callback = mock.Mock()

        adapted = user.mqttcommon.adapt_callback(user.mqttcommon.API_V2_MQTT5, 'on_connect', callback)
        adapted('client', 'userdata', 'flags', ReasonCodeStub(5), 'properties')

        callback.assert_called_once_with('client', 'userdata', 'flags', 5, 'properties')

    @staticmethod
    def test_v1_on_disconnect():
        callback = mock.Mock()

        adapted = user.mqttcommon.adapt_callback(user.mqttcommon.API_V1, 'on_disconnect', callback)
        adapted('client', 'userdata', 5)

        callback.assert_called_once_with('client', 'userdata', 5, None)

    @staticmethod
    def test_v2_on_disconnect_drops_disconnect_flags():
        callback = mock.Mock()

        adapted = user.mqttcommon.adapt_callback(user.mqttcommon.API_V2_MQTT3, 'on_disconnect', callback)
        adapted('client', 'userdata', 'disconnect_flags', ReasonCodeStub(5), 'properties')

        callback.assert_called_once_with('client', 'userdata', 5, 'properties')

    @staticmethod
    def test_v1_on_subscribe():
        callback = mock.Mock()

        adapted = user.mqttcommon.adapt_callback(user.mqttcommon.API_V1, 'on_subscribe', callback)
        adapted('client', 'userdata', 7, [0, 1])

        callback.assert_called_once_with('client', 'userdata', 7, [0, 1], None)

    @staticmethod
    def test_v2_on_subscribe():
        callback = mock.Mock()

        adapted = user.mqttcommon.adapt_callback(user.mqttcommon.API_V2_MQTT5, 'on_subscribe', callback)
        adapted('client', 'userdata', 7, [ReasonCodeStub(0), ReasonCodeStub(1)], 'properties')

        callback.assert_called_once_with('client', 'userdata', 7, [0, 1], 'properties')

    @staticmethod
    def test_v1_on_publish():
        callback = mock.Mock()

        adapted = user.mqttcommon.adapt_callback(user.mqttcommon.API_V1, 'on_publish', callback)
        adapted('client', 'userdata', 7)

        callback.assert_called_once_with('client', 'userdata', 7, None)

    @staticmethod
    def test_v2_on_publish_drops_reason_code():
        callback = mock.Mock()

        adapted = user.mqttcommon.adapt_callback(user.mqttcommon.API_V2_MQTT5, 'on_publish', callback)
        adapted('client', 'userdata', 7, ReasonCodeStub(0), 'properties')

        callback.assert_called_once_with('client', 'userdata', 7, 'properties')

    def test_invalid_event(self):
        with self.assertRaises(ValueError) as error:
            user.mqttcommon.adapt_callback(user.mqttcommon.API_V1, 'invalid', mock.Mock())

        self.assertEqual(error.exception.args[0], 'Invalid event, invalid.')

    def test_invalid_api(self):
        with self.assertRaises(ValueError) as error:
            user.mqttcommon.adapt_callback('invalid', 'on_connect', mock.Mock())

        self.assertEqual(error.exception.args[0], 'Invalid api, invalid.')


class TestApplyCredentials(unittest.TestCase):
    @staticmethod
    def test_credentials_set():
        client = mock.Mock()

        user.mqttcommon.apply_credentials(client, 'username', 'password')

        client.username_pw_set.assert_called_once_with('username', 'password')

    @staticmethod
    def test_username_only():
        client = mock.Mock()

        user.mqttcommon.apply_credentials(client, 'username', None)

        client.username_pw_set.assert_not_called()

    @staticmethod
    def test_password_only():
        client = mock.Mock()

        user.mqttcommon.apply_credentials(client, None, 'password')

        client.username_pw_set.assert_not_called()

    @staticmethod
    def test_no_credentials():
        client = mock.Mock()

        user.mqttcommon.apply_credentials(client, None, None)

        client.username_pw_set.assert_not_called()


class TestConfigureTLS(unittest.TestCase):
    @staticmethod
    def format_error(option, value):
        return f"Invalid '{option}', {value}"

    @staticmethod
    def test_defaults():
        client = mock.Mock()

        user.mqttcommon.configure_tls(client, {}, format_error=TestConfigureTLS.format_error)

        client.tls_set.assert_called_once_with(ca_certs=None,
                                               certfile=None,
                                               keyfile=None,
                                               cert_reqs=ssl.CERT_REQUIRED,
                                               tls_version=ssl.PROTOCOL_TLSv1_2,
                                               ciphers=None)

    @staticmethod
    def test_configured_values():
        client = mock.Mock()
        tls_dict = {
            'certs_required': 'none',
            'tls_version': 'tlsv1',
            'ca_certs': '/path/ca_certs',
            'certfile': '/path/certfile',
            'keyfile': '/path/keyfile',
            'ciphers': 'ciphers'
        }

        user.mqttcommon.configure_tls(client, tls_dict, format_error=TestConfigureTLS.format_error)

        client.tls_set.assert_called_once_with(ca_certs='/path/ca_certs',
                                               certfile='/path/certfile',
                                               keyfile='/path/keyfile',
                                               cert_reqs=ssl.CERT_NONE,
                                               tls_version=ssl.PROTOCOL_TLSv1,
                                               ciphers='ciphers')

    @staticmethod
    def test_empty_ca_certs_is_unset():
        client = mock.Mock()

        user.mqttcommon.configure_tls(client, {'ca_certs': ''}, format_error=TestConfigureTLS.format_error)

        client.tls_set.assert_called_once_with(ca_certs=None,
                                               certfile=None,
                                               keyfile=None,
                                               cert_reqs=ssl.CERT_REQUIRED,
                                               tls_version=ssl.PROTOCOL_TLSv1_2,
                                               ciphers=None)

    @staticmethod
    def test_none_options_are_unset():
        client = mock.Mock()

        user.mqttcommon.configure_tls(client, {'certfile': 'none', 'keyfile': 'None', 'ciphers': 'NONE'},
                                      format_error=TestConfigureTLS.format_error)

        client.tls_set.assert_called_once_with(ca_certs=None,
                                               certfile=None,
                                               keyfile=None,
                                               cert_reqs=ssl.CERT_REQUIRED,
                                               tls_version=ssl.PROTOCOL_TLSv1_2,
                                               ciphers=None)

    def test_invalid_certs_required(self):
        client = mock.Mock()

        with self.assertRaises(ValueError) as error:
            user.mqttcommon.configure_tls(client, {'certs_required': 'invalid'},
                                          format_error=TestConfigureTLS.format_error)

        self.assertEqual(error.exception.args[0], "Invalid 'certs_required', invalid")

    def test_invalid_tls_version(self):
        client = mock.Mock()

        with self.assertRaises(ValueError) as error:
            user.mqttcommon.configure_tls(client, {'tls_version': 'invalid'},
                                          format_error=TestConfigureTLS.format_error)

        self.assertEqual(error.exception.args[0], "Invalid 'tls_version', invalid")


class TestPahoLogLevels(unittest.TestCase):
    def test_paho_log_levels(self):
        self.assertEqual(user.mqttcommon.PAHO_LOG_LEVELS[mqtt.MQTT_LOG_INFO], 'INFO')
        self.assertEqual(user.mqttcommon.PAHO_LOG_LEVELS[mqtt.MQTT_LOG_ERR], 'ERROR')
        self.assertEqual(user.mqttcommon.PAHO_LOG_LEVELS[mqtt.MQTT_LOG_DEBUG], 'DEBUG')


class TestApiLevel(unittest.TestCase):
    def test_api_level(self):
        # Bump deliberately when adding or changing shared surface, and raise the
        # consumers' required level in the same round.
        self.assertEqual(user.mqttcommon.MQTTCOMMON_API, (1, 0))


class QueueLoggerThreadStub(user.mqttcommon.QueueLoggerThread):
    """ A concrete QueueLoggerThread for testing the base class. """
    def start_entry(self):
        """ Return the start entry. """
        return {'log_type': 'INFO', 'msg_text': "Starting logger thread"}

    def exit_entry(self):
        """ Return the exit entry. """
        return {'log_type': 'INFO', 'msg_text': f"Exited logger thread, {self.name}."}

    def invalid_entry(self, entry):
        """ Return the error entry for an entry that could not be logged. """
        return {'log_type': 'ERROR', 'msg_text': entry}


class TestQueueLoggerThread(unittest.TestCase):
    def test_run(self):
        mock_logger = mock.Mock()
        log_queue = queue.Queue()

        SUT = QueueLoggerThreadStub(log_queue, mock_logger)

        entry = {'log_type': 'DEBUG', 'msg_text': "a message"}
        log_queue.put(entry)
        log_queue.put(None)

        SUT.start()
        SUT.join(timeout=5)

        self.assertFalse(SUT.is_alive())
        self.assertTrue(SUT.daemon)
        self.assertTrue(SUT.name.startswith('QueueLoggerThreadStub-'))

        entries = [call[0][0] for call in mock_logger.log_entry.call_args_list]
        self.assertEqual(len(entries), 3)
        self.assertEqual(entries[0], {'log_type': 'INFO', 'msg_text': "Starting logger thread"})
        self.assertIs(entries[1], entry)
        self.assertEqual(entries[2], {'log_type': 'INFO', 'msg_text': f"Exited logger thread, {SUT.name}."})

    def test_run_with_invalid_entry(self):
        mock_logger = mock.Mock()
        log_queue = queue.Queue()

        invalid_entry = {'log_type': 'BOGUS', 'msg_text': "invalid"}

        def log_entry(entry):
            if entry is invalid_entry:
                raise KeyError('log_type')

        mock_logger.log_entry.side_effect = log_entry

        SUT = QueueLoggerThreadStub(log_queue, mock_logger)
        log_queue.put(invalid_entry)
        log_queue.put(None)

        SUT.start()
        SUT.join(timeout=5)

        self.assertFalse(SUT.is_alive())

        entries = [call[0][0] for call in mock_logger.log_entry.call_args_list]
        self.assertEqual(len(entries), 4)
        self.assertEqual(entries[0], {'log_type': 'INFO', 'msg_text': "Starting logger thread"})
        self.assertIs(entries[1], invalid_entry)
        self.assertEqual(entries[2], {'log_type': 'ERROR', 'msg_text': invalid_entry})
        self.assertEqual(entries[3], {'log_type': 'INFO', 'msg_text': f"Exited logger thread, {SUT.name}."})

    def test_abstract_base_class_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            user.mqttcommon.QueueLoggerThread(queue.Queue(), mock.Mock())


class LoggerStub(user.mqttcommon.Logger):
    """ A concrete Logger, for testing the shared logging skeleton. """
    LOG_NAME = 'user.mqttcommon-test'
    LOG_FORMAT = "test %s %s"
    ERROR_LOG_FORMAT = "test-error %s %s"
    LOG_KEY = 'name'


class LoggerThreadStub(user.mqttcommon.LoggerThread):
    """ A distinct concrete LoggerThread, to assert the ctor honors thread_class. """


class ComposedLoggerStub(LoggerStub):
    """ A Logger whose format arguments are composed instead of LOG_KEY-keyed. """
    def _format_args(self, entry):
        """ Compose the first argument from the message id. """
        return (f"composed-{entry['msg_id']}", entry['msg_text'])


class TestLogger(unittest.TestCase):
    def test_init_starts_a_daemon_logger_thread(self):
        with mock.patch('user.mqttcommon.logging') as mock_logging:
            mock_log = mock_logging.getLogger.return_value
            log_queue = queue.Queue()
            name = random_string()

            SUT = LoggerStub(name, log_queue)

            self.assertEqual(SUT.name, name)
            self.assertIs(SUT.log_queue, log_queue)
            self.assertTrue(SUT.log_thread.daemon)
            self.assertTrue(SUT.log_thread.is_alive())

            SUT.shutdown(timeout=5)

            self.assertFalse(SUT.log_thread.is_alive())
            # The thread logs its start and its exit, and nothing else.
            messages = [call[0][2] for call in mock_log.info.call_args_list]
            self.assertEqual(messages, ["Starting logger thread", f"Exited logger thread, {SUT.log_thread.name}."])

    def test_init_uses_the_supplied_thread_class(self):
        with mock.patch('user.mqttcommon.logging'):
            SUT = LoggerStub(random_string(), queue.Queue(), thread_class=LoggerThreadStub)

            self.assertIsInstance(SUT.log_thread, LoggerThreadStub)
            self.assertTrue(SUT.log_thread.is_alive())

            SUT.shutdown(timeout=5)

            self.assertFalse(SUT.log_thread.is_alive())

    def test_init_uses_the_supplied_logger(self):
        mock_log = mock.Mock()
        SUT = LoggerStub(random_string(), queue.Queue(), log=mock_log)

        self.assertIs(SUT.log, mock_log)

        message = random_string()
        SUT.info(None, message)
        SUT.shutdown(timeout=5)

        # The start, the queued message, and the exit all log through the supplied logger.
        mock_log.info.assert_any_call("test %s %s", SUT.name, message)
        self.assertEqual(mock_log.info.call_count, 3)

    def test_format_args_can_be_overridden(self):
        with mock.patch('user.mqttcommon.logging') as mock_logging:
            mock_log = mock_logging.getLogger.return_value
            SUT = ComposedLoggerStub(random_string(), queue.Queue())
            SUT.shutdown(timeout=5)
            mock_log.reset_mock()

            text = random_string()
            SUT.log_entry({'log_type': 'INFO', 'msg_id': 7, 'msg_text': text})

            mock_log.info.assert_called_once_with("test %s %s", "composed-7", text)

    def test_create_entry_captures_the_emitting_thread(self):
        name = random_string()
        text = random_string()

        entry = user.mqttcommon.Logger.create_entry(name, 'INFO', None, text)

        self.assertEqual(entry, {'name': name, 'log_type': 'INFO', 'msg_id': None, 'msg_text': text,
                                 'thread_id': threading.get_native_id()})

    def test_queue_methods_create_the_expected_entries(self):
        with mock.patch('user.mqttcommon.logging'):
            name = random_string()
            texts = [random_string() for _ in range(4)]
            SUT = LoggerStub(name, queue.Queue())
            # Drain the thread so the entries stay queued for assertion.
            SUT.shutdown(timeout=5)

            SUT.trace(1, texts[0])
            SUT.debug(2, texts[1])
            SUT.info(3, texts[2])
            SUT.error(4, texts[3])

        entries = []
        while not SUT.log_queue.empty():
            entries.append(SUT.log_queue.get_nowait())

        self.assertEqual([entry['name'] for entry in entries], [name] * 4)
        self.assertEqual([entry['log_type'] for entry in entries], ['TRACE', 'DEBUG', 'INFO', 'ERROR'])
        self.assertEqual([entry['msg_id'] for entry in entries], [1, 2, 3, 4])
        self.assertEqual([entry['msg_text'] for entry in entries], texts)
        self.assertEqual([entry['thread_id'] for entry in entries], [threading.get_native_id()] * 4)

    @staticmethod
    def _stopped_logger(name=None, log_queue=None):
        """ Construct a Logger and drain its thread, so log_entry calls are synchronous. """
        logger = LoggerStub(name or random_string(),
                            log_queue if log_queue is not None else queue.Queue())
        logger.shutdown(timeout=5)
        return logger

    def test_log_entry_dispatches_the_log_types(self):
        with mock.patch('user.mqttcommon.logging') as mock_logging:
            mock_log = mock_logging.getLogger.return_value
            SUT = self._stopped_logger()
            mock_log.reset_mock()

            trace_name = random_string()
            trace_message = random_string()
            debug_name = random_string()
            debug_message = random_string()
            info_name = random_string()
            info_message = random_string()
            error_name = random_string()
            error_message = random_string()

            SUT.log_entry({'name': trace_name, 'log_type': 'TRACE', 'msg_text': trace_message})
            SUT.log_entry({'name': debug_name, 'log_type': 'DEBUG', 'msg_text': debug_message})
            SUT.log_entry({'name': info_name, 'log_type': 'INFO', 'msg_text': info_message})
            SUT.log_entry({'name': error_name, 'log_type': 'ERROR', 'msg_text': error_message})

            self.assertEqual(mock_log.debug.call_count, 2)
            mock_log.debug.assert_any_call("test %s %s", trace_name, trace_message)
            mock_log.debug.assert_any_call("test %s %s", debug_name, debug_message)
            mock_log.info.assert_called_once_with("test %s %s", info_name, info_message)
            mock_log.error.assert_called_once_with("test-error %s %s", error_name, error_message)

    def test_log_entry_with_no_log_type_is_skipped(self):
        with mock.patch('user.mqttcommon.logging') as mock_logging:
            mock_log = mock_logging.getLogger.return_value
            SUT = self._stopped_logger()
            mock_log.reset_mock()

            SUT.log_entry({'name': random_string(), 'log_type': None, 'msg_text': random_string()})

            mock_log.debug.assert_not_called()
            mock_log.info.assert_not_called()
            mock_log.error.assert_not_called()

    def test_log_entry_with_an_invalid_entry_raises(self):
        with mock.patch('user.mqttcommon.logging'):
            SUT = self._stopped_logger()

            with self.assertRaises(KeyError):  # unknown log type
                SUT.log_entry({'name': random_string(), 'log_type': random_string(),
                               'msg_text': random_string()})
            with self.assertRaises(KeyError):  # missing log type
                SUT.log_entry({})
            with self.assertRaises(TypeError):  # not a dict
                SUT.log_entry(random_string())


class TestShutdown(unittest.TestCase):
    def test_shutdown_drains_the_queue(self):
        with mock.patch('user.mqttcommon.logging') as mock_logging:
            mock_log = mock_logging.getLogger.return_value
            SUT = LoggerStub(random_string(), queue.Queue())

            first = {'name': random_string(), 'log_type': 'INFO', 'msg_text': random_string()}
            second = {'name': random_string(), 'log_type': 'ERROR', 'msg_text': random_string()}
            SUT.log_queue.put(first)
            SUT.log_queue.put(second)

            SUT.shutdown(timeout=5)

            # The start message, the queued messages, and the exit message are logged in queue order.
            self.assertFalse(SUT.log_thread.is_alive())
            logged = [(call[0], call[1][2]) for call in mock_log.method_calls if call[0] in ('info', 'error')]
            self.assertEqual(logged, [('info', "Starting logger thread"),
                                      ('info', first['msg_text']),
                                      ('error', second['msg_text']),
                                      ('info', f"Exited logger thread, {SUT.log_thread.name}.")])

    def test_shutdown_is_idempotent(self):
        with mock.patch('user.mqttcommon.logging') as mock_logging:
            mock_log = mock_logging.getLogger.return_value
            SUT = LoggerStub(random_string(), queue.Queue())

            SUT.shutdown(timeout=5)
            leftover = {'name': random_string(), 'log_type': 'INFO', 'msg_text': random_string()}
            SUT.log_queue.put(leftover)

            SUT.shutdown(timeout=5)

            # The second shutdown neither joins again nor queues another sentinel.
            self.assertFalse(SUT.log_thread.is_alive())
            self.assertIs(SUT.log_queue.get_nowait(), leftover)
            with self.assertRaises(queue.Empty):
                SUT.log_queue.get_nowait()
            mock_log.error.assert_not_called()

    def test_shutdown_warns_when_the_logger_thread_does_not_shut_down(self):
        with mock.patch('user.mqttcommon.logging') as mock_logging:
            mock_log = mock_logging.getLogger.return_value
            name = random_string()
            SUT = LoggerStub(name, queue.Queue())

            # Replace log_entry to simulate a stuck WeeWX log handler.
            block_entered = threading.Event()
            blocked = threading.Event()

            def block_entry(_entry):
                block_entered.set()
                blocked.wait(5)

            SUT.log_entry = block_entry

            SUT.log_queue.put({'name': random_string(), 'log_type': 'INFO',
                               'msg_text': random_string()})
            self.assertTrue(block_entered.wait(5))

            SUT.shutdown(timeout=0.05)

            mock_log.error.assert_called_once_with("test-error %s %s", name,
                                                   f"Unable to shut down {SUT.log_thread.name} thread")
            self.assertTrue(SUT.log_thread.is_alive())

            # Release the thread and wait for it to exit.
            blocked.set()
            SUT.log_thread.join(timeout=5)
            self.assertFalse(SUT.log_thread.is_alive())


class TestLoggerThread(unittest.TestCase):
    def test_run(self):
        mock_logger = mock.Mock()
        log_queue = queue.Queue()

        SUT = user.mqttcommon.LoggerThread(log_queue, mock_logger)

        debug_entry = {'name': random_string(), 'log_type': 'DEBUG', 'msg_text': random_string()}
        no_log_type_entry = {'name': random_string(), 'log_type': None, 'msg_text': random_string()}
        error_entry = {'name': random_string(), 'log_type': 'ERROR', 'msg_text': random_string()}

        log_queue.put(debug_entry)
        log_queue.put(no_log_type_entry)
        log_queue.put(error_entry)
        log_queue.put(None)

        SUT.start()
        SUT.join(timeout=5)

        self.assertFalse(SUT.is_alive())
        self.assertTrue(SUT.daemon)
        self.assertTrue(SUT.name.startswith('LoggerThread-'))

        entries = [call[0][0] for call in mock_logger.log_entry.call_args_list]
        self.assertEqual(len(entries), 5)
        self.assertEqual(entries[0], {'name': SUT.name, 'log_type': 'INFO', 'msg_id': None,
                                      'msg_text': "Starting logger thread", 'thread_id': SUT.native_id})
        self.assertIs(entries[1], debug_entry)
        self.assertIs(entries[2], no_log_type_entry)
        self.assertIs(entries[3], error_entry)
        self.assertEqual(entries[4], {'name': SUT.name, 'log_type': 'INFO', 'msg_id': None,
                                      'msg_text': f"Exited logger thread, {SUT.name}.",
                                      'thread_id': SUT.native_id})

    def test_run_invalid_entry(self):
        mock_logger = mock.Mock()
        log_queue = queue.Queue()

        invalid_entry = {'name': random_string(), 'log_type': random_string(),
                         'msg_text': random_string()}

        def log_entry(entry):
            if entry is invalid_entry:
                raise KeyError('log_type')

        mock_logger.log_entry.side_effect = log_entry

        SUT = user.mqttcommon.LoggerThread(log_queue, mock_logger)

        log_queue.put(invalid_entry)
        log_queue.put(None)

        SUT.start()
        SUT.join(timeout=5)

        self.assertFalse(SUT.is_alive())

        entries = [call[0][0] for call in mock_logger.log_entry.call_args_list]
        self.assertEqual(len(entries), 4)
        self.assertIs(entries[1], invalid_entry)
        # The raw entry is handed over as the message of an error entry.
        self.assertEqual(entries[2], {'name': SUT.name, 'log_type': 'ERROR', 'msg_id': None,
                                      'msg_text': invalid_entry, 'thread_id': SUT.native_id})
        self.assertEqual(entries[3]['log_type'], 'INFO')
        self.assertEqual(entries[3]['msg_text'], f"Exited logger thread, {SUT.name}.")


class TestMessageThrottle(unittest.TestCase):
    @staticmethod
    def _throttle_config(max_count=None, duration=None):
        return {'max': max_count, 'duration': duration}

    def test_none_key_is_not_throttled(self):
        throttle_config = {
            'category': {'ERROR': self._throttle_config(random.randint(1, 10), random.randint(1, 10))},
            'message': {},
        }
        SUT = user.mqttcommon.MessageThrottle(throttle_config)

        with mock.patch.object(user.mqttcommon.MessageThrottle, '_check_message') as mock_check_message:
            self.assertFalse(SUT.is_throttled('ERROR', None))

            mock_check_message.assert_not_called()

    def test_no_config_is_not_throttled(self):
        SUT = user.mqttcommon.MessageThrottle()

        self.assertFalse(SUT.is_throttled('ERROR', random.randint(1000, 9999)))
        self.assertEqual(SUT.logged_ids, {})

    def test_message_tier_is_used(self):
        logging_level = 'ERROR'
        msg_id = random.randint(1000, 9999)
        message_config = self._throttle_config(random.randint(1, 10), random.randint(1, 10))
        throttle_config = {
            'category': {
                'ALL': self._throttle_config(random.randint(1, 10), random.randint(1, 10)),
                logging_level: self._throttle_config(random.randint(1, 10), random.randint(1, 10)),
            },
            'message': {msg_id: message_config},
        }
        SUT = user.mqttcommon.MessageThrottle(throttle_config)

        with mock.patch.object(user.mqttcommon.MessageThrottle, '_check_message') as mock_check_message:
            SUT.is_throttled(logging_level, msg_id)

            mock_check_message.assert_called_once_with(msg_id, message_config)

    def test_category_tier_is_used(self):
        logging_level = 'ERROR'
        msg_id = random.randint(1000, 9999)
        category_config = self._throttle_config(random.randint(1, 10), random.randint(1, 10))
        throttle_config = {
            'category': {
                'ALL': self._throttle_config(random.randint(1, 10), random.randint(1, 10)),
                logging_level: category_config,
            },
            'message': {},
        }
        SUT = user.mqttcommon.MessageThrottle(throttle_config)

        with mock.patch.object(user.mqttcommon.MessageThrottle, '_check_message') as mock_check_message:
            SUT.is_throttled(logging_level, msg_id)

            mock_check_message.assert_called_once_with(msg_id, category_config)

    def test_all_tier_is_used(self):
        msg_id = random.randint(1000, 9999)
        all_config = self._throttle_config(random.randint(1, 10), random.randint(1, 10))
        throttle_config = {
            'category': {'ALL': all_config},
            'message': {},
        }
        SUT = user.mqttcommon.MessageThrottle(throttle_config)

        with mock.patch.object(user.mqttcommon.MessageThrottle, '_check_message') as mock_check_message:
            SUT.is_throttled('INFO', msg_id)

            mock_check_message.assert_called_once_with(msg_id, all_config)

    def test_no_tier_is_used(self):
        throttle_config = {
            'category': {'ERROR': self._throttle_config(random.randint(1, 10), random.randint(1, 10))},
            'message': {},
        }
        SUT = user.mqttcommon.MessageThrottle(throttle_config)

        with mock.patch.object(user.mqttcommon.MessageThrottle, '_check_message') as mock_check_message:
            self.assertFalse(SUT.is_throttled('INFO', random.randint(1000, 9999)))

            mock_check_message.assert_not_called()

    def test_max_is_none(self):
        msg_id = random.randint(1000, 9999)
        throttle_config = self._throttle_config(None, random.randint(60, 600))
        SUT = user.mqttcommon.MessageThrottle()

        with mock.patch('user.mqttcommon.time') as mock_time:
            self.assertFalse(SUT._check_message(msg_id, throttle_config))

            self.assertEqual(SUT.logged_ids, {})
            self.assertEqual(mock_time.time.call_count, 0)

    def test_duration_zero_first_message_is_throttled(self):
        msg_id = random.randint(1000, 9999)
        throttle_config = self._throttle_config(random.randint(1, 1000), 0)
        SUT = user.mqttcommon.MessageThrottle()

        with mock.patch('user.mqttcommon.time') as mock_time:
            self.assertTrue(SUT._check_message(msg_id, throttle_config))

            self.assertEqual(SUT.logged_ids, {msg_id: {'count': 1}})
            self.assertEqual(mock_time.time.call_count, 0)

    def test_duration_zero_within_count_is_throttled(self):
        msg_id = random.randint(1000, 9999)
        count = random.randint(1, 10)
        throttle_config = self._throttle_config(random.randint(count, 1000), 0)
        SUT = user.mqttcommon.MessageThrottle()

        with mock.patch('user.mqttcommon.time') as mock_time:
            SUT.logged_ids = {msg_id: {'count': count}}

            self.assertTrue(SUT._check_message(msg_id, throttle_config))

            self.assertEqual(SUT.logged_ids, {msg_id: {'count': count + 1}})
            self.assertEqual(mock_time.time.call_count, 0)

    def test_duration_zero_summary_is_emitted(self):
        msg_id = random.randint(1000, 9999)
        max_count = random.randint(1, 100)
        count = max_count * random.randint(2, 9)
        summaries = []
        throttle_config = self._throttle_config(max_count, 0)
        SUT = user.mqttcommon.MessageThrottle(log_summary=summaries.append)

        with mock.patch('user.mqttcommon.time') as mock_time:
            SUT.logged_ids = {msg_id: {'count': count}}

            self.assertFalse(SUT._check_message(msg_id, throttle_config))

            self.assertEqual(SUT.logged_ids, {msg_id: {'count': count + 1}})
            self.assertEqual(summaries, [f"{count + 1} messages have been suppressed of {max_count}."])
            self.assertEqual(mock_time.time.call_count, 0)

    def test_window_first_message_is_logged(self):
        msg_id = random.randint(1000, 9999)
        duration = random.randint(60, 600)
        throttle_config = self._throttle_config(random.randint(1, 1000), duration)
        now = int(time.time())
        SUT = user.mqttcommon.MessageThrottle()

        with mock.patch('user.mqttcommon.time') as mock_time:
            mock_time.time.return_value = now

            self.assertFalse(SUT._check_message(msg_id, throttle_config))

            self.assertEqual(SUT.logged_ids, {msg_id: {'window': int(now // duration), 'count': 1}})

    def test_window_change_resets_count(self):
        msg_id = random.randint(1000, 9999)
        duration = random.randint(60, 600)
        count = random.randint(1, 100)
        now = time.time()
        throttle_config = self._throttle_config(random.randint(1, 1000), duration)
        SUT = user.mqttcommon.MessageThrottle()

        with mock.patch('user.mqttcommon.time') as mock_time:
            mock_time.time.return_value = now

            SUT.logged_ids = {msg_id: {'window': -1, 'count': count}}

            self.assertFalse(SUT._check_message(msg_id, throttle_config))

            self.assertEqual(SUT.logged_ids, {msg_id: {'window': int(now // duration), 'count': 1}})

    def test_message_within_threshold(self):
        msg_id = random.randint(1000, 9999)
        duration = random.randint(60, 600)
        count = random.randint(1, 100)
        now = time.time()
        window = int(now // duration)
        throttle_config = self._throttle_config(count + 1, duration)
        SUT = user.mqttcommon.MessageThrottle()

        with mock.patch('user.mqttcommon.time') as mock_time:
            mock_time.time.return_value = now

            SUT.logged_ids = {msg_id: {'window': window, 'count': count}}

            self.assertFalse(SUT._check_message(msg_id, throttle_config))

            self.assertEqual(SUT.logged_ids, {msg_id: {'window': window, 'count': count + 1}})

    def test_window_summary_is_emitted(self):
        msg_id = random.randint(1000, 9999)
        duration = random.randint(60, 600)
        max_count = random.randint(1, 100)
        count = max_count * random.randint(2, 9) - 1
        threshold = count + 1
        now = duration
        window = int(now // duration)
        summaries = []
        throttle_config = self._throttle_config(max_count, duration)
        SUT = user.mqttcommon.MessageThrottle(log_summary=summaries.append)

        with mock.patch('user.mqttcommon.time') as mock_time:
            mock_time.time.return_value = now

            SUT.logged_ids = {msg_id: {'window': window, 'count': count}}

            self.assertFalse(SUT._check_message(msg_id, throttle_config))

            self.assertEqual(SUT.logged_ids, {msg_id: {'window': window, 'count': threshold}})
            self.assertEqual(summaries, [f"{threshold - max_count} messages have been suppressed in window id: {window}."])

    def test_message_is_over_threshold(self):
        msg_id = random.randint(1000, 9999)
        duration = random.randint(60, 600)
        count = random.randint(10, 100)
        now = duration
        window = int(now // duration)
        throttle_config = self._throttle_config(count - 3, duration)
        SUT = user.mqttcommon.MessageThrottle()

        with mock.patch('user.mqttcommon.time') as mock_time:
            mock_time.time.return_value = now

            SUT.logged_ids = {msg_id: {'window': window, 'count': count}}

            self.assertTrue(SUT._check_message(msg_id, throttle_config))

            self.assertEqual(SUT.logged_ids, {msg_id: {'window': window, 'count': count + 1}})

    def test_summary_without_callback_is_dropped(self):
        msg_id = random.randint(1000, 9999)
        duration = random.randint(60, 600)
        max_count = random.randint(1, 100)
        count = max_count * random.randint(2, 9) - 1
        now = duration
        window = int(now // duration)
        throttle_config = self._throttle_config(max_count, duration)
        SUT = user.mqttcommon.MessageThrottle()

        with mock.patch('user.mqttcommon.time') as mock_time:
            mock_time.time.return_value = now

            SUT.logged_ids = {msg_id: {'window': window, 'count': count}}

            self.assertFalse(SUT._check_message(msg_id, throttle_config))

            self.assertEqual(SUT.logged_ids, {msg_id: {'window': window, 'count': count + 1}})


class TestMessageThrottleParseConfig(unittest.TestCase):
    def test_throttle_not_in_config(self):
        config = configobj.ConfigObj({})

        expected_throttle_config = {
            'category': {},
            'message': {},
        }

        self.assertDictEqual(user.mqttcommon.MessageThrottle.parse_config(config), expected_throttle_config)

    def test_empty_throttle_section(self):
        config_dict = {
            'throttle': {}
        }
        config = configobj.ConfigObj(config_dict)

        expected_throttle_config = {
            'category': {},
            'message': {},
        }

        self.assertDictEqual(user.mqttcommon.MessageThrottle.parse_config(config), expected_throttle_config)

    def test_throttle_category_section(self):
        category = {
            'ERROR': {
                'max': random.randint(1, 10),
                'duration': random.randint(1, 10),
            }
        }

        config_dict = {
            'throttle': {
                'category': copy.deepcopy(category),
            }
        }
        config = configobj.ConfigObj(config_dict)

        expected_throttle_config = {
            'category': copy.deepcopy(category),
            'message': {},
        }

        self.assertDictEqual(user.mqttcommon.MessageThrottle.parse_config(config), expected_throttle_config)

    def test_invalid_category_specified(self):
        category_name = f"NOT_A_CATEGORY-{random.randint(1000, 9999)}"
        category = {
            category_name: {}
        }

        config_dict = {
            'throttle': {
                'category': copy.deepcopy(category),
            }
        }
        config = configobj.ConfigObj(config_dict)
        with self.assertRaises(ValueError) as error:
            user.mqttcommon.MessageThrottle.parse_config(config)

        self.assertEqual(error.exception.args[0],
                         f"{category_name} is not valid. Valid categories are ['ALL', 'ERROR', 'INFO', 'DEBUG', 'TRACE']")

    def test_category_missing_max(self):
        category_name = 'ERROR'
        category = {
            category_name: {
                'duration': random.randint(1, 10),
            }
        }

        config_dict = {
            'throttle': {
                'category': copy.deepcopy(category),
            }
        }
        config = configobj.ConfigObj(config_dict)

        with self.assertRaises(ValueError) as error:
            user.mqttcommon.MessageThrottle.parse_config(config)
        self.assertEqual(error.exception.args[0], f"{category_name} is missing 'max' configuration option.")

    def test_category_missing_duration(self):
        category_name = 'ERROR'
        category = {
            category_name: {
                'max': random.randint(1, 10),
            }
        }

        config_dict = {
            'throttle': {
                'category': copy.deepcopy(category),
            }
        }
        config = configobj.ConfigObj(config_dict)

        with self.assertRaises(ValueError) as error:
            user.mqttcommon.MessageThrottle.parse_config(config)
        self.assertEqual(error.exception.args[0], f"{category_name} is missing 'duration' configuration option.")

    def test_messages_missing_max(self):
        message_id = f"message-{random.randint(1000, 9999)}"
        message = {
            message_id: {
                'duration': random.randint(1, 10),
            }
        }

        config_dict = {
            'throttle': {
                'messages': copy.deepcopy(message),
            }
        }
        config = configobj.ConfigObj(config_dict)

        with self.assertRaises(ValueError) as error:
            user.mqttcommon.MessageThrottle.parse_config(config)
        self.assertEqual(error.exception.args[0], f"{message_id} is missing 'max' configuration option.")

    def test_messages_missing_duration(self):
        message_id = f"message-{random.randint(1000, 9999)}"
        message = {
            message_id: {
                'max': random.randint(1, 10),
            }
        }

        config_dict = {
            'throttle': {
                'messages': copy.deepcopy(message),
            }
        }
        config = configobj.ConfigObj(config_dict)

        with self.assertRaises(ValueError) as error:
            user.mqttcommon.MessageThrottle.parse_config(config)
        self.assertEqual(error.exception.args[0], f"{message_id} is missing 'duration' configuration option.")

    def test_no_messages_specified_in_message_section(self):
        msg_id_int = random.randint(1000, 9999)
        message_id = str(msg_id_int)
        message = {
            message_id: {
                'duration': random.randint(1, 10),
                'max': random.randint(1, 10),
            }
        }

        config_dict = {
            'throttle': {
                'messages': copy.deepcopy(message),
            }
        }
        config = configobj.ConfigObj(config_dict)

        expected_throttle_config = {
            'category': {},
            'message': {
                msg_id_int: copy.deepcopy(message[message_id])
            },
        }

        self.assertDictEqual(user.mqttcommon.MessageThrottle.parse_config(config), expected_throttle_config)

    def test_single_message_specified_in_message_section(self):
        messages_name = f"messages-{random.randint(1000, 9999)}"
        msg_id_int = random.randint(1000, 9999)
        message_ids = str(msg_id_int)
        message = {
            messages_name: {
                'duration': random.randint(1, 10),
                'max': random.randint(1, 10),
                'messages': message_ids,
            }
        }

        config_dict = {
            'throttle': {
                'messages': copy.deepcopy(message),
            }
        }
        config = configobj.ConfigObj(config_dict)

        expected_throttle_config = {
            'category': {},
            'message': {
                msg_id_int: copy.deepcopy(message[messages_name])
            },
        }
        del expected_throttle_config['message'][msg_id_int]['messages']

        self.assertDictEqual(user.mqttcommon.MessageThrottle.parse_config(config), expected_throttle_config)

    def test_multiple_messages_specified_in_message_section(self):
        messages_name = f"messages-{random.randint(1000, 9999)}"
        message_ids = [str(random.randint(1000, 9999)), str(random.randint(1000, 9999))]
        duration = random.randint(1, 10)
        max_count = random.randint(1, 10)
        message = {
            messages_name: {
                'duration': duration,
                'max': max_count,
                'messages': message_ids,
            }
        }

        config_dict = {
            'throttle': {
                'messages': copy.deepcopy(message),
            }
        }
        config = configobj.ConfigObj(config_dict)

        expected_throttle_config = {
            'category': {},
            'message': {
            },
        }
        for message_id in message_ids:
            expected_throttle_config['message'][int(message_id)] = {
                'duration': duration,
                'max': max_count,
            }

        self.assertDictEqual(user.mqttcommon.MessageThrottle.parse_config(config), expected_throttle_config)

    def test_message_id_in_list_already_specified(self):
        messages_name = f"messages-{random.randint(1000, 9999)}"
        msg_id_int = random.randint(1000, 9999)
        message_ids = str(msg_id_int)
        message = {
            message_ids: {
                'duration': random.randint(1, 10),
                'max': random.randint(1, 10),
            },
            messages_name: {
                'duration': random.randint(1, 10),
                'max': random.randint(1, 10),
                'messages': message_ids,
            },
        }

        config_dict = {
            'throttle': {
                'messages': copy.deepcopy(message),
            }
        }
        config = configobj.ConfigObj(config_dict)

        with self.assertRaises(ValueError) as error:
            user.mqttcommon.MessageThrottle.parse_config(config)

        self.assertEqual(error.exception.args[0], f"{message_ids} has been configured multiple times")

    def test_message_id_already_specified(self):
        messages_name = f"messages-{random.randint(1000, 9999)}"
        msg_id_int = random.randint(1000, 9999)
        message_ids = str(msg_id_int)
        message = {
            messages_name: {
                'duration': random.randint(1, 10),
                'max': random.randint(1, 10),
                'messages': message_ids,
            },
            message_ids: {
                'duration': random.randint(1, 10),
                'max': random.randint(1, 10),
            },
        }

        config_dict = {
            'throttle': {
                'messages': copy.deepcopy(message),
            }
        }
        config = configobj.ConfigObj(config_dict)

        with self.assertRaises(ValueError) as error:
            user.mqttcommon.MessageThrottle.parse_config(config)

        self.assertEqual(error.exception.args[0], f"{message_ids} has been configured multiple times")


if __name__ == '__main__':
    unittest.main()
