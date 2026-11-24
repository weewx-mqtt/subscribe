#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import contextlib
import helpers
import mock

import configobj
import random
import ssl

import test_weewx_stubs
from test_weewx_stubs import random_string, BaseTestClass
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

from user.mqttcommon import Logger
from user.mqttsubscribe import MQTTSubscriber

mock_client = None

# The TLS 1.2 default. A build without the legacy constant, as OpenSSL 4 is,
# reaches it through PROTOCOL_TLS_CLIENT, which means 'TLS 1.2 or newer'.
TLS_1_2 = getattr(ssl, 'PROTOCOL_TLSv1_2', ssl.PROTOCOL_TLS_CLIENT)


def create_subscriber_config(**overrides):
    """ Build the minimal subscriber config, with per-test overrides. """
    config_dict = {
        'message_callback': {},
        'topics': {random_string(): {}},
    }
    config_dict.update(overrides)
    return configobj.ConfigObj(config_dict)


@contextlib.contextmanager
def patched_subscriber(client=None):
    """ Patch the subscriber's collaborators and install the module-level mock client. """
    global mock_client
    mock_client = client if client is not None else mock.Mock()
    with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
        with mock.patch('user.mqttsubscribe.TopicManager'):
            yield mock_client


def assert_missing_ssl_constant(test_case, config_option, value, constant_name):
    """ Hiding an ssl constant must make the subscriber reject the matching TLS option. """
    config = create_subscriber_config(tls={'ca_certs': random_string(), config_option: value})
    mock_logger = mock.Mock(spec=Logger)
    with patched_subscriber():
        try:
            saved_constant = getattr(ssl, constant_name)
            delattr(ssl, constant_name)
        except AttributeError:
            saved_constant = None
        with test_case.assertRaises(ValueError) as error:
            MQTTSubscriberTest(config, mock_logger)
        if saved_constant:
            setattr(ssl, constant_name, saved_constant)
        test_case.assertEqual(error.exception.args[0], f"Invalid '{config_option}', {value}.")


class MQTTSubscriberTest(MQTTSubscriber):
    def get_client(self, mqtt_options):
        return mock_client

    def set_callbacks(self, mqtt_options):
        pass

    def connect(self, mqtt_options):
        self.client.connect()

class Msg:
    def __init__(self):
        pass

class TestInitialization(BaseTestClass):
    def test_connect_exception(self):
        global mock_client
        mock_logger = mock.Mock(spec=Logger)

        config = create_subscriber_config()

        exception = Exception("Connect exception.")

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            mock_client = mock.Mock()
            mock_client.return_value = mock_client
            mock_client.connect.side_effect = mock.Mock(side_effect=exception)
            with self.assertRaises(test_weewx_stubs.WeeWxIOError) as error:
                with mock.patch('user.mqttsubscribe.TopicManager'):
                    MQTTSubscriberTest(config, mock_logger)

            self.assertEqual(error.exception.args[0], exception)

    def test_missing_topics(self):
        config_dict = {

            'message_callback': {},
        }
        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)
        with self.assertRaises(ValueError) as error:
            MQTTSubscriber(config, mock_logger)

        self.assertEqual(error.exception.args[0], "[[topics]] is required.")

    def test_missing_archive_topic_in_topics(self):
        archive_topic = random_string()
        config = create_subscriber_config(archive_topic=archive_topic)

        mock_logger = mock.Mock(spec=Logger)
        with self.assertRaises(ValueError) as error:
            with mock.patch('user.mqttsubscribe.TopicManager'):
                MQTTSubscriber(config, mock_logger)

        self.assertEqual(error.exception.args[0], (f"Archive topic {archive_topic} must be in [[topics]]."))

    @staticmethod
    def test_username_None():
        host = 'host'
        port = random.randint(1000, 9999)
        keepalive = random.randint(1, 10)
        config = create_subscriber_config(host=host, keepalive=keepalive, port=port, username=None, password=random_string(), archive_topic=None)

        mock_logger = mock.Mock(spec=Logger)

        with patched_subscriber():
            SUT = MQTTSubscriberTest(config, mock_logger)
            SUT.client.username_pw_set.assert_not_called()
            SUT.client.connect.assert_called_once()

    @staticmethod
    def test_password_None():
        host = 'host'
        port = random.randint(1000, 9999)
        keepalive = random.randint(1, 10)
        config = create_subscriber_config(host=host, keepalive=keepalive, port=port, username=random_string(), password=None, archive_topic=None)

        mock_logger = mock.Mock(spec=Logger)

        with patched_subscriber():
            SUT = MQTTSubscriberTest(config, mock_logger)
            SUT.client.username_pw_set.assert_not_called()
            SUT.client.connect.assert_called()

    @staticmethod
    def test_username_and_password_None():
        host = 'host'
        port = random.randint(1000, 9999)
        keepalive = random.randint(1, 10)
        config = create_subscriber_config(host=host, keepalive=keepalive, port=port, username=None, password=None, archive_topic=None)

        mock_logger = mock.Mock(spec=Logger)

        with patched_subscriber():
            SUT = MQTTSubscriberTest(config, mock_logger)
            SUT.client.username_pw_set.assert_not_called()
            SUT.client.connect.assert_called_once()

    @staticmethod
    def test_username_and_password_set():
        host = 'host'
        port = random.randint(1000, 9999)
        keepalive = random.randint(1, 10)
        username = random_string()
        password = random_string()
        config = create_subscriber_config(host=host, keepalive=keepalive, port=port, username=username, password=password, archive_topic=None)

        mock_logger = mock.Mock(spec=Logger)

        with patched_subscriber():
            SUT = MQTTSubscriberTest(config, mock_logger)
            SUT.client.username_pw_set.assert_called_once_with(username, password)
            SUT.client.connect.assert_called_once()

    def test_clean_start_not_valid(self):
        clean_start = random_string()
        config_dict = {
            'clean_start': clean_start,
            'topics': {
                random_string(): {}
            }
        }

        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)

        with patched_subscriber():
            with self.assertRaises(ValueError) as error:

                MQTTSubscriberTest(config, mock_logger)
            self.assertEqual(error.exception.args[0], f"Invalid 'clean_start' option, {clean_start}.")


class Testtls_configuration(BaseTestClass):
    @staticmethod
    def test_tls_configuration_good():
        ca_certs = random_string()
        config = create_subscriber_config(tls={'ca_certs': ca_certs})
        mock_logger = mock.Mock(spec=Logger)
        with patched_subscriber():
            SUT = MQTTSubscriberTest(config, mock_logger)
            SUT.client.tls_set.assert_called_once_with(ca_certs=ca_certs,
                                                       certfile=None,
                                                       keyfile=None,
                                                       cert_reqs=ssl.CERT_REQUIRED,
                                                       tls_version=TLS_1_2,
                                                       ciphers=None)

    def test_missing_PROTOCOL_TLS(self):
        assert_missing_ssl_constant(self, 'tls_version', 'tls', 'PROTOCOL_TLS')

    def test_missing_PROTOCOL_TLSv1(self):
        assert_missing_ssl_constant(self, 'tls_version', 'tlsv1', 'PROTOCOL_TLSv1')

    def test_missing_PROTOCOL_TLSv1_1(self):
        assert_missing_ssl_constant(self, 'tls_version', 'tlsv1_1', 'PROTOCOL_TLSv1_1')

    def test_missing_PROTOCOL_TLSv1_2(self):
        assert_missing_ssl_constant(self, 'tls_version', 'tlsv1_2', 'PROTOCOL_TLSv1_2')

    def test_missing_PROTOCOL_SSLv2(self):
        assert_missing_ssl_constant(self, 'tls_version', 'sslv2', 'PROTOCOL_SSLv2')

    def test_missing_PROTOCOL_SSLv23(self):
        assert_missing_ssl_constant(self, 'tls_version', 'sslv23', 'PROTOCOL_SSLv23')

    def test_missing_PROTOCOL_SSLv3(self):
        assert_missing_ssl_constant(self, 'tls_version', 'sslv3', 'PROTOCOL_SSLv3')

    def test_invalid_certs_required(self):
        assert_missing_ssl_constant(self, 'certs_required', random_string(), 'PROTOCOL_SSLv3')

class TestDeprecatedOptions(BaseTestClass):
    def test_a_deprecated_config_options_is_logged_and_exception_not_raised(self):
        global mock_client
        mock_client = mock.Mock()
        config = create_subscriber_config(stop_on_validation_errors=False, topics={}, topic=random_string())

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            with mock.patch('user.mqttsubscribe.TopicManager'):
                with mock.patch('user.mqttcommon.Logger', spec=Logger) as mock_logger:
                    MQTTSubscriberTest(config, mock_logger)

                self.assertEqual(mock_logger.info.call_count, 15)
                mock_logger.info.assert_any_call(32016, "'topic' is deprecated, use '[[topics]][[[topic name]]]'.")

    def test_topic_is_deprecated(self):
        config = create_subscriber_config(stop_on_validation_errors=True, topics={}, topic=random_string())

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            with mock.patch('user.mqttsubscribe.TopicManager'):
                with self.assertRaises(ValueError) as error:
                    MQTTSubscriber(config, mock_logger)

                self.assertEqual(error.exception.args[0], "'topic' is deprecated, use '[[topics]][[[topic name]]]'.")

    def test_overlap_is_deprecated(self):
        config = create_subscriber_config(stop_on_validation_errors=True, topics={}, overlap=random_string())

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            with mock.patch('user.mqttsubscribe.TopicManager'):
                with self.assertRaises(ValueError) as error:
                    MQTTSubscriber(config, mock_logger)
                self.assertEqual(error.exception.args[0], "'overlap' is deprecated, use 'adjust_start_time'.")

    def test_archive_field_cache_is_deprecated(self):
        config = create_subscriber_config(stop_on_validation_errors=True, topics={}, archive_field_cache=random_string())

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            with mock.patch('user.mqttsubscribe.TopicManager'):
                with self.assertRaises(ValueError) as error:
                    MQTTSubscriber(config, mock_logger)
                self.assertEqual(error.exception.args[0],
                                 "'archive_field_cache' is deprecated, use '[[topics]][[[topic name]]][[[[field name]]]]'.")

    def test_full_topic_fieldname_is_deprecated(self):
        config = create_subscriber_config(stop_on_validation_errors=True, message_callback={'full_topic_fieldname': random_string()}, topics={})

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            with mock.patch('user.mqttsubscribe.TopicManager'):
                with self.assertRaises(ValueError) as error:
                    MQTTSubscriber(config, mock_logger)
                self.assertEqual(error.exception.args[0],
                                 "'full_topic_fieldname' is deprecated, use '[[topics]][[[topic name]]][[[[field name]]]]'.")

    def test_contains_total_is_deprecated(self):
        config = create_subscriber_config(stop_on_validation_errors=True, message_callback={'contains_total': random_string()}, topics={})

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            with mock.patch('user.mqttsubscribe.TopicManager'):
                with self.assertRaises(ValueError) as error:
                    MQTTSubscriber(config, mock_logger)
                self.assertEqual(error.exception.args[0],
                                 "'contains_total' is deprecated, use '[[topics]][[[topic name]]][[[[field name]]]]' contains_total setting.")

    def test_label_map_is_deprecated(self):
        config = create_subscriber_config(stop_on_validation_errors=True, message_callback={'label_map': {}}, topics={})

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            with mock.patch('user.mqttsubscribe.TopicManager'):
                with self.assertRaises(ValueError) as error:
                    MQTTSubscriber(config, mock_logger)
                self.assertEqual(error.exception.args[0],
                                 "'label_map' is deprecated, use '[[topics]][[[topic name]]][[[[field name]]]]' name setting.")

    def test_fields_is_deprecated(self):
        config = create_subscriber_config(stop_on_validation_errors=True, message_callback={'fields': {}}, topics={})

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            with mock.patch('user.mqttsubscribe.TopicManager'):
                with self.assertRaises(ValueError) as error:
                    MQTTSubscriber(config, mock_logger)
                self.assertEqual(error.exception.args[0],
                                 "'fields' is deprecated, use '[[topics]][[[topic name]]][[[[field name]]]]'.")

    def test_use_topic_as_fieldname(self):
        config_dict = {}
        config_dict['topics'] = {}
        config_dict['topics']['use_topic_as_fieldname'] = 'true'
        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)

        with patched_subscriber():
            SUT = MQTTSubscriberTest(config, mock_logger)
            self.assertEqual(SUT.logger.info.call_count, 14)
            mock_logger.info.assert_any_call(32015, "'use_topic_as_fieldname' option is no longer needed and can be removed.")

    def test_log_is_deprecated(self):
        config = create_subscriber_config(topics={}, log='true')

        mock_logger = mock.Mock(spec=Logger)

        with patched_subscriber():
            MQTTSubscriberTest(config, mock_logger)
            mock_logger.info.assert_any_call(32015, "'log' is deprecated, use 'log_mqtt'.")

class TestStart(BaseTestClass):
    def set_connection_success(self, *args, **kwargs):
        self.SUT.userdata['connect'] = True

    def test_bad_connection_return_code(self):
        global mock_client
        mock_logger = mock.Mock(spec=Logger)
        rc_strings = {
            0: "Connection Accepted.",
            1: "Connection Refused: unacceptable protocol version.",
            2: "Connection Refused: identifier rejected.",
            3: "Connection Refused: broker unavailable.",
            4: "Connection Refused: bad user name or password.",
            5: "Connection Refused: not authorised.",
        }

        config = create_subscriber_config(topics={})
        connect_rc = random.randint(1, 10)
        flags = random.randint(0, 255)
        rc_string = rc_strings.get(connect_rc, "Connection Refused: unknown reason.")

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            with mock.patch('user.mqttsubscribe.TopicManager'):
                with mock.patch('user.mqttsubscribe.time'):
                    with self.assertRaises(test_weewx_stubs.WeeWxIOError) as error:
                        mock_client = mock.Mock()
                        SUT = MQTTSubscriberTest(config, mock_logger)

                        SUT.userdata = {}
                        SUT.userdata['connect'] = True
                        SUT.userdata['connect_rc'] = connect_rc
                        SUT.userdata['connect_flags'] = flags

                        SUT.start()

                    SUT.client.loop_start.assert_called_once()
                    self.assertEqual(error.exception.args[0],
                                     f"Unable to connect, result code {int(connect_rc)}, '{rc_string}', connection flags {flags}.")

    @staticmethod
    def test_immediate_connection():
        global mock_client
        mock_logger = mock.Mock(spec=Logger)

        config = create_subscriber_config(topics={})

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            with mock.patch('user.mqttsubscribe.TopicManager'):
                with mock.patch('user.mqttsubscribe.time') as mock_time:
                    mock_client = mock.Mock()
                    SUT = MQTTSubscriberTest(config, mock_logger)

                    SUT.userdata = {}
                    SUT.userdata['connect'] = True
                    SUT.userdata['connect_rc'] = 0

                    SUT.start()
                    SUT.client.loop_start.assert_called_once()
                    mock_time.sleep.assert_not_called()

    def test_wait_for_connection(self):
        global mock_client
        mock_logger = mock.Mock(spec=Logger)

        config = create_subscriber_config(topics={})

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            with mock.patch('user.mqttsubscribe.TopicManager'):
                with mock.patch('user.mqttsubscribe.time') as mock_time:
                    mock_client = mock.Mock()
                    SUT = MQTTSubscriberTest(config, mock_logger)

                    self.SUT = SUT
                    SUT.userdata = {}
                    SUT.userdata['connect'] = False
                    SUT.userdata['connect_rc'] = 0
                    mock_time.sleep.side_effect = mock.Mock(side_effect=self.set_connection_success)  # Hack, use this to escape the loop

                    SUT.start()
                    SUT.client.loop_start.assert_called_once()
                    mock_time.sleep.assert_called_once()

class Test_disconnect(BaseTestClass):
    @staticmethod
    def test_disconnect():
        mock_logger = mock.Mock(spec=Logger)

        config = create_subscriber_config(topics={})

        with patched_subscriber():
            SUT = MQTTSubscriberTest(config, mock_logger)
            SUT.disconnect()
            SUT.client.disconnect.assert_called_once()
            SUT.client.loop_stop.assert_called_once()

class Teston_connect(BaseTestClass):
    unit_system_name = 'US'
    unit_system = 1
    config_dict = {
        'host': random_string(),
        'keepalive': random.randint(1, 10),
        'port': random.randint(1, 10),
        'username': random_string(),
        'password': random_string(),
        'archive_topic': None
    }

    def test_multiple_topics(self):
        global mock_client
        topic1 = random_string()
        topic2 = random_string()
        config_dict = dict(self.config_dict)
        config_dict['topics'] = {}
        config_dict['topics'][topic1] = {}
        config_dict['topics'][topic1]['subscribe'] = True
        config_dict['topics'][topic2] = {}
        config_dict['topics'][topic2]['subscribe'] = True
        config_dict['message_callback'] = {}

        config = configobj.ConfigObj(config_dict)

        subscribed_topics = dict(config_dict['topics'])
        qos = 0

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('user.mqttsubscribe.MessageCallbackProvider'):
            with mock.patch('user.mqttsubscribe.TopicManager') as mock_manager:
                mock_client = mock.Mock()
                type(mock_manager.return_value).subscribed_topics = mock.PropertyMock(return_value=subscribed_topics)
                type(mock_manager.return_value).get_qos = mock.Mock(return_value=qos)
                mock_client.subscribe.return_value = [1, 0]
                SUT = MQTTSubscriberTest(config, mock_logger)
                SUT._subscribe(mock_client)
                self.assertEqual(mock_client.subscribe.call_count, 2)
                mock_client.subscribe.assert_any_call(topic1, qos)
                mock_client.subscribe.assert_any_call(topic2, qos)

if __name__ == '__main__':
    helpers.run_tests()
