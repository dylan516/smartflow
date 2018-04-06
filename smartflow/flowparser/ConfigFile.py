"""

@author: Dylan
"""
import os
import shutil

import sys
import xlrd

from smartflow.flowparser.Utils import warning_msg, error_msg, info_msg, \
    cell2str


class ConfigFile(object):
    """
    """

    def __init__(self, config_file):
        """
        Constructor
        """
        self.working_path = os.path.dirname(__file__)
        self.config_file = os.path.join(os.getcwd(), config_file)

        # Create config file if not exist
        if not os.path.exists(self.config_file):
            src = os.path.join(self.working_path, '..', '.sys', 'config_template.xls')
            shutil.copy(src, self.config_file)
            info_msg('Config file "' + self.config_file + '" is missing, creating from template.')
            sys.exit()

        self.load_config_file()

    # def create_config_file(self):
    #     src = os.path.join(self.working_path, '.sys', 'config_template.xls')
    #     config_file = os.path.join(os.getcwd(), self.option_value_dict['--new'].rstrip('.xls') + '.xls')
    #     shutil.copy(src, config_file)
    #     info_msg('Create config file "' + config_file + '" from template.')
    #     sys.exit()

    def load_config_file(self):
        self.wb_selectors = xlrd.open_workbook(self.config_file)

        self.configuration = self.__load_configuration()
        self.parameters_selector = self.__load_parameters_selector()
        self.timing_selector = self.__load_timing_selector()
        self.level_selector = self.__load_level_selector()
        self.testflow_sequence = self.__load_testflow_sequence()
        self.floweditor = self.__load_floweditor()

    def __load_configuration(self):
        configuration = {}
        sheet_configuration = self.wb_selectors.sheet_by_name('configuration')

        for rowx in range(sheet_configuration.nrows):
            row = sheet_configuration.row_values(rowx)
            if rowx < 1:
                continue
            if row[0] != '':
                configuration[row[0]] = row[1]
        return configuration

    def __load_parameters_selector(self):
        parameters_selector = {}
        sheet_parameters = self.wb_selectors.sheet_by_name('tm_parameters')

        tm_parameters = []  # [testmethod_name, selector, param1, value1, ...'

        for rowx in range(sheet_parameters.nrows):
            row = sheet_parameters.row_values(rowx)
            if rowx < 2:
                continue

            testmethod_name = row[0]
            selector = row[1]
            if testmethod_name == '' and selector == '':
                continue

            tm_parameters = []
            for param_index in range(2, len(row), 2):
                if row[param_index]:
                    tm_parameters.append(cell2str(row[param_index]))
                    tm_parameters.append(cell2str(row[param_index + 1]))
            key = testmethod_name + '::' + selector
            parameters_selector[key] = tm_parameters
        return parameters_selector

    def __load_timing_selector(self):
        timing_selector = {}
        sheet_timing = self.wb_selectors.sheet_by_name('timing')

        for rowx in range(sheet_timing.nrows):
            row = sheet_timing.row_values(rowx)
            if rowx < 2:
                continue
            if row[0] != '':
                timing_selector[row[0]] = row[1:4]
        return timing_selector

    def __load_level_selector(self):
        level_selector = {}
        sheet_level = self.wb_selectors.sheet_by_name('level')

        for rowx in range(sheet_level.nrows):
            row = sheet_level.row_values(rowx)
            if rowx < 2:
                continue
            if row[0] != '':
                level_selector[row[0]] = row[1:4]
        return level_selector

    def __load_testflow_sequence(self):
        testflow_sequence = []
        sheet_testflow_sequence = self.wb_selectors.sheet_by_name('testflow')
        header = []

        for rowx in range(sheet_testflow_sequence.nrows):
            row = sheet_testflow_sequence.row_values(rowx)
            if rowx == 0:
                header = row
                continue
            elif rowx < 2:
                continue

            row_dict = {}
            for index in range(len(row)):
                row_dict[header[index]] = row[index]
            if ('type' in row_dict) and (row_dict['type'].strip() != ''):
                testflow_sequence.append(row_dict)
        return testflow_sequence

    def __load_floweditor(self):
        floweditor = []
        sheet_floweditor = self.wb_selectors.sheet_by_name('floweditor')
        header = []

        for rowx in range(sheet_floweditor.nrows):
            row = sheet_floweditor.row_values(rowx)
            if rowx == 0:
                header = row
                continue
            elif rowx < 2:
                continue

            row_dict = {}
            for index in range(len(row)):
                row_dict[header[index]] = row[index]
            if ('testsuite_name_regex' in row_dict) and (row_dict['testsuite_name_regex'].strip() != ''):
                floweditor.append(row_dict)
        return floweditor

    def get_config(self, keyword):
        if keyword in self.configuration:
            value = self.configuration[keyword]
        else:
            warning_msg('Keyword "' + keyword + '" is not defined in "configuration" sheet')
            value = None
        return value

    def get_parameters(self, testmethod_name, selector):
        key = testmethod_name + '::' + selector

        if key in self.parameters_selector:
            return self.parameters_selector[key]
        else:
            error_msg('testmethod_name ' + str(testmethod_name) + ' not defined.')
            error_msg('selector ' + str(selector) + ' not defined.')

    def get_timing(self, selector):
        if selector in self.timing_selector:
            return self.timing_selector[selector]
        else:
            return ['', '', '']

    def get_level(self, selector):
        if selector in self.level_selector:
            return self.level_selector[selector]
        else:
            return ['', '', '']
