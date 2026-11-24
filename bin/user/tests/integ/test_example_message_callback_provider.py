#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import helpers
import utils

from test_get_data import TestGetData
from test_driver import TestDriver
from test_get_accumulated_data import TestAccumulatedData
from test_service import TestService

class TestGetDataExampleMessageCallbackProvider(TestGetData):
    # @unittest.skip("")
    def test_xml(self):
        utils.run_data_file(self, 'xml', 'example_callback_provider.json')

class TestDriverExamoleMessageCallbackProvider(TestDriver):
    # @unittest.skip("")
    def test_xml(self):
        utils.run_data_file(self, 'xml', 'example_callback_provider.json')

class TestAccunulatedDataExampleMessageCallbackProvider(TestAccumulatedData):
    # @unittest.skip("")
    def test_xml(self):
        utils.run_data_file(self, 'xml', 'example_callback_provider.json')

class TestServiceExampleMessageCallbackProvider(TestService):
    # @unittest.skip("")
    def test_xml(self):
        utils.run_data_file(self, 'xml', 'example_callback_provider.json')

if __name__ == '__main__':
    helpers.run_tests()
