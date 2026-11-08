#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import helpers

from test_get_data import TestGetData
from test_driver import TestDriver
from test_get_accumulated_data import TestAccumulatedData
from test_service import TestService

class TestGetDataExampleMessageCallbackProvider(TestGetData):
    # @unittest.skip("")
    def test_xml(self):
        with open("bin/user/tests/integ/data/example_callback_provider.json", encoding="UTF-8") as file_pointer:
            self.runit('xml', file_pointer, check_results=True)

class TestDriverExamoleMessageCallbackProvider(TestDriver):
    # @unittest.skip("")
    def test_xml(self):
        with open("bin/user/tests/integ/data/example_callback_provider.json", encoding="UTF-8") as file_pointer:
            self.runit('xml', file_pointer, check_results=True)

class TestAccunulatedDataExampleMessageCallbackProvider(TestAccumulatedData):
    # @unittest.skip("")
    def test_xml(self):
        with open("bin/user/tests/integ/data/example_callback_provider.json", encoding="UTF-8") as file_pointer:
            self.runit('xml', file_pointer, check_results=True)

class TestServiceExampleMessageCallbackProvider(TestService):
    # @unittest.skip("")
    def test_xml(self):
        with open("bin/user/tests/integ/data/example_callback_provider.json", encoding="UTF-8") as file_pointer:
            self.runit('xml', file_pointer, check_results=True)

if __name__ == '__main__':
    helpers.run_tests()
