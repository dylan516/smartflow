"""

@author: Dylan
"""
import csv
import sys

from smartflow.flowparser.Utils import get_block_name, get_core_name, \
    get_voltage_mode, info_msg


class TesttableEditor(object):

    def __init__(self, testtable_editor=None):
        self.lines = []

        if testtable_editor:
            self.lines = self.load_testtable(testtable_editor)
            self.__get_testmodes()
        else:
            self.create()

        self.sbin_dict = {}
        self.keys = self.keys()

    def load_testtable(self, testtable_editor):
        with open(testtable_editor, 'r', newline='') as srcFile:
            csvreader = csv.reader(srcFile, dialect='excel')
            lines = list(csvreader)
        return lines

    def __get_testmodes(self):
        testmodes = []
        for testmode in self.lines[1][3:]:
            if (testmode not in testmodes) and (testmode.strip()):
                testmodes.append(testmode)
        return testmodes

    def __create_testmodes_list(self):
        testmodes_list = []
        for testmode in self.testmodes:
            testmodes_list += [testmode] * 5
        return testmodes_list

    def create(self, testmodes=None, \
               tnum_start=0, tnum_step=1, sbin_start=1, sbin_step=1, \
               hbin_number=1, hbin_name='FAIL'):
        if testmodes is None:
            testmodes = ['WS', 'FT', 'QA', 'VA']
        self.testmodes = testmodes

        self.line0 = ['Suite name', 'Test name', 'Test number'] + \
                     ['Lsl', 'Lsl_typ', 'Usl_typ', 'Usl', 'Units'] * len(self.testmodes) + \
                     ['Bin_s_num', 'Bin_s_name', 'Bin_h_num', 'Bin_h_name',
                      'Bin_type', 'Bin_reprobe', 'Bin_overon', 'Test_remarks', 'Block']
        self.line1 = ['Test mode', '', ''] + self.__create_testmodes_list() + [''] * 9
        self.lines.append(self.line0)
        self.lines.append(self.line1)

        self.set_tnum_start(tnum_start)
        self.set_tnum_step(tnum_step)
        self.set_sbin_start(sbin_start)
        self.set_sbin_step(sbin_step)
        self.set_hbin_number(hbin_number)
        self.set_hbin_name(hbin_name)

    def set_tnum_start(self, tnum_start):
        self.testnumber = tnum_start
        return self

    def set_tnum_step(self, tnum_step):
        self.tnum_step = tnum_step
        return self

    def set_sbin_start(self, sbin_start):
        self.sbin_num = sbin_start
        return self

    def set_sbin_step(self, sbin_step):
        self.sbin_step = sbin_step
        return self

    def set_hbin_number(self, hbin_number):
        self.hbin_number = hbin_number
        return self

    def set_hbin_name(self, hbin_name):
        self.hbin_name = hbin_name
        return self

    def get_key(self, line):
        suite_name = line[0]
        test_name = line[1]
        key = suite_name + '@' + test_name
        return key

    def keys(self):
        keys = []
        for line in self.lines[2:]:
            key = self.get_key(line)
            keys.append(key)
        return keys

    def __tnum(self):
        testnumber = self.testnumber
        self.testnumber += self.tnum_step
        return testnumber

    def __sbin_num(self):
        sbin_num = self.sbin_num
        self.sbin_num += 2
        return sbin_num

    def clear(self):
        self.lines = self.lines[:2]
        self.keys = []

    def add(self, suite_name, test_name, limits=None):
        if limits is None:
            limits = ['0', 'GE', 'LE', '0', 'NA']
        core = get_core_name(suite_name)
        block = get_block_name(suite_name)
        voltage_mode = get_voltage_mode(suite_name)

        testnumber = self.__tnum()

        Bin_s_name = block + '_' + core + '_' + voltage_mode
        if Bin_s_name in self.sbin_dict:
            Bin_s_num = self.sbin_dict[Bin_s_name]
        else:
            Bin_s_num = self.__sbin_num()
            self.sbin_dict[Bin_s_name] = Bin_s_num

        Bin_type = 'bad'
        Bin_reprobe = 'no'
        Bin_overon = 'yes'
        Test_remarks = ''

        line = [suite_name, test_name, testnumber] + \
               limits * len(self.__get_testmodes()) + \
               [Bin_s_num, Bin_s_name, self.hbin_name, self.hbin_number,
                Bin_type, Bin_reprobe, Bin_overon, Test_remarks, block]

        if self.get_key(line) not in self.keys:
            self.lines.append(line)

    def add_qscan_limits(self, suite_name):
        for test_name in ['ScanTestFTR', 'ScanTestSTR']:
            self.add(suite_name, test_name)

    def add_vmin_limits(self, suite_name):
        self.add(suite_name, 'SpecSearch_Vmin', ['0', 'NA', 'NA', '0', 'V'])

    def add_fmax_limits(self, suite_name):
        self.add(suite_name, 'SpecSearch_Fmax', ['0', 'NA', 'NA', '0', 'MHz'])

    def write(self, testtable):
        with open(testtable, 'w', newline='') as dstFile:
            csvwriter = csv.writer(dstFile, dialect='excel')
            csvwriter.writerows(self.lines)
        info_msg('Test table %s is auto-generated.' % testtable)

    def export_suite_and_test_list(self):
        suite_and_test_list = []
        for line in self.lines[2:]:
            suite_and_test = self.get_key(line)
            if suite_and_test not in suite_and_test_list:
                suite_and_test_list.append(suite_and_test)
        return suite_and_test_list


if __name__ == '__main__':
    csvfile = sys.argv[1]
    output = sys.argv[2]

    testtable_editor = TesttableEditor(csvfile)

    suite_list = testtable_editor.export_suite_and_test_list()
    print(suite_list)

    testtable_editor.clear()

    for suite_and_test in suite_list:
        suite_name, test_name = suite_and_test.split('@')
        testtable_editor.add(suite_name, test_name)

    testtable_editor.write(output)
