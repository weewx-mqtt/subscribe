#
#    Copyright (c) 2026 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
""" Tests for the common paho mqtt code. """
import queue
import ssl
import unittest

import mock

import paho.mqtt.client as mqtt

import user.mqttcommon


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


if __name__ == '__main__':
    unittest.main()
