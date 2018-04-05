"""

@author: Dylan

"""

import re
import shutil
from optparse import OptionParser

import sys

from smartflow.flowparser.ConfigFile import ConfigFile
from smartflow.flowparser.TestFlowReader import TestFlowReader
from smartflow.flowparser.TestFlowWriter import TestFlowWriter
from smartflow.flowparser.Utils import popolate_local_flags_string, error_msg, \
    info_msg, warning_msg


class TestFlowEditor(object):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.__parse_options()

    def __parse_options(self):
        description = "Edit testflow primary/testmethod/flags with xls config file."

        parser = OptionParser(description=description)
        parser.add_option("-i", dest="tf_input", metavar=None,
                          help="Specify test flow input file for editing")
        parser.add_option("-o", dest="tf_output", metavar=None,
                          help="Specify test flow output file")
        parser.add_option("-c", dest="config_file", metavar="CONFIG_FILE",
                          help="Specify config file")
        parser.add_option("-t", dest="flowtype", metavar="TYPE",
                          help="Specify the type to edit", default='Y')

        options, () = parser.parse_args()

        # Parse options
        if options.config_file:
            config_file = options.config_file.replace('.xls', '') + '.xls'
            self.config = ConfigFile(config_file)
        else:
            error_msg('Please provide the config file with "-c" option.')
            sys.exit()

        if options.tf_input:
            self.tf_input = options.tf_input
            info_msg('Config file is "' + config_file + '"')
        else:
            warning_msg('Please provide intput testflow for editing with "-i" option.')
            sys.exit()

        if options.tf_output:
            self.tf_output = options.tf_output
        else:
            self.tf_output = self.config.get_config('testflow_name')

        self.flowtype = options.flowtype

    def init(self):
        self.reader = TestFlowReader(self.tf_input)
        self.writer = TestFlowWriter(self.reader, self.config)

        self.section_list = self.reader.section_list

        self.testsuites_list = self.reader.testsuites_list
        self.testmethods_list = self.reader.testmethods_list
        self.testmethodparameters_list = self.reader.testmethodparameters_list

    def filter_testsuites(self, testsuite_name_regex='.*', testmethod_regex='.*'):
        filtered_by_testsuite_name = []
        testsuite_name_list = []
        for testsuite_name in self.reader.get_testsuites_name_list():
            matcher = re.search(testsuite_name_regex, testsuite_name)
            if matcher:
                filtered_by_testsuite_name.append(testsuite_name)
        for testsuite_name in filtered_by_testsuite_name:
            testmethod = self.reader.get_testmethod_by_testsuite_name(testsuite_name)
            matcher = re.search(testmethod_regex, testmethod)
            if matcher:
                testsuite_name_list.append(testsuite_name)
        return testsuite_name_list

    def change_testmethod(self):
        for line in self.config.floweditor:
            enable = line['enable']
            if enable == '':
                enable = 'Y'
            testsuite_name_regex = line['testsuite_name_regex']
            testmethod_regex = line['testmethod_regex']
            testmethod_name = line['target_testmethod_name']
            parameters_selector = line['parameters_selector']

            tim_equ_set, tim_spec_set, timset = self.config.get_timing(line['timing_selector'])
            lev_equ_set, lev_spec_set, levset = self.config.get_level(line['level_selector'])
            seqlbl = line['override_seqlbl']
            comment = '"' + line['comment'].strip('"') + '"'
            local_flags = popolate_local_flags_string(line['local_flags'])

            # Update the testmethod for each section
            if enable in ('-', 'N'):
                continue
            elif enable == self.flowtype:
                testsuites_name_list = self.filter_testsuites(testsuite_name_regex, testmethod_regex)
                for testsuite_name in testsuites_name_list:
                    # Change testmethods_list
                    self.writer.update_testmethods_list(testsuite_name, testmethod_name)
                    self.writer.update_testmethods_section()

                    # Change testmethodparameters_list
                    self.writer.update_testmethodparameters_list(testsuite_name, testmethod_name, parameters_selector)
                    self.writer.update_testmethodparameters_section()

                    # Change testsuites_name_list
                    properties_dict = {'override_tim_equ_set': tim_equ_set, 'override_lev_equ_set': lev_equ_set,
                                       'override_tim_spec_set': tim_spec_set, 'override_lev_spec_set': lev_spec_set,
                                       'override_timset': timset, 'override_levset': levset, 'override_seqlbl': seqlbl,
                                       'comment': comment, 'local_flags': local_flags}

                    self.writer.update_testsuite_list(testsuite_name, properties_dict)
                    self.writer.update_testsuites_section()

    def __read_input_file(self):
        if '--input' in self.option_value_dict:
            self.tf_input = self.option_value_dict['--input']
            self.reader = TestFlowReader(self.tf_input)
            self.writer = TestFlowWriter(self.reader)

            self.section_list = self.reader.section_list

            self.testsuites_list = self.reader.testsuites_list
            self.testmethods_list = self.reader.testmethods_list
            self.testmethodparameters_list = self.reader.testmethodparameters_list
        else:
            error_msg('Please provide intput testflow.')

    def __write_output_file(self):
        if '--output' in self.option_value_dict:
            self.tf_output = self.option_value_dict['--output']
        else:
            self.tf_output = self.config.get_config('testflow_name')
        self.writer.write(self.tf_output, self.section_list)

    def run(self):
        self.init()

        # Change Testmethod/Primary
        self.change_testmethod()

        # Write the output
        if self.tf_input == self.tf_output:
            shutil.copy(self.tf_input, 'bak_' + self.tf_input)
            warning_msg('The input testflow is renamed to bak_%s' % self.tf_input)

        self.writer.write(self.tf_output, self.section_list)
        info_msg('"%s" is edited to "%s"' % (self.tf_input, self.tf_output))
