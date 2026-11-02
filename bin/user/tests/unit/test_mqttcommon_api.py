#
#    Copyright (c) 2026 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import importlib
import unittest

import mock

import test_weewx_stubs
# setup stubs before importing mqttsubscribe
test_weewx_stubs.setup_stubs()
import user.mqttcommon
import user.mqttsubscribe

class TestApiCheck(unittest.TestCase):
    def setUp(self):
        # reset stubs for every test
        test_weewx_stubs.setup_stubs()

    def test_stale_mqttcommon_raises_at_import(self):
        with mock.patch.object(user.mqttcommon, 'MQTTCOMMON_API', (0, 0)):
            with self.assertRaises(ImportError):
                importlib.reload(user.mqttsubscribe)

if __name__ == '__main__':
    unittest.main()
