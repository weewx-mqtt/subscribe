#
#    Copyright (c) 2026 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import queue
import random
import unittest

import mock

import test_weewx_stubs
from test_weewx_stubs import BaseTestClass, random_string
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

from user.mqttcommon import Logger, LoggerThread

class TestLoggerThread(BaseTestClass):
    def test_run(self):
        log_queue = queue.Queue()
        mock_logger = mock.Mock()
        mock_logger.create_entry.side_effect = Logger.create_entry
        mock_logger.stamp_entry.side_effect = lambda entry: entry

        SUT = LoggerThread(log_queue, mock_logger)

        first = Logger.create_entry(random_string(), 'INFO', random.randint(1, 100), random_string())
        second = Logger.create_entry(random_string(), 'ERROR', None, random_string())
        log_queue.put(first)
        log_queue.put(second)
        log_queue.put(None)

        SUT.start()
        SUT.join(timeout=5)

        self.assertFalse(SUT.is_alive())
        self.assertTrue(SUT.name.startswith('LoggerThread-'))

        entries = [call[0][0] for call in mock_logger.log_entry.call_args_list]
        self.assertEqual(len(entries), 4)
        self.assertEqual(entries[0]['msg_id'], 122002)
        self.assertIs(entries[1], first)
        self.assertIs(entries[2], second)
        self.assertEqual(entries[3]['msg_id'], 122003)

    def test_run_invalid_entry(self):
        log_queue = queue.Queue()
        mock_logger = mock.Mock()
        mock_logger.create_entry.side_effect = Logger.create_entry
        mock_logger.stamp_entry.side_effect = lambda entry: entry

        invalid_entry = {'log_type': random_string(), 'msg_id': None, 'msg_text': random_string()}

        def log_entry(entry):
            if entry is invalid_entry:
                raise KeyError('log_type')

        mock_logger.log_entry.side_effect = log_entry

        SUT = LoggerThread(log_queue, mock_logger)

        log_queue.put(invalid_entry)
        log_queue.put(None)

        SUT.start()
        SUT.join(timeout=5)

        self.assertFalse(SUT.is_alive())

        entries = [call[0][0] for call in mock_logger.log_entry.call_args_list]
        self.assertEqual(len(entries), 4)
        self.assertEqual(entries[0]['msg_id'], 122002)
        self.assertIs(entries[1], invalid_entry)
        self.assertEqual(entries[2]['msg_id'], 124003)
        self.assertEqual(entries[2]['log_type'], 'ERROR')
        self.assertIn(str(invalid_entry), entries[2]['msg_text'])
        self.assertEqual(entries[3]['msg_id'], 122003)

if __name__ == '__main__':
    unittest.main(exit=False)
