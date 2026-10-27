#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import unittest
import mock

import configobj
import copy
import random
import sys
import threading
import time

import test_weewx_stubs
from test_weewx_stubs import BaseTestClass, random_string
# setup stubs before importing MQTTSubscribe
import user.mqttcommon
test_weewx_stubs.setup_stubs()

from user.mqttsubscribe import create_logger as Logger

class TestInintialization(BaseTestClass):
    def test_init_set_trace_log_level(self):
        log_level = 5

        with mock.patch('user.mqttcommon.logging') as mock_logging:

            mock_logging._checkLevel.return_value = log_level
            mock_logging.getLevelName.return_value = f'Level {int(log_level)}'

            mock_grandparent_handler = mock.Mock()
            mock_grandparent_logger = mock.Mock()
            mock_grandparent_logger.handlers = [mock_grandparent_handler]
            mock_grandparent_logger.parent = None

            mock_parent_handler = mock.Mock()
            mock_parent_logger = mock.Mock()
            mock_parent_logger.handlers = [mock_parent_handler]
            mock_parent_logger.parent = mock_grandparent_logger

            mock_logger = mock.Mock()
            mock_logger.parent = mock_parent_logger
            mock_logging.getLogger.return_value = mock_logger

            SUT = Logger({'mode': random_string()}, level=random_string())

            mock_logging.addLevelName.assert_called_once_with(log_level, 'TRACE')
            SUT.log.setLevel.assert_called_once_with(log_level)

            mock_grandparent_handler.setLevel.assert_called_once_with(log_level)
            mock_parent_handler.setLevel.assert_called_once_with(log_level)

            self.assertEqual(SUT.log.addHandler.call_count, 2)

    @staticmethod
    def test_init_filename_set():
        with mock.patch('user.mqttcommon.logging') as mock_logging:

            mock_logging._checkLevel.return_value = 0

            mock_file_handler = mock.Mock()
            mock_logging.FileHandler.return_value = mock_file_handler
            mode = random_string()
            filename = random_string()

            SUT = Logger({'mode': mode}, filename=filename)

            mock_logging.Formatter.assert_called_once()
            mock_logging.FileHandler.assert_called_once()
            mock_file_handler.setLevel.assert_called_once()
            mock_file_handler.setFormatter.assert_called_once()
            SUT.log.addHandler.assert_called_once()

    @staticmethod
    def test_init_console_set():
        with mock.patch('user.mqttcommon.logging') as mock_logging:

            mock_logging._checkLevel.return_value = 0
            mode = random_string()

            SUT = Logger({'mode': mode}, console=True)

            SUT.log.addHandler.assert_called_once()

    def test_throttle_notice_is_logged(self):
        mode = random_string()
        config_dict = {
            'mode': mode,
            'throttle': {},
        }
        config = configobj.ConfigObj(config_dict)

        with mock.patch('user.mqttcommon.logging') as mock_logging:
            mock_logging._checkLevel.return_value = 0
            thread_id = threading.get_native_id()

            SUT = Logger(config)
            SUT.shutdown()

            SUT.log.info.assert_any_call(SUT.LOG_FORMAT, f"{mode}-{thread_id}",
                                         user.mqttcommon.MessageThrottle.NOTICE_EXPERIMENTAL)

class TestLogging(BaseTestClass):
    @staticmethod
    def test_error_logged():
        with mock.patch('user.mqttcommon.logging') as mock_logging:
            mock_logging._checkLevel.return_value = 0
            thread_id = threading.get_native_id()
            mode = random_string()
            message_text = random_string()

            SUT = Logger({'mode': mode})

            SUT.error(random.randint(1, 100), message_text)
            SUT.shutdown()

            SUT.log.error.assert_called_once_with(SUT.LOG_FORMAT, f"{mode}-{thread_id}", message_text)

    @staticmethod
    def test_info_logged():
        with mock.patch('user.mqttcommon.logging') as mock_logging:
            mock_logging._checkLevel.return_value = 0
            thread_id = threading.get_native_id()
            mode = random_string()
            message = random_string()

            SUT = Logger({'mode': mode})

            SUT.info(random.randint(1, 100), message)
            SUT.shutdown()

            # The logger thread start message is also logged at INFO.
            SUT.log.info.assert_any_call(SUT.LOG_FORMAT, f"{mode}-{thread_id}", message)

    @staticmethod
    def test_archive_record_context_is_logged():
        with mock.patch('user.mqttcommon.logging') as mock_logging:
            mock_logging._checkLevel.return_value = 0
            thread_id = threading.get_native_id()
            mode = random_string()
            archive_timestamp = int(time.time())
            message = random_string()

            SUT = Logger({'mode': mode})
            SUT.archive_timestamp = archive_timestamp

            SUT.info(random.randint(1, 100), message)
            SUT.shutdown()

            # The archive timestamp is part of the context while a record is being processed.
            SUT.log.info.assert_any_call(SUT.LOG_FORMAT, f"{mode}-{thread_id}-{archive_timestamp}", message)

    @staticmethod
    def test_debug_logged():
        with mock.patch('user.mqttcommon.logging') as mock_logging:
            mock_logging._checkLevel.return_value = 0
            thread_id = threading.get_native_id()
            mode = random_string()
            message = random_string()

            SUT = Logger({'mode': mode})

            SUT.debug(random.randint(1, 100), message)
            SUT.shutdown()

            SUT.log.debug.assert_called_once_with(SUT.LOG_FORMAT, f"{mode}-{thread_id}", message)

    @staticmethod
    def test_trace_logged_with_debug_set():
        with mock.patch('user.mqttcommon.logging') as mock_logging:
            sys.modules['weewx'].debug = 2
            mock_logging._checkLevel.return_value = 0
            thread_id = threading.get_native_id()
            mode = random_string()
            message = random_string()

            SUT = Logger({'mode': mode})

            SUT.trace(random.randint(1, 100), message)
            SUT.shutdown()

            SUT.log.debug.assert_called_once_with(SUT.LOG_FORMAT, f"{mode}-{thread_id}", message)

    @staticmethod
    def test_trace_logged_with_debug_not_set():
        with mock.patch('user.mqttcommon.logging') as mock_logging:
            mock_logging._checkLevel.return_value = 0
            thread_id = threading.get_native_id()
            mode = random_string()
            message = random_string()

            sys.modules['weewx'].debug = 0
            SUT = Logger({'mode': mode})

            SUT.trace(random.randint(1, 100), message)
            SUT.shutdown()

            SUT.log.log.assert_called_once_with(5, SUT.LOG_FORMAT, f"{mode}-{thread_id}", message)

class TestQueue(BaseTestClass):
    def test_log_entry_invalid_entry(self):
        with mock.patch('user.mqttcommon.logging') as mock_logging:
            mock_logging._checkLevel.return_value = 0

            SUT = Logger({'mode': random_string()})

            with self.assertRaises(KeyError):
                SUT.log_entry({'log_type': random_string(), 'msg_id': None, 'msg_text': random_string()})
            with self.assertRaises(KeyError):
                SUT.log_entry({})
            with self.assertRaises(TypeError):
                SUT.log_entry(random_string())

            SUT.shutdown()

    def test_shutdown_drains_queue(self):
        with mock.patch('user.mqttcommon.logging') as mock_logging:
            mock_logging._checkLevel.return_value = 0
            mock_log = mock_logging.getLogger.return_value

            SUT = Logger({'mode': random_string()})

            SUT.info(random.randint(1, 100), random_string())
            SUT.debug(random.randint(1, 100), random_string())
            SUT.error(random.randint(1, 100), random_string())

            SUT.shutdown()

            # The start message, the queued messages, and the exit message are logged in queue order.
            logged = [call[0] for call in mock_log.method_calls]
            self.assertEqual(logged, ['info', 'info', 'debug', 'error', 'info'])
            self.assertFalse(SUT.log_thread.is_alive())

    def test_shutdown_is_idempotent(self):
        with mock.patch('user.mqttcommon.logging') as mock_logging:
            mock_logging._checkLevel.return_value = 0

            SUT = Logger({'mode': random_string()})

            SUT.shutdown()
            SUT.shutdown()

            self.assertFalse(SUT.log_thread.is_alive())

    def test_shutdown_timeout(self):
        with mock.patch('user.mqttcommon.logging') as mock_logging:
            mock_logging._checkLevel.return_value = 0
            mock_log = mock_logging.getLogger.return_value
            mode = random_string()

            SUT = Logger({'mode': mode})

            # Replace log_entry to simulate a stuck log handler.
            block_entered = threading.Event()
            blocked = threading.Event()

            def block_entry(_entry):
                block_entered.set()
                blocked.wait(5)

            SUT.log_entry = block_entry

            SUT.info(random.randint(1, 100), random_string())
            self.assertTrue(block_entered.wait(5))

            SUT.shutdown(timeout=0.05)

            expected_text = user.mqttcommon.Logger.log_messages[124004].format(name=SUT.log_thread.name)
            mock_log.error.assert_called_once_with(SUT.LOG_FORMAT, f"{mode}-{threading.get_native_id()}", expected_text)
            self.assertTrue(SUT.log_thread.is_alive())

            # Release the thread and wait for it to exit.
            blocked.set()
            SUT.log_thread.join(timeout=5)
            self.assertFalse(SUT.log_thread.is_alive())

class TestThrottling(BaseTestClass):
    def test_window_summary_is_logged(self):
        mode = random_string()
        msg_id_int = random.randint(1000, 9999)
        msg_id = str(msg_id_int)
        duration = random.randint(60, 600)
        max_count = random.randint(1, 100)
        count = max_count * random.randint(2, 9) - 1
        threshold = count + 1
        now = duration
        window = int(now // duration)

        config_dict = {
            'mode': mode,
            'throttle': {
                'messages': {
                    msg_id: {
                        'duration': duration,
                        'max': max_count,
                    }
                }
            }
        }
        config = configobj.ConfigObj(config_dict)

        with mock.patch('user.mqttcommon.logging') as mock_logging:
            with mock.patch('user.mqttcommon.time') as mock_time:
                mock_logging._checkLevel.return_value = 0
                mock_time.time.return_value = now
                thread_id = threading.get_native_id()

                SUT = Logger(config)

                SUT.throttle.logged_ids = {
                    msg_id: {
                        'window': window,
                        'count': count,
                    }
                }

                throttle = SUT.throttle._check_message(msg_id, SUT.throttle.throttle_config['message'][msg_id_int])

                logged_ids = {
                    msg_id: {
                        'window': window,
                        'count': threshold,
                    }
                }

                message_text = f"{threshold - max_count} messages have been suppressed in window id: {window}."

                SUT.shutdown()

                self.assertFalse(throttle)
                self.assertEqual(len(SUT.throttle.logged_ids), 1)
                self.assertDictEqual(SUT.throttle.logged_ids, logged_ids)
                SUT.log.error.assert_called_once_with(SUT.LOG_FORMAT, f"{mode}-{thread_id}", message_text)




if __name__ == '__main__':
    # testcase = sys.argv[1]
    testcase = 'test_window_summary_is_logged'

    test_suite = unittest.TestSuite()
    test_suite.addTest(TestThrottling(testcase))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)