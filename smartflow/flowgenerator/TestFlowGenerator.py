'''

@author: Dylan
'''

from optparse import OptionParser

import sys

from smartflow.flowparser.ConfigFile import ConfigFile
from smartflow.flowparser.TestFlow import TestFlow, Run_Node, \
    Run_and_branch_Node, MultiBin_Node, Group_Node
from smartflow.flowparser.TestFlowReader import TestFlowReader
from smartflow.flowparser.TestFlowWriter import TestFlowWriter
from smartflow.flowparser.Utils import popolate_local_flags_string, \
    get_block_name, get_core_name, info_msg, error_msg


class TestFlowGenerator(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        self.__parse_options()

    def __parse_options(self):
        description = "Automatically generate testflow from xls config file."

        parser = OptionParser(description=description)
        parser.add_option("-i", dest="tf_input", metavar=None,
                          help="Test flow template")
        parser.add_option("-o", dest="tf_output", metavar=None,
                          help="Test flow output file")
        parser.add_option("-c", dest="config_file", metavar="CONFIG_FILE",
                          help="Specify config file for auto-generation.")
        parser.add_option("-t", dest="flow_type", metavar=None, default='prod',
                          help="Specify test flow type. [prod, eng, vmin, fmax, shmoo]")

        options, () = parser.parse_args()

        # Parse options
        self.tf_input = options.tf_input
        self.flow_type = options.flow_type

        if options.config_file:
            config_file = options.config_file.replace('.xls', '') + '.xls'
            self.config = ConfigFile(config_file)
        else:
            error_msg('Please provide the config file with "-c" option.')
            sys.exit()
        info_msg('Config file is "' + config_file + '"')

        if options.tf_output:
            self.tf_output = options.tf_output
        else:
            self.tf_output = self.config.get_config('testflow_name')

    def init(self):
        self.section_list = []
        self.testsuite_name_list = ['']
        self.testsuite_list = []
        self.testmethod_list = []
        self.testmethodparameters_list = []
        self.testflow = TestFlow()

        self.reader = TestFlowReader(self.tf_input)
        self.writer = TestFlowWriter(self.reader)

        self.section_list = self.reader.section_list

        self.testsuites_list = []
        self.testmethods_list = []
        self.testmethodparameters_list = []

    def get_tm_id(self, testsuite_name):
        return str(self.testsuite_name_list.index(testsuite_name))

    def update_testsuite_list(self, testsuite_name, timing=None, level=None, pattern_name=None,
                              local_flags_bitarray=None):
        testsuite = []

        self.testsuite_name_list.append(testsuite_name)
        testsuite.append(testsuite_name)

        tm_id = self.get_tm_id(testsuite_name)
        testsuite.append(tm_id)

        local_flags = popolate_local_flags_string(local_flags_bitarray)

        if (timing == None):
            timing = ['', '', '']
        if (level == None):
            level = ['', '', '']
        if (pattern_name == None):
            pattern_name = '""'
        else:
            pattern_name = '"' + pattern_name + '"'

        prop_list = ['override', '1',
                     'override_tim_equ_set', timing[0],
                     'override_lev_equ_set', level[0],
                     'override_tim_spec_set', timing[1],
                     'override_lev_spec_set', level[1],
                     'override_timset', timing[2],
                     'override_levset', level[2],
                     'override_seqlbl', pattern_name,
                     'override_testf', 'tm_' + tm_id,
                     'local_flags', local_flags,
                     'site_control', '"parallel:"'
                     ]

        testsuite += prop_list
        self.testsuite_list.append(testsuite)
        return testsuite

    def update_testmethod_list(self, testsuite_name, testmethod_name):
        testmethod = []
        tm_id = self.get_tm_id(testsuite_name)

        testmethod.append(tm_id)
        testmethod.append(testmethod_name)
        self.testmethod_list += testmethod

        return testmethod

    def update_testmethodparameters_list(self, testsuite_name, testmethod_name, parameters_selector):
        testmethodparameters = []
        tm_id = self.get_tm_id(testsuite_name)

        testmethodparameters.append(tm_id)
        testmethodparameters.append(testmethod_name)

        tm_parameters = self.config.get_parameters(testmethod_name, parameters_selector)
        testmethodparameters += tm_parameters
        self.testmethodparameters_list.append(testmethodparameters)

        return testmethodparameters

    def add_testsuite(self, testsuite_name, testmethod_name='', parameters_selector='', timing=None, level=None,
                      pattern_name=None, local_flags=''):
        self.update_testsuite_list(testsuite_name, timing, level, pattern_name, local_flags)
        self.update_testmethod_list(testsuite_name, testmethod_name)
        self.update_testmethodparameters_list(testsuite_name, testmethod_name, parameters_selector)

    def update_prop_list(self, prop_list, prop, value):
        value_index = prop_list.index(prop) + 1
        prop_list[value_index] = value
        return prop_list

    def update_sections(self):
        # Create each section
        testmethod_parameters_section = self.writer.create_testmethodparameters_section(self.testmethodparameters_list)
        testmethods_section = self.writer.create_testmethods_section(self.testmethod_list)
        test_suites_section = self.writer.create_test_suites_section(self.testsuite_list)
        testflow_section = self.writer.create_testflow_section(self.testflow)

        # Update each section to section list
        self.reader.update_section_list(testmethod_parameters_section)
        self.reader.update_section_list(testmethods_section)
        self.reader.update_section_list(test_suites_section)
        self.reader.update_section_list(testflow_section)

    def create_testflow_section(self):
        last_active_node = self.testflow
        active_node = self.testflow

        group_name_list = []
        group_dict = {}

        core_group = None

        for line in self.config.testflow_sequence:
            node_type = line['type']
            if (not node_type.startswith('group#')):
                pattern_name = line['pattern']
                testmethod_name = line['testmethod_name']
                parameters_selector = line['parameters_selector']
                local_flags = line['local_flags']
                testsuite_name = line['testsuite_name']

                timing = self.config.get_timing(line['timing_selector'])
                level = self.config.get_level(line['level_selector'])

            if (node_type == 'run'):
                active_node.add(Run_Node(testsuite_name))
                # Add testsuite
                self.add_testsuite(testsuite_name, testmethod_name, parameters_selector, timing, level, pattern_name,
                                   local_flags)
            elif (node_type == 'run_and_branch'):
                active_node.add(Run_and_branch_Node(testsuite_name, None, MultiBin_Node()))
                # Add testsuite
                self.add_testsuite(testsuite_name, testmethod_name, parameters_selector, timing, level, pattern_name,
                                   local_flags)
            elif (node_type == 'suite_group'):
                group_name = get_block_name(testsuite_name) + get_core_name(testsuite_name)
                suite_group = Group_Node(False, group_name)
                suite_group.add(Run_and_branch_Node(testsuite_name, None, MultiBin_Node()))
                active_node.add(suite_group)
                # Add testsuite
                self.add_testsuite(testsuite_name, testmethod_name, parameters_selector, timing, level, pattern_name,
                                   local_flags)
            elif (node_type == 'core_group_start'):
                group_name = get_core_name(testsuite_name)
                core_group = Group_Node(False, group_name)
                core_group.add(Run_and_branch_Node(testsuite_name, None, MultiBin_Node()))
                # Add testsuite
                self.add_testsuite(testsuite_name, testmethod_name, parameters_selector, timing, level, pattern_name,
                                   local_flags)
            elif (node_type == 'core_group'):
                core_group.add(Run_and_branch_Node(testsuite_name, None, MultiBin_Node()))
                # Add testsuite
                self.add_testsuite(testsuite_name, testmethod_name, parameters_selector, timing, level, pattern_name,
                                   local_flags)
            elif (node_type == 'core_group_end'):
                core_group.add(Run_and_branch_Node(testsuite_name, None, MultiBin_Node()))
                active_node.add(core_group)
                # Add testsuite
                self.add_testsuite(testsuite_name, testmethod_name, parameters_selector, timing, level, pattern_name,
                                   local_flags)
            elif (node_type == 'retest_on_fail'):
                testsuite_name_retest = testsuite_name + self.config.get_config('retest_testsuite_postfix')
                # Add testsuite
                self.add_testsuite(testsuite_name, testmethod_name, parameters_selector, timing, level, pattern_name,
                                   local_flags)
                # Add retest testsuite
                self.add_testsuite(testsuite_name_retest, testmethod_name, parameters_selector, timing, level,
                                   pattern_name, local_flags)
                active_node.add(Run_and_branch_Node(testsuite_name, None, \
                                                    Run_and_branch_Node(testsuite_name_retest, None, MultiBin_Node())))
            elif (node_type == 'char_shmoo_on_fail'):
                testsuite_name_vmin = testsuite_name + self.config.get_config('vmin_testsuite_postfix')
                testsuite_name_fmax = testsuite_name + self.config.get_config('fmax_testsuite_postfix')
                testsuite_name_shmoo = testsuite_name + self.config.get_config('shmoo_testsuite_postfix')
                # Add testsuite
                self.add_testsuite(testsuite_name, testmethod_name, parameters_selector, timing, level, pattern_name,
                                   local_flags)
                # Add vmin/fmax/shmoo testsuite
                self.add_testsuite(testsuite_name_vmin, \
                                   self.config.get_config('vmin_testmethod'), self.config.get_config('vmin_selector'), \
                                   timing, level, pattern_name, local_flags)
                self.add_testsuite(testsuite_name_fmax, \
                                   self.config.get_config('fmax_testmethod'), self.config.get_config('fmax_selector'), \
                                   timing, level, pattern_name, local_flags)
                self.add_testsuite(testsuite_name_shmoo, \
                                   self.config.get_config('shmoo_testmethod'), self.config.get_config('shmoo_selector'), \
                                   timing, level, pattern_name, local_flags)

                run_and_branch = Run_and_branch_Node(testsuite_name, None, None)
                run_and_branch.else_branch \
                    .add(Run_Node(testsuite_name_vmin)) \
                    .add(Run_Node(testsuite_name_fmax)) \
                    .add(Run_Node(testsuite_name_shmoo))
                active_node.add(run_and_branch)
            elif (node_type.startswith('group#')):
                group_name = node_type.lstrip('group#')

                if (group_name not in group_name_list):
                    last_active_node = active_node
                    new_group = Group_Node(False, group_name)
                    group_dict[group_name] = new_group
                    group_name_list.append(group_name)
                    active_node = new_group

                elif (len(group_name_list)):
                    if group_name_list[-1] == group_name:
                        last_active_node.add(active_node)
                        group_name_list.pop()
                        active_node = last_active_node

    def write(self, tf_output=None):
        if (tf_output == None):
            tf_output = self.tf_output

        self.update_sections()
        self.writer.write(tf_output, self.section_list)
        info_msg('Test flow %s is auto-generated.' % tf_output)

    def run(self):
        self.init()
        self.create_testflow_section()
        self.write()
