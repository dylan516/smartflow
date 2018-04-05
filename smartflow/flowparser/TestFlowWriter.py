'''

@author: Dylan

'''
import csv
import os

from smartflow.flowparser.TestFlowSection import TestFlowSection
from smartflow.flowparser.Utils import SEPARATOR


class TestFlowWriter(object):
    '''
    classdocs
    '''

    def __init__(self, reader, config=None):
        '''
        Constructor
        '''
        super().__init__()
        self.reader = reader
        self.config = config

    def get_tm_parameters_by_selector(self, tm_prameters_lut, testmethod_name, parameters_selector):
        key = testmethod_name + '::' + parameters_selector
        return tm_prameters_lut[key]

    def update_testsuite(self, testsuite, properties_dict):
        prop_list = ['override_tim_equ_set', 'override_lev_equ_set',
                     'override_tim_spec_set', 'override_lev_spec_set',
                     'override_timset', 'override_levset',
                     'override_seqlbl', 'override_testf', 'comment', 'local_flags']

        properties_list = []
        prop_dict = {}

        for prop in prop_list:
            # Get value from config.csv
            if (prop in properties_dict):
                value = str(properties_dict[prop])
                if (value.strip() == ''):
                    value = self.reader.get_testsuite_property(testsuite, prop)
                    if (prop == 'override_tim_equ_set'):
                        value = None
            else:
                # Get existed properties
                value = self.reader.get_testsuite_property(testsuite, prop)
            prop_dict[prop] = value

            if (value != None):
                properties_list.append(prop)
                properties_list.append(value)

        rest_properties = testsuite[testsuite.index('local_flags') + 2:]
        updated_testsuite = testsuite[0:4] + properties_list + rest_properties
        return updated_testsuite

    def update_testsuite_list(self, testsuite_name, properties_dict):
        for index in range(len(self.reader.testsuites_list)):
            testsuite = self.reader.testsuites_list[index]
            if (testsuite[0] == testsuite_name):
                updated_testsuite = self.update_testsuite(testsuite, properties_dict)
                self.reader.testsuites_list[index] = updated_testsuite

    def update_testmethods_list(self, testsuite_name, testmethod):
        tm_id = self.reader.get_tm_id_by_testsuite_name(testsuite_name)
        testmethod_index = self.reader.testmethods_list.index(tm_id) + 1
        self.reader.testmethods_list[testmethod_index] = testmethod

    def update_testmethodparameters_list(self, testsuite_name, testmethod_name, parameters_selector):
        testmethodparameters = []

        tm_id = self.reader.get_tm_id_by_testsuite_name(testsuite_name)
        predefined_tm_parameters = self.config.get_parameters(testmethod_name, parameters_selector)

        testmethodparameters.append(tm_id)
        testmethodparameters.append(testmethod_name)
        testmethodparameters += predefined_tm_parameters

        for index in range(len(self.reader.testmethodparameters_list)):
            if (self.reader.testmethodparameters_list[index][0] == testmethodparameters[0]):
                self.reader.testmethodparameters_list[index] = testmethodparameters

    def update_testsuites_section(self):
        section = TestFlowSection('test_suites')
        section.add_csvline([section.section_name])

        for testsuite in self.reader.testsuites_list:
            section.add_csvline([testsuite[0], ':'])
            for param_index in range(2, len(testsuite), 2):
                value_index = param_index + 1
                if (testsuite[param_index] == 'override'):
                    section.add_csvline(['  ', testsuite[param_index], ' = ', testsuite[value_index], ';'])
                elif (testsuite[param_index] == 'local_flags'):
                    section.add_csvline(['', testsuite[param_index], '  = ', testsuite[value_index], ';'])
                else:
                    section.add_csvline([' ', testsuite[param_index], ' = ', testsuite[value_index], ';'])
        section.add_csvline(['end'])
        section.add_csvline([SEPARATOR])
        section.syncup_asclines()
        self.reader.update_section_list(section)

    def update_testmethods_section(self):
        section = TestFlowSection('testmethods')
        section.add_csvline([section.section_name])

        for tm_id_index in range(0, len(self.reader.testmethods_list), 2):
            testmethod_index = tm_id_index + 1
            section.add_csvline(['tm_', self.reader.testmethods_list[tm_id_index], ':'])
            section.add_csvline(
                ['  ', 'testmethod_class', ' = "', self.reader.testmethods_list[testmethod_index], '";'])
        section.add_csvline(['end'])
        section.add_csvline([SEPARATOR])
        section.syncup_asclines()
        self.reader.update_section_list(section)

    def update_testmethodparameters_section(self):
        section = TestFlowSection('testmethodparameters')
        section.add_csvline([section.section_name])

        for tm_parameters in self.reader.testmethodparameters_list:
            section.add_csvline(['tm_', tm_parameters[0], ':'])
            for param_index in range(2, len(tm_parameters), 2):
                value_index = param_index + 1
                if (tm_parameters[param_index].strip()):
                    section.add_csvline(['  "', tm_parameters[param_index], '" = "', tm_parameters[value_index], '";'])
        section.add_csvline(['end'])
        section.add_csvline([SEPARATOR])
        section.syncup_asclines()
        self.reader.update_section_list(section)

    def set_testmethod_parameter_by_testsuite_name(self, testsuite_name, param, value):
        testmethodparameters = self.get_testmethodparameters_by_testsuite_name(testsuite_name)[2:]
        value_index = testmethodparameters.index(param) + 1
        self.testmethodparameters[value_index] = value

    def create_header_section(self):
        section = TestFlowSection('header')
        return section

    def create_information_section(self):
        section = TestFlowSection('information')
        return section

    def create_declarations_section(self):
        section = TestFlowSection('declarations')
        return section

    def create_implicit_declarations_section(self):
        section = TestFlowSection('implicit_declarations')
        return section

    def create_flags_section(self):
        section = TestFlowSection('flags')
        return section

    def create_testmethodparameters_section(self, testmethodparameters_list):
        section = TestFlowSection('testmethodparameters')
        # Add section_name
        line = [section.section_name]
        section.add_csvline(line)

        # Add testmethod_parameters
        for testmethod_parameters in testmethodparameters_list:
            # Add tm_id
            tm_id = testmethod_parameters[0]
            line = ['tm_', tm_id, ':']
            section.add_csvline(line)
            # Add parameters
            for index in range(2, len(testmethod_parameters), 2):
                param = testmethod_parameters[index]
                value = testmethod_parameters[index + 1]
                line = ['  "', param, '" = "', value, '";']
                section.add_csvline(line)

        # Add 'end' and seperator
        section.add_csvline(['end'])
        section.add_csvline([SEPARATOR])

        section.syncup_asclines();
        return section

    def create_testmethodlimits_section(self):
        section = TestFlowSection('testmethodlimits')
        return section

    def create_testmethods_section(self, testmethod_list):
        section = TestFlowSection('testmethods')
        # Add section_name
        line = [section.section_name]
        section.add_csvline(line)

        # Add testmethods
        for index in range(0, len(testmethod_list), 2):
            tm_id = testmethod_list[index]
            testmethod_name = testmethod_list[index + 1]
            line = ['tm_', tm_id, ':']
            section.add_csvline(line)
            line = ['  ', 'testmethod_class', ' = "', testmethod_name, '";']
            section.add_csvline(line)

        # Add 'end' and seperator
        section.add_csvline(['end'])
        section.add_csvline([SEPARATOR])

        section.syncup_asclines();
        return section

    def create_test_suites_section(self, testsuite_list):
        section = TestFlowSection('test_suites')
        # Add section_name
        line = [section.section_name]
        section.add_csvline(line)

        # Add testsuite
        for testsuite in testsuite_list:
            # Add testsuite_name
            testsuite_name = testsuite[0]
            line = [testsuite_name, ':']
            section.add_csvline(line)
            # Add testsuite properties
            for index in range(2, len(testsuite), 2):
                prop = testsuite[index]
                value = str(testsuite[index + 1])
                prefix = ' '
                if (prop == 'override'):
                    prefix = '  '
                elif (prop == 'local_flags'):
                    prefix = ''

                if ('set' in prop and value.strip() == ''):
                    continue
                else:
                    line = [prefix, prop, ' = ', value, ';']
                    section.add_csvline(line)

        # Add 'end' and seperator
        section.add_csvline(['end'])
        section.add_csvline([SEPARATOR])

        section.syncup_asclines();
        return section

    def create_bin_disconnect_section(self):
        section = TestFlowSection('bin_disconnect')
        return section

    def create_testflow_section(self, testflow):
        section = TestFlowSection('test_flow')
        # Add section_name
        line = [section.section_name]
        section.add_csvline(line)

        # Add dummy line
        section.add_ascline([''])

        # Add testflow
        for line in str(testflow).split('\n'):
            section.add_csvline(line)

        # Add 'end' and seperator
        section.add_csvline(['end'])
        section.add_csvline([SEPARATOR])

        section.syncup_asclines();
        return section

    def create_binning_section(self):
        section = TestFlowSection('binning')
        return section

    def create_context_section(self):
        section = TestFlowSection('context')
        return section

    def create_hardware_bin_descriptions_section(self):
        section = TestFlowSection('hardware_bin_descriptions')
        return section

    def write(self, tf_output, section_list):
        if (tf_output.endswith('.csv')):
            self.__write_csv_testflow(tf_output, section_list)
        else:
            self.__write_ascii_testflow(tf_output, section_list)

    def __write_csv_testflow(self, tf_output, section_list):
        folder_path = os.path.abspath(tf_output)

        if (not os.path.exists(folder_path)):
            os.makedirs(folder_path)

        for section in section_list[1::2]:
            filename = os.path.join(folder_path, section.section_name + '.csv')
            with open(filename, 'w', newline='') as dstFile:
                csvwriter = csv.writer(dstFile, dialect='excel', quoting=csv.QUOTE_ALL, lineterminator='\n')
                csvwriter.writerows(section.csvlines)

    def __write_ascii_testflow(self, tf_output, section_list):
        with open(tf_output, 'w', newline='') as dstFile:
            for section in section_list[1::2]:
                dstFile.write('\n'.join(section.asclines) + '\n')
