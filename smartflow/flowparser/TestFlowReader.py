"""

@author: Dylan
"""

import csv
import os
import re

from smartflow.SmartFlow import SmartFlow
from smartflow.flowparser.TestFlowSection import TestFlowSection
from smartflow.flowparser.Utils import SECTION_KEYS


class TestFlowReader(object):
    """
    classdocs
    """

    section_state = "header"
    section_list = []

    testsuites_list = []
    testmethods_list = []
    testmethodparameters_list = []

    def __init__(self, tf_input=None):
        """
        Constructor
        """
        # super().__init__()
        self.working_path = os.path.dirname(__file__)

        if tf_input is None:
            self.tf_input = os.path.join(self.working_path, '..', '.sys', 'empty.ttf')
        else:
            self.tf_input = tf_input

        self.read()

    def __read_ascii_testflow(self):
        section = TestFlowSection("header")

        with open(self.tf_input, 'r', newline='') as srcFile:
            for line in srcFile:
                line = line.strip('\n')
                if self.section_state in ("header", "end"):
                    if line in SECTION_KEYS:
                        self.section_list.append(section.section_name)
                        self.section_list.append(section)
                        section = TestFlowSection(line)
                        self.section_state = section.section_name
                elif self.section_state in SECTION_KEYS:
                    if line == "end":
                        self.section_state = "end"

                # Add ascii line into current section
                section.add_ascline(line)

            # Add the last section_state
            self.section_list.append(section.section_name)
            self.section_list.append(section)

        self.__read_asc_testflow()

    def __populate_section_list(self):
        if self.tf_input[-5:] == '.csv/':
            self.__read_csv_testflow()
        else:
            self.__read_ascii_testflow()

    def __read_csv_testflow(self):
        section = None
        folder_path = os.path.join(os.getcwd(), self.tf_input)

        for section_name in SECTION_KEYS:
            section = TestFlowSection(section_name)
            filename = os.path.join(folder_path, section_name + '.csv')
            with open(filename, 'r', newline='') as srcFile:
                csvreader = csv.reader(srcFile, dialect='excel')
                for line in csvreader:
                    section.add_csvline(line)
            section.syncup_asclines()

            self.section_list.append(section.section_name)
            self.section_list.append(section)

    def __read_asc_testflow(self):
        for section in self.section_list[1::2]:
            if section.section_name in ("information", "bin_disconnect"):
                for line in section.asclines:
                    matcher = re.match('(\s+)(.*)( = )(.*)(;)', line)
                    if matcher:
                        prefix = matcher.group(1)
                        key = matcher.group(2)
                        equal = matcher.group(3)
                        value = matcher.group(4)
                        postfix = matcher.group(5)
                        section.add_csvline([prefix, key, equal, value, postfix])
                    else:
                        section.add_csvline([line])
            elif section.section_name in "declarations":
                for line in section.asclines:
                    matcher = re.match('(@)(\w+)( = )(.*)(;)', line)
                    if matcher:
                        prefix = matcher.group(1)
                        key = matcher.group(2)
                        equal = matcher.group(3)
                        value = matcher.group(4)
                        postfix = matcher.group(5)
                        section.add_csvline([prefix, key, equal, value, postfix])
                    else:
                        section.add_csvline([line])
            elif section.section_name in "implicit_declarations":
                for line in section.asclines:
                    section.add_csvline([line])
            elif section.section_name in "flags":
                for line in section.asclines:
                    matcher = re.match('(user\s+)(.*)( = )(.*)(;)', line)
                    if matcher:
                        prefix = matcher.group(1)
                        key = matcher.group(2)
                        equal = matcher.group(3)
                        value = matcher.group(4)
                        postfix = matcher.group(5)
                        section.add_csvline([prefix, key, equal, value, postfix])
                    else:
                        matcher = re.match('()(\w+)( = )(.*)(;)', line)
                        if matcher:
                            prefix = matcher.group(1)
                            key = matcher.group(2)
                            equal = matcher.group(3)
                            value = matcher.group(4)
                            postfix = matcher.group(5)
                            section.add_csvline([prefix, key, equal, value, postfix])
                        else:
                            section.add_csvline([line])
            elif section.section_name in "testmethodparameters":
                for line in section.asclines:
                    matcher = re.match('(tm_)(\d+)(:)', line)
                    if matcher:
                        prefix = matcher.group(1)
                        tm_id = matcher.group(2)
                        postfix = matcher.group(3)
                        section.add_csvline([prefix, tm_id, postfix])
                    else:
                        matcher = re.match('(\s+")(.*)(" = ")(.*)(";)', line)
                        if matcher:
                            prefix = matcher.group(1)
                            key = matcher.group(2)
                            equal = matcher.group(3)
                            value = matcher.group(4)
                            postfix = matcher.group(5)
                            section.add_csvline([prefix, key, equal, value, postfix])
                        else:
                            section.add_csvline([line])
            elif section.section_name in "testmethods":
                for line in section.asclines:
                    matcher = re.match('(tm_)(\d+)(:)', line)
                    if matcher:
                        prefix = matcher.group(1)
                        tm_id = matcher.group(2)
                        postfix = matcher.group(3)
                        section.add_csvline([prefix, tm_id, postfix])
                    else:
                        matcher = re.match('(\s+)(testmethod_class)( = ")(.*)(";)', line)
                        if matcher:
                            prefix = matcher.group(1)
                            key = matcher.group(2)
                            equal = matcher.group(3)
                            value = matcher.group(4)
                            postfix = matcher.group(5)
                            section.add_csvline([prefix, key, equal, value, postfix])
                        else:
                            section.add_csvline([line])
            elif section.section_name in "testmethodlimits":
                for line in section.asclines:
                    matcher = re.match('(tm_)(\d+)(:)', line)
                    if matcher:
                        prefix = matcher.group(1)
                        tm_id = matcher.group(2)
                        postfix = matcher.group(3)
                        section.add_csvline([prefix, tm_id, postfix])
                    else:
                        matcher = re.match('(\s+")(.*)(" = )(.*)(;)', line)
                        if matcher:
                            prefix = matcher.group(1)
                            testname = matcher.group(2)
                            equal = matcher.group(3)
                            value = matcher.group(4)
                            postfix = matcher.group(5)
                            section.add_csvline([prefix, testname, equal, value, postfix])
                        else:
                            section.add_csvline([line])
            elif section.section_name in "test_suites":
                for line in section.asclines:
                    matcher = re.match('(\w+)(:)', line)
                    if matcher:
                        testsuite_name = matcher.group(1)
                        postfix = matcher.group(2)
                        section.add_csvline([testsuite_name, postfix])
                    else:
                        matcher = re.match('(\s*)(\w+)(\s+= )(.*)(;)', line)
                        if matcher:
                            prefix = matcher.group(1)
                            key = matcher.group(2)
                            equal = matcher.group(3)
                            value = matcher.group(4)
                            postfix = matcher.group(5)
                            section.add_csvline([prefix, key, equal, value, postfix])
                        else:
                            section.add_csvline([line])
            elif section.section_name in "test_flow":
                for line in section.asclines:
                    section.add_csvline([line])
            elif section.section_name in "binning":
                for line in section.asclines:
                    section.add_csvline([line])
            elif section.section_name in "hardware_bin_descriptions":
                for line in section.asclines:
                    matcher = re.match('(\s+)(\d+)( = )(.*)(;)', line)
                    if matcher:
                        prefix = matcher.group(1)
                        key = matcher.group(2)
                        equal = matcher.group(3)
                        value = matcher.group(4)
                        postfix = matcher.group(5)
                        section.add_csvline([prefix, key, equal, value, postfix])
                    else:
                        section.add_csvline([line])
            elif section.section_name in "context":
                for line in section.asclines:
                    matcher = re.match('(context_)(\w+)( = )(.*)(;)', line)
                    if matcher:
                        prefix = matcher.group(1)
                        key = matcher.group(2)
                        equal = matcher.group(3)
                        value = matcher.group(4)
                        postfix = matcher.group(5)
                        section.add_csvline([prefix, key, equal, value, postfix])
                    else:
                        section.add_csvline([line])
            else:
                for line in section.asclines:
                    section.add_csvline([line])

            # Update ascii asclines
            section.syncup_asclines()
            self.update_section_list(section)

    def __populate_testsuites_list(self):
        state = "header"
        test_suites_section = self.get_section_by_section_name("test_suites")
        testsuite = []

        for line in test_suites_section.csvlines:
            if state == 'header':
                if len(line) > 1 and line[1] == ':':
                    testsuite_name = line[0]
                    testsuite_tm_id = ''
                    testsuite = [testsuite_name, testsuite_tm_id]
                    state = 'testsuite'
            elif state == 'testsuite':
                if len(line) > 4 and line[4] == ';':
                    param = line[1]
                    value = line[3]
                    testsuite.append(param)
                    testsuite.append(value)
                    if param == 'override_testf':
                        testsuite[1] = value.lstrip('tm_')
                elif len(line) > 1 and line[1] == ':':
                    self.testsuites_list.append(testsuite)
                    testsuite_name = line[0]
                    testsuite_tm_id = ''
                    testsuite = [testsuite_name, testsuite_tm_id]

        # Add the last testsuite
        self.testsuites_list.append(testsuite)

    def __populate_testmethods_list(self):
        testmethods_section = self.get_section_by_section_name("testmethods")
        for line in testmethods_section.csvlines:
            if len(line) > 2 and line[0] == 'tm_':
                self.testmethods_list.append(line[1])
            elif len(line) > 4 and line[1] == 'testmethod_class':
                self.testmethods_list.append(line[3])

    def __populate_testmethodparameters_list(self):
        state = "header"
        testmethodparameters_section = self.get_section_by_section_name('testmethodparameters')
        parameters = []

        for line in testmethodparameters_section.csvlines:
            if state == 'header':
                if len(line) > 2 and line[0] == 'tm_':
                    tm_id = line[1]
                    parameters.append(tm_id)
                    parameters.append(self.get_testmethod_by_tm_id(tm_id))
                    state = 'parameters'
            elif state == 'parameters':
                if len(line) > 4 and line[4] == '";':
                    param = line[1]
                    value = line[3]
                    parameters.append(param)
                    parameters.append(value)
                elif len(line) > 2 and line[0] == 'tm_':
                    self.testmethodparameters_list.append(parameters)
                    tm_id = line[1]
                    parameters = [tm_id, self.get_testmethod_by_tm_id(tm_id)]

        # Add the last parameters
        self.testmethodparameters_list.append(parameters)

    def get_section_name_list(self):
        return self.section_list[1::2]

    def get_section_by_section_name(self, section_name):
        section_index = self.section_list.index(section_name) + 1
        section = self.section_list[section_index]
        return section

    def get_testsuites_name_list(self):
        testsuites_name_list = []
        for testsuite in self.testsuites_list:
            testsuites_name_list.append(testsuite[0])
        return testsuites_name_list

    def get_testsuite_by_testsuite_name(self, testsuite_name):
        for testsuite in self.testsuites_list:
            if testsuite_name == testsuite[0]:
                return testsuite

    def get_tm_id_by_testsuite_name(self, testsuite_name):
        tm_id = self.get_testsuite_by_testsuite_name(testsuite_name)[1]
        return tm_id

    def get_testmethod_by_tm_id(self, tm_id):
        testmethod_index = self.testmethods_list.index(tm_id) + 1
        testmethod = self.testmethods_list[testmethod_index]
        return testmethod

    def get_testmethod_by_testsuite_name(self, testsuite_name):
        tm_id = self.get_tm_id_by_testsuite_name(testsuite_name)
        testmethod_name = self.get_testmethod_by_tm_id(tm_id)
        return testmethod_name

    def get_testsuite_name_by_tm_id(self, tm_id):
        testsuite_name = ''
        for testsuite in self.testsuites_list:
            if tm_id == testsuite[1]:
                testsuite_name = testsuite[0]
                return testsuite_name

    def get_testmethodparameters_by_tm_id(self, tm_id):
        for testmethodparameters in self.testmethodparameters_list:
            if tm_id == testmethodparameters[0]:
                return testmethodparameters

    def get_testmethodparameters_by_testsuite_name(self, testsuite_name):
        tm_id = self.get_tm_id_by_testsuite_name(testsuite_name)
        testmethodparameters = self.get_testmethodparameters_by_tm_id(tm_id)
        return testmethodparameters

    def get_testmethod_parameter_by_testsuite_name(self, testsuite_name, param):
        testmethodparameters = self.get_testmethodparameters_by_testsuite_name(testsuite_name)[2:]
        value_index = testmethodparameters.index(param) + 1
        value = self.testmethodparameters[value_index]
        return value

    def get_testsuite_property(self, testsuite, prop):
        if prop in testsuite:
            value = testsuite[testsuite.index(prop) + 1]
            return value
        else:
            return None

    def update_section_list(self, section):
        section_index = self.section_list.index(section.section_name) + 1
        self.section_list[section_index] = section

    def read(self):
        self.__populate_section_list()
        self.__populate_testsuites_list()
        self.__populate_testmethods_list()
        self.__populate_testmethodparameters_list()
