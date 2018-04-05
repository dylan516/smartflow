#!/usr/bin/env python3
'''

Create IDDQ test flow automatically

@author: Dylan
@version: 
'''
import os

# import Tkinter as tk
from smartflow.flowgenerator.TestFlowGenerator import TestFlowGenerator
from smartflow.flowparser.TestFlow import Group_Node, Run_Node, \
    Run_and_branch_Node, MultiBin_Node


class SAF_Generator(TestFlowGenerator):
    def __init__(self):
        super().__init__()

    def create_iddq_flow(self):
        timing = ['1', '1', '1']
        level = ['1', '1', '1']

        group_on = Group_Node(False, 'IDDQ_ACTIVE')
        ActivePatternsFiles = open('ActivePatterns.txt', 'r')
        ActivePatternsList = ActivePatternsFiles.readlines()
        for index in range(len(ActivePatternsList)):
            pattern_name = ActivePatternsList[index].strip('\n')
            testmethod_name = 'SOC_tml.DC.ProductionIDDQ'
            parameters_selector = 'default'
            testsuite_name = 'DC' + pattern_name + '_' + 'NV'

            group_on.add(Run_Node('Disconnect_iddq_on_%d' % (index + 1)))
            group_on.add(Run_and_branch_Node(testsuite_name, None, MultiBin_Node()))
            self.add_testsuite('Disconnect_iddq_on_%d' % (index + 1), 'SOC_tml.Common.Disconnect', 'default')
            self.add_testsuite(testsuite_name, testmethod_name, parameters_selector, \
                               timing, level, pattern_name, '')

        group_off = Group_Node(False, 'IDDQ_OFF')
        OffPatternsFiles = open('OffPatterns.txt', 'r')
        OffPatternsList = OffPatternsFiles.readlines()

        for index in range(len(OffPatternsList)):
            pattern_name = OffPatternsList[index].strip('\n')
            testmethod_name = 'SOC_tml.DC.ProductionIDDQ'
            parameters_selector = 'default'
            testsuite_name = 'DC' + pattern_name + '_' + 'NV'

            group_off.add(Run_Node('Disconnect_iddq_off_%d' % (index + 1)))
            group_off.add(Run_and_branch_Node(testsuite_name, None, MultiBin_Node()))
            self.add_testsuite('Disconnect_iddq_off_%d' % (index + 1), 'SOC_tml.Common.Disconnect', 'default')
            self.add_testsuite(testsuite_name, testmethod_name, parameters_selector, \
                               timing, level, pattern_name, '')

        group_sleep = Group_Node(False, 'IDDQ_Sleep')
        SleepPatternsFiles = open('SleepPatterns.txt', 'r')
        SleepPatternsList = SleepPatternsFiles.readlines()

        for index in range(len(SleepPatternsList)):
            pattern_name = SleepPatternsList[index].strip('\n')
            testmethod_name = 'SOC_tml.DC.ProductionIDDQ'
            parameters_selector = 'Sleep'
            testsuite_name = 'DC' + pattern_name + '_' + 'NV'

            group_sleep.add(Run_Node('Disconnect_iddq_sleep_%d' % (index + 1)))
            group_sleep.add(Run_and_branch_Node(testsuite_name, None, MultiBin_Node()))
            self.add_testsuite('Disconnect_iddq_sleep_%d' % (index + 1), 'SOC_tml.Common.Disconnect', 'default')
            self.add_testsuite(testsuite_name, testmethod_name, parameters_selector, \
                               timing, level, pattern_name, '')
        self.testflow.add(group_on)
        self.testflow.add(group_off)
        self.testflow.add(group_sleep)

    def create_iddq_char_flow(self):
        # char setting for level/timing of active/off
        timing = ['1', '1', '1']
        level = ['1', '1', '1']
        start_level = 1
        start_volt = 700
        end_volt = 1050
        step = 50
        ActivePatternsFiles = open(os.getcwd() + '/ActivePatterns.txt', 'r')
        ActivePatternsList = ActivePatternsFiles.readlines()
        group_on = Group_Node(False, 'IDDQ_ACTIVE_CHAR')
        for index in range(len(ActivePatternsList)):
            sub_group = Group_Node(False, 'Iddq_active_%s' % ActivePatternsList[index].strip('\n'))
            pattern_name = ActivePatternsList[index].strip('\n')
            testmethod_name = 'SOC_tml.DC.ProductionIDDQ'
            parameters_selector = 'default'

            for voltage in range(start_volt, end_volt + step, step):
                testsuite_name = 'DC' + pattern_name + '_%dmV' % voltage
                sub_group.add(Run_Node('Disconnect_' + testsuite_name))
                sub_group.add(Run_and_branch_Node(testsuite_name, None, MultiBin_Node()))

                self.add_testsuite('Disconnect_' + testsuite_name, 'SOC_tml.Common.Disconnect', 'default')
                level[1] = str(int((voltage - start_volt) / step) + start_level)
                self.add_testsuite(testsuite_name, testmethod_name, parameters_selector, \
                                   timing, level, pattern_name, '')

            group_on.add(sub_group)

        OffPatternsFiles = open(os.getcwd() + '/OffPatterns.txt', 'r')
        OffPatternsList = OffPatternsFiles.readlines()
        group_off = Group_Node(False, 'IDDQ_Off_CHAR')
        for index in range(len(OffPatternsList)):
            sub_group = Group_Node(False, 'Iddq_off_%s' % OffPatternsList[index].strip('\n'))

            pattern_name = OffPatternsList[index].strip('\n')
            testmethod_name = 'SOC_tml.DC.ProductionIDDQ'
            parameters_selector = 'default'

            for voltage in range(start_volt, end_volt + step, step):
                testsuite_name = 'DC' + pattern_name + '_%dmV' % voltage
                sub_group.add(Run_Node('Disconnect_' + testsuite_name))
                sub_group.add(Run_and_branch_Node(testsuite_name, None, MultiBin_Node()))

                self.add_testsuite('Disconnect_' + testsuite_name, 'SOC_tml.Common.Disconnect', 'default')
                level[1] = str(int((voltage - start_volt) / step) + start_level)
                self.add_testsuite(testsuite_name, testmethod_name, parameters_selector, \
                                   timing, level, pattern_name, '')

            group_off.add(sub_group)
        # char setting for level/timing of sleep
        timing = ['1', '1', '1']
        level = ['1', '1', '1']
        start_level = 1
        start_volt = 700
        end_volt = 1050
        step = 50
        SleepPatternsFiles = open(os.getcwd() + '/SleepPatterns.txt', 'r')
        SleepPatternsList = SleepPatternsFiles.readlines()
        group_sleep = Group_Node(False, 'IDDQ_SlEEP_CHAR')
        for index in range(len(SleepPatternsList)):
            sub_group = Group_Node(False, 'Iddq_sleep_%s' % SleepPatternsList[index].strip('\n'))
            pattern_name = SleepPatternsList[index].strip('\n')
            testmethod_name = 'SOC_tml.DC.ProductionIDDQ'
            parameters_selector = 'Sleep'

            for voltage in range(start_volt, end_volt + step, step):
                testsuite_name = 'DC' + pattern_name + '_%dmV' % voltage
                sub_group.add(Run_Node('Disconnect_' + testsuite_name))
                sub_group.add(Run_and_branch_Node(testsuite_name, None, MultiBin_Node()))

                self.add_testsuite('Disconnect_' + testsuite_name, 'SOC_tml.Common.Disconnect', 'default')
                level[1] = str(int((voltage - start_volt) / step) + start_level)
                self.add_testsuite(testsuite_name, testmethod_name, parameters_selector, \
                                   timing, level, pattern_name, '')

            group_sleep.add(sub_group)

        self.testflow.add(group_on)
        self.testflow.add(group_off)
        self.testflow.add(group_sleep)


if __name__ == '__main__':
    editor = SAF_Generator()

    if (editor.option_value_dict['--type'] == 'phase'):
        editor.create_iddq_flow()
        editor.write('iddq_autogen.ttf')
    if (editor.option_value_dict['--type'] == 'char'):
        editor.create_iddq_char_flow()
        editor.write('iddq_char_autogen.ttf')
    print("Please check timing/level/DPS/Functional check especailly for sleep mode!!!")
