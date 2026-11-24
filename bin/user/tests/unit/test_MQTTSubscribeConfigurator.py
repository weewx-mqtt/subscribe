#
#    Copyright (c) 2023-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#


import helpers
import unittest
import mock

import contextlib
import io

import argparse

import test_weewx_stubs
from test_weewx_stubs import random_string, BaseTestClass
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

from user.mqttsubscribe import Configurator
from user.tests.configurator_helpers import create_options


def parse_args_expect_error(test_case, argv, expected_stderr):
    """ Parse argv and assert the expected argparse failure. """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    Configurator.add_parsers(subparsers)

    stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr):
        with test_case.assertRaises(SystemExit) as error:
            parser.parse_args(argv)

    test_case.assertEqual(error.exception.code, 2)
    test_case.assertIn(expected_stderr, stderr.getvalue())


def assert_configurator_error(test_case, options, expected_message):
    """ A mutually-exclusive option must be reported through parser.error. """
    mock_parser = mock.Mock()
    mock_parser.error = mock.Mock(side_effect=Exception("done"))
    with test_case.assertRaises(Exception):
        Configurator(mock_parser, options)
    mock_parser.error.assert_called_once_with(expected_message)


class TestEnableArgParse(unittest.TestCase):
    def test_driver_enable(self):
        parse_args_expect_error(self,
                                ['configure', 'driver', '--conf', random_string(), '--enable', 'true'],
                                "error: unrecognized arguments: --enable")

    #  @unittest.skip("Not sure what to do with this test.")
    def test_service_enable(self):
        parser = argparse.ArgumentParser()

        subparsers = parser.add_subparsers(dest='command')

        _ = Configurator.add_parsers(subparsers)

        _ = parser.parse_args(['configure', 'service', '--conf', random_string(), '--enable', 'true'])


class TestConfArgParse(unittest.TestCase):
    def test_create_example_conf(self):
        parse_args_expect_error(self, ['configure', '--create-example', '--conf', 'foo'], "--create-example: expected one argument")

    def test_service_missing_conf(self):
        parse_args_expect_error(self, ['configure', 'service'], "configure service: error: the following arguments are required: --conf")

    def test_driver_missing_conf(self):
        parse_args_expect_error(self, ['configure', 'driver'], "configure driver: error: the following arguments are required: --conf")

class TestMutuallyExclusiveOptions(unittest.TestCase):
    def __init__(self, args):
        self.options = None
        super().__init__(args)

    def setUp(self):
        self.options = ['--conf', random_string()]

    def run_mutually_exclusive(self, mutually_exclusive, error_msg):
        self.options.extend(mutually_exclusive)

        parser = argparse.ArgumentParser()

        _ = Configurator.add_common_options(parser)

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as error:
                _ = parser.parse_args(self.options)

        self.assertEqual(error.exception.code, 2)
        self.assertIn(error_msg, stderr.getvalue())

class TestMutuallyExclusiveExportOptions(TestMutuallyExclusiveOptions):
    def test_export_mutually_exclusive_with_print_configspec(self):
        self.run_mutually_exclusive(
            ['--export', random_string(), '--print-configspec', random_string()],
            "error: argument --print-configspec: not allowed with argument --export"
        )

    def test_export_mutually_exclusive_with_validate(self):
        self.run_mutually_exclusive(
            ['--export', random_string(), '--validate'],
            "error: argument --validate: not allowed with argument --export"
        )

    def test_export_mutually_exclusive_with_add_from(self):
        self.run_mutually_exclusive(
            ['--export', random_string(), '--add-from', random_string()],
            "error: argument --add-from: not allowed with argument --export"
        )

    def test_export_mutually_exclusive_with_remove(self):
        self.run_mutually_exclusive(
            ['--export', random_string(), '--remove'],
            "error: argument --remove: not allowed with argument --export"
        )

    def test_export_mutually_exclusive_with_replace_with(self):
        self.run_mutually_exclusive(
            ['--export', random_string(), '--replace-with', random_string()],
            "error: argument --replace-with: not allowed with argument --export"
        )

    def test_export_mutually_exclusive_with_update_from(self):
        self.run_mutually_exclusive(
            ['--export', random_string(), '--update-from', random_string()],
            "error: argument --update-from: not allowed with argument --export"
        )

class TestMutuallyExclusivePrintConfigSpecOptions(TestMutuallyExclusiveOptions):
    def test_print_configspec_mutually_exclusive_with_validate(self):
        self.run_mutually_exclusive(
            ['--print-configspec', random_string(), '--validate'],
            "error: argument --validate: not allowed with argument --print-configspec"
        )

    def test_print_configspec_mutually_exclusive_with_add_from(self):
        self.run_mutually_exclusive(
            ['--print-configspec', random_string(), '--add-from', random_string()],
            "error: argument --add-from: not allowed with argument --print-configspec"
        )

    def test_print_configspec_mutually_exclusive_with_remove(self):
        self.run_mutually_exclusive(
            ['--print-configspec', random_string(), '--remove'],
            "error: argument --remove: not allowed with argument --print-configspec"
        )

    def test_print_configspec_mutually_exclusive_with_replace_with(self):
        self.run_mutually_exclusive(
            ['--print-configspec', random_string(), '--replace-with', random_string()],
            "error: argument --replace-with: not allowed with argument --print-configspec"
        )

    def test_print_configspec_mutually_exclusive_with_update_from(self):
        self.run_mutually_exclusive(
            ['--print-configspec', random_string(), '--update-from', random_string()],
            "error: argument --update-from: not allowed with argument --print-configspec"
        )

class TestMutuallyExclusiveValidateOptions(TestMutuallyExclusiveOptions):
    def test_validate_mutually_exclusive_with_add_from(self):
        self.run_mutually_exclusive(
            ['--validate', random_string(), '--add-from', random_string()],
            "error: argument --add-from: not allowed with argument --validate"
        )

    def test_validate_mutually_exclusive_with_remove(self):
        self.run_mutually_exclusive(
            ['--validate', '--remove'],
            "error: argument --remove: not allowed with argument --validate"
        )

    def test_validate_mutually_exclusive_with_replace_with(self):
        self.run_mutually_exclusive(
            ['--validate', '--replace-with', random_string()],
            "error: argument --replace-with: not allowed with argument --validate"
        )

    def test_validate_mutually_exclusive_with_update_from(self):
        self.run_mutually_exclusive(
            ['--validate', '--update-from', random_string()],
            "error: argument --update-from: not allowed with argument --validate"
        )

class TestMutuallyExclusiveAddFromeOptions(TestMutuallyExclusiveOptions):
    def test_add_from_mutually_exclusive_with_remove(self):
        self.run_mutually_exclusive(
            ['--add-from', random_string(), '--remove'],
            "error: argument --remove: not allowed with argument --add-from"
        )

    def test_add_from_mutually_exclusive_with_replace_with(self):
        self.run_mutually_exclusive(
            ['--add-from', random_string(), '--replace-with', random_string()],
            "error: argument --replace-with: not allowed with argument --add-from"
        )

    def test_add_from_mutually_exclusive_with_update_from(self):
        self.run_mutually_exclusive(
            ['--add-from', random_string(), '--update-from', random_string()],
            "error: argument --update-from: not allowed with argument --add-from"
        )

class TestMutuallyExclusiveRemoveOptions(TestMutuallyExclusiveOptions):
    def test_remove_mutually_exclusive_with_replace_with(self):
        self.run_mutually_exclusive(
            ['--remove', '--replace-with', random_string()],
            "error: argument --replace-with: not allowed with argument --remove"
        )

    def test_remove_mutually_exclusive_with_update_from(self):
        self.run_mutually_exclusive(
            ['--remove', '--update-from', random_string()],
            "error: argument --update-from: not allowed with argument --remove"
        )

class TestMutuallyExclusiveReplaceWithOptions(TestMutuallyExclusiveOptions):
    def test_replace_with_mutually_exclusive_with_update_from(self):
        self.run_mutually_exclusive(
            ['--replace-with', random_string(), '--update-from', random_string()],
            "error: argument --update-from: not allowed with argument --replace-with"
        )

class TestInitConfigurator(BaseTestClass):
    def test_missing_primary_option(self):
        options = create_options(type=None,
                                 create_example=None,
                                 export=None,
                                 print_configspec=None,
                                 enable=None,
                                 validate=None,
                                 no_backup=True,
                                 add_from=None,
                                 remove=None,
                                 replace_with=None,
                                 update_from=None,
                                 output=None,
                                 conf=None)

        mock_parser = mock.Mock()
        _ = Configurator(mock_parser, options)

        mock_parser.error.assert_called_once_with("Either 'service|driver' or '--create-example' is required.")

    def test_output_mutually_exclusive_with_export(self):
        options = create_options(type=random_string(),
                                 create_example=None,
                                 export='bin/user/tests/data/output.conf',
                                 print_configspec=None,
                                 enable=None,
                                 validate=None,
                                 no_backup=None,
                                 add_from=None,
                                 remove=None,
                                 replace_with=None,
                                 update_from=None,
                                 output='bin/user/tests/data/output.conf',
                                 conf='bin/user/tests/data/weewx.conf')

        assert_configurator_error(self, options, "'--output' is mutually exclusive with '--export'.")

    def test_output_mutually_exclusive_with_print_configspec(self):
        options = create_options(type=random_string(),
                                 create_example=None,
                                 export=None,
                                 print_configspec='bin/user/tests/data/output.conf',
                                 enable=None,
                                 validate=None,
                                 no_backup=None,
                                 add_from=None,
                                 remove=None,
                                 replace_with=None,
                                 update_from=None,
                                 output='bin/user/tests/data/output.conf',
                                 conf='bin/user/tests/data/weewx.conf')

        assert_configurator_error(self, options, "'--output' is mutually exclusive with '--print-configspec'.")

    def test_output_mutually_exclusive_with_validate(self):
        options = create_options(type=random_string(),
                                 create_example=None,
                                 export=None,
                                 print_configspec=None,
                                 enable=None,
                                 validate=True,
                                 no_backup=None,
                                 add_from=None,
                                 remove=None,
                                 replace_with=None,
                                 update_from=None,
                                 output='bin/user/tests/data/output.conf',
                                 conf='bin/user/tests/data/weewx.conf')

        assert_configurator_error(self, options, "'--output' is mutually exclusive with '--validate'.")

    def test_enable_mutually_exclusive_with_export(self):
        options = create_options(type='service',
                                 create_example=None,
                                 export='bin/user/tests/data/output.conf',
                                 print_configspec=None,
                                 enable=True,
                                 validate=None,
                                 no_backup=None,
                                 add_from=None,
                                 remove=None,
                                 replace_with=None,
                                 update_from=None,
                                 output=None,
                                 conf=None)

        assert_configurator_error(self, options, "'--enable' is mutually exclusive with '--export'.")

    def test_enable_mutually_exclusive_with_print_configspec(self):
        options = create_options(type='service',
                                 create_example=None,
                                 export=None,
                                 print_configspec='bin/user/tests/data/output.conf',
                                 enable=True,
                                 validate=None,
                                 no_backup=None,
                                 add_from=None,
                                 remove=None,
                                 replace_with=None,
                                 update_from=None,
                                 output=None,
                                 conf='bin/user/tests/data/weewx.conf')

        assert_configurator_error(self, options, "'--enable' is mutually exclusive with '--print-configspec'.")

    def test_enable_mutually_exclusive_with_validate(self):
        options = create_options(type='service',
                                 create_example=None,
                                 export=None,
                                 print_configspec=None,
                                 enable=True,
                                 validate=True,
                                 no_backup=None,
                                 add_from=None,
                                 remove=None,
                                 replace_with=None,
                                 update_from=None,
                                 output=None,
                                 conf='bin/user/tests/data/weewx.conf')

        assert_configurator_error(self, options, "'--enable' is mutually exclusive with '--validate'.")

    def test_no_backup_mutually_exclusive_with_export(self):
        options = create_options(type=random_string(),
                                 create_example=None,
                                 export='bin/user/tests/data/output.conf',
                                 print_configspec=None,
                                 enable=None,
                                 validate=None,
                                 no_backup=True,
                                 add_from=None,
                                 remove=None,
                                 replace_with=None,
                                 update_from=None,
                                 output=None,
                                 conf='bin/user/tests/data/weewx.conf')

        assert_configurator_error(self, options, "'--no-backup' is mutually exclusive with '--export'.")

    def test_no_backup_mutually_exclusive_with_print_configspec(self):
        options = create_options(type=random_string(),
                                 create_example=None,
                                 export=None,
                                 print_configspec='bin/user/tests/data/output.conf',
                                 enable=None,
                                 validate=None,
                                 no_backup=True,
                                 add_from=None,
                                 remove=None,
                                 replace_with=None,
                                 update_from=None,
                                 output=None,
                                 conf=None)

        assert_configurator_error(self, options, "'--no-backup' is mutually exclusive with '--print-configspec'.")

    def test_no_backup_mutually_exclusive_with_validate(self):
        options = create_options(type=random_string(),
                                 create_example=None,
                                 export=None,
                                 print_configspec=None,
                                 enable=None,
                                 validate=True,
                                 no_backup=True,
                                 add_from=None,
                                 remove=None,
                                 replace_with=None,
                                 update_from=None,
                                 output=None,
                                 conf='bin/user/tests/data/weewx.conf')

        assert_configurator_error(self, options, "'--no-backup' is mutually exclusive with '--validate'.")

class TestRunConfigurator(BaseTestClass):
    '''
    These are not 'real' tests. The results are not checked. The only check that the
    options run to completion.
    '''
    def test_create_example(self):
        options = create_options(type=None,
                                 create_example='bin/user/tests/data/output.conf',
                                 export=None,
                                 print_configspec=None,
                                 enable=None,
                                 validate=None,
                                 no_backup=True,
                                 add_from=None,
                                 remove=None,
                                 replace_with=None,
                                 update_from=None,
                                 output='bin/user/tests/data/output.conf',
                                 conf=None)

        SUT = Configurator(None, options)

        SUT.run()

    def test_export(self):
        options = create_options(type='driver',
                                 create_example=None,
                                 export='bin/user/tests/data/output.conf',
                                 print_configspec=None,
                                 enable=None,
                                 validate=None,
                                 no_backup=None,
                                 add_from=None,
                                 remove=None,
                                 replace_with=None,
                                 update_from=None,
                                 output=None,
                                 top_level=None,
                                 conf='bin/user/tests/data/weewx.conf')

        SUT = Configurator(None, options)

        SUT.run()

    def test_print_configspec(self):
        options = create_options(type='driver',
                                 create_example=None,
                                 export=None,
                                 print_configspec='bin/user/tests/data/output.conf',
                                 enable=None,
                                 validate=None,
                                 no_backup=None,
                                 add_from=None,
                                 remove=None,
                                 replace_with=None,
                                 update_from=None,
                                 output=None,
                                 conf=None,
                                 top_level=None)

        SUT = Configurator(None, options)

        SUT.run()

    def test_validate(self):
        options = create_options(type='driver',
                                 create_example=None,
                                 export=None,
                                 print_configspec=None,
                                 enable=None,
                                 validate=True,
                                 no_backup=None,
                                 add_from=None,
                                 remove=None,
                                 replace_with=None,
                                 update_from=None,
                                 output=None,
                                 top_level=None,
                                 conf='bin/user/tests/data/weewx.conf')

        SUT = Configurator(None, options)

        SUT.run()

    def test_add_from(self):
        options = create_options(type='driver',
                                 create_example=None,
                                 export=None,
                                 print_configspec=None,
                                 enable=None,
                                 validate=None,
                                 no_backup=True,
                                 add_from='bin/user/tests/data/mqttsubscribe.conf',
                                 remove=None,
                                 replace_with=None,
                                 update_from=None,
                                 top_level=None,
                                 output='bin/user/tests/data/output.conf',
                                 conf='bin/user/tests/data/weewx.conf')

        SUT = Configurator(None, options)

        SUT.run()

    def test_remove(self):
        options = create_options(type='driver',
                                 create_example=None,
                                 export=None,
                                 print_configspec=None,
                                 enable=None,
                                 validate=None,
                                 no_backup=True,
                                 add_from=None,
                                 remove=True,
                                 replace_with=None,
                                 update_from=None,
                                 top_level=None,
                                 output='bin/user/tests/data/output.conf',
                                 conf='bin/user/tests/data/weewx.conf')

        SUT = Configurator(None, options)

        SUT.run()

    def test_replace_with(self):
        options = create_options(type='driver',
                                 create_example=None,
                                 export=None,
                                 print_configspec=None,
                                 enable=None,
                                 validate=None,
                                 no_backup=True,
                                 add_from=None,
                                 remove=None,
                                 replace_with='bin/user/tests/data/mqttsubscribe.conf',
                                 update_from=None,
                                 output='bin/user/tests/data/output.conf',
                                 conf='bin/user/tests/data/weewx.conf',
                                 top_level=None)

        SUT = Configurator(None, options)

        SUT.run()

    def test_update_from(self):
        options = create_options(type='driver',
                                 create_example=None,
                                 export=None,
                                 print_configspec=None,
                                 enable=None,
                                 validate=None,
                                 no_backup=True,
                                 add_from=None,
                                 remove=None,
                                 replace_with=None,
                                 top_level=None,
                                 update_from='bin/user/tests/data/mqttsubscribe.conf',
                                 output='bin/user/tests/data/output.conf',
                                 conf='bin/user/tests/data/weewx.conf')

        SUT = Configurator(None, options)

        SUT.run()

if __name__ == '__main__':
    helpers.run_tests()
