#!/usr/bin/env python3
'''

Create ATPG_SAF test flow automatically

@author: Dylan
@version: 
'''

import os
import shutil

from smartflow.flowgenerator.TestFlowGenerator import TestFlowGenerator
from smartflow.flowparser.TestFlow import Group_Node, Run_Node, \
    Assignment_Node, MultiBin_Node, Run_and_branch_Node, Char_Shmoo_on_fail_Node, \
    If_Node
from smartflow.flowparser.Utils import get_core_name, warning_msg, info_msg
from testtable_gen import TesttableEditor


class SAF_Generator(TestFlowGenerator):
    def __init__(self):
        super().__init__()
        self.saf_pattern_dict = self.load_saf_sheet()
        self.__saf_config()

    def load_saf_sheet(self):
        saf_pattern_dict = {}

        self.config.load_config_file()
        sheet_saf = self.config.wb_selectors.sheet_by_name('saf')

        for colx in range(sheet_saf.ncols):
            col = sheet_saf.col_values(colx)
            header = col[0]
            pattern_list = col[1:]
            saf_pattern_dict[header] = pattern_list
        return saf_pattern_dict

    def __saf_config(self):
        self.int_testsuites = []
        self.saf_testsuites = []

        # Get saf core list and pattern list
        self.core_list = self.saf_pattern_dict['core_list']
        self.INT_pattern = self.saf_pattern_dict['INT_pattern']
        self.F32_pattern = self.saf_pattern_dict['F32_pattern']
        self.SAF_pattern = self.saf_pattern_dict['SAF_pattern']
        self.TOPUP_pattern = self.saf_pattern_dict['TOPUP_pattern']
        self.FS_pattern = self.saf_pattern_dict['FS_pattern']
        self.voltage_mode = self.saf_pattern_dict['voltage_mode']

        # Config testmethod
        self.prod_tm = 'MSM_SOC_tml.custom.Digital.QScanPlus.ScanTest'
        self.prod_sel = 'default'
        self.prod_osv_sel = 'osv'
        self.vmin_tm = ''
        self.vmin_sel = ''
        self.fmax_tm = ''
        self.fmax_sel = ''
        self.shmoo_tm = ''
        self.shmoo_sel = ''

        # Config testtable
        self.testtable_file = 'atpg.csv'
        self.tnum_start = 100000000
        self.prod_int_sbin_start = 4000
        self.prod_saf_sbin_start = 4500

    def create_saf_flow(self, flowtpye='prod'):
        voltage_mode_group = {}

        scan_init_group = {}
        atpg_int_group = {}
        atpg_saf_group = {}
        atpg_saf_first32_group = {}
        atpg_saf_topup_group = {}
        atpg_saf_fs_group = {}
        scan_sync = {}

        for voltage_mode in self.voltage_mode:
            if (voltage_mode == ''):
                continue
            # Start to create each voltage mode group
            voltage_mode_group[voltage_mode] = Group_Node(False, 'ATPG_' + voltage_mode)

            int_timing = self.config.get_timing(voltage_mode + '_INT')
            saf_timing = self.config.get_timing(voltage_mode + '_SAF')
            level = self.config.get_level(voltage_mode)

            # Add ScanInit group
            scan_init_group[voltage_mode] = Group_Node(False, 'ATPG_SCANINIT_' + voltage_mode)
            scan_init_group[voltage_mode] \
                .add(Run_Node('FN_VecTagLog_' + voltage_mode)) \
                .add(Run_Node('FN_ScanInit_' + voltage_mode)) \
                .add(Assignment_Node('@FAILED_SCAN_TML', 0))

            self.add_testsuite('FN_VecTagLog_' + voltage_mode, 'MSM_SOC_tml.custom.Digital.QScanPlus.VecTagLog', \
                               'default', ['', '', ''], ['', '', ''], '', '')
            self.add_testsuite('FN_ScanInit_' + voltage_mode, 'MSM_SOC_tml.custom.Digital.QScanPlus.ScanInit', \
                               'default', ['', '', ''], ['', '', ''], '', '')
            voltage_mode_group[voltage_mode].add(scan_init_group[voltage_mode])

            # Add ATPG_INT group
            atpg_int_group[voltage_mode] = Group_Node(False, 'ATPG_INT_' + voltage_mode)
            for pattern_name in self.INT_pattern:
                if (pattern_name == ''):
                    continue
                testsuite_name = 'FN' + pattern_name + '_' + voltage_mode

                if (flowtype == 'osv'):
                    self.add_testsuite(testsuite_name, self.prod_tm, self.prod_osv_sel, int_timing, level, pattern_name)
                else:
                    self.add_testsuite(testsuite_name, self.prod_tm, self.prod_sel, int_timing, level, pattern_name)

                if (flowtype in ('prod', 'osv')):
                    atpg_int_group[voltage_mode] \
                        .add(Run_and_branch_Node(testsuite_name, None, None))
                elif (flowtype == 'eng'):
                    atpg_int_group[voltage_mode].add(Char_Shmoo_on_fail_Node(testsuite_name))
                    self.add_testsuite(testsuite_name + '_VMIN', self.prod_tm, 'default', saf_timing, level,
                                       pattern_name)
                    self.add_testsuite(testsuite_name + '_FMAX', self.prod_tm, 'default', saf_timing, level,
                                       pattern_name)
                    self.add_testsuite(testsuite_name + '_SHMOO', self.prod_tm, 'default', saf_timing, level,
                                       pattern_name)

                self.int_testsuites.append(testsuite_name)
            voltage_mode_group[voltage_mode].add(atpg_int_group[voltage_mode])

            # Add ATPG_SAFFIRST32 group
            eval_if_node = If_Node('@EVAL == 1', None, None)
            atpg_saf_first32_group[voltage_mode] = Group_Node(False, 'ATPG_SAFFIRST32_' + voltage_mode)
            for pattern_name in self.F32_pattern:
                if (pattern_name == ''):
                    continue
                testsuite_name = 'FN' + pattern_name + '_' + voltage_mode

                if (flowtype == 'osv'):
                    self.add_testsuite(testsuite_name, self.prod_tm, self.prod_osv_sel, int_timing, level, pattern_name)
                else:
                    self.add_testsuite(testsuite_name, self.prod_tm, self.prod_sel, int_timing, level, pattern_name)

                if (flowtype in ('prod', 'osv')):
                    atpg_saf_first32_group[voltage_mode].add(Run_and_branch_Node(testsuite_name, None, None))
                elif (flowtype == 'eng'):
                    atpg_saf_first32_group[voltage_mode].add(Char_Shmoo_on_fail_Node(testsuite_name))
                    self.add_testsuite(testsuite_name + '_VMIN', self.prod_tm, 'default', saf_timing, level,
                                       pattern_name)
                    self.add_testsuite(testsuite_name + '_FMAX', self.prod_tm, 'default', saf_timing, level,
                                       pattern_name)
                    self.add_testsuite(testsuite_name + '_SHMOO', self.prod_tm, 'default', saf_timing, level,
                                       pattern_name)

                self.saf_testsuites.append(testsuite_name)

            eval_if_node.then_branch.add(atpg_saf_first32_group[voltage_mode])
            voltage_mode_group[voltage_mode].add(eval_if_node)

            # Add ATPG_SAF group
            atpg_saf_group[voltage_mode] = Group_Node(False, 'ATPG_SAF_' + voltage_mode)
            for pattern_name in self.SAF_pattern:
                if (pattern_name == ''):
                    continue
                testsuite_name = 'FN' + pattern_name + '_' + voltage_mode

                core_group = Group_Node(False, 'ATPG_SAF_' + get_core_name(testsuite_name))
                if (flowtype == 'osv'):
                    self.add_testsuite(testsuite_name, self.prod_tm, self.prod_osv_sel, int_timing, level, pattern_name)
                else:
                    self.add_testsuite(testsuite_name, self.prod_tm, self.prod_sel, int_timing, level, pattern_name)

                if (flowtype in ('prod', 'osv')):
                    core_group.add(Run_and_branch_Node(testsuite_name, None, None))
                elif (flowtype == 'eng'):
                    core_group.add(Char_Shmoo_on_fail_Node(testsuite_name))
                    self.add_testsuite(testsuite_name + '_VMIN', self.prod_tm, 'default', saf_timing, level,
                                       pattern_name)
                    self.add_testsuite(testsuite_name + '_FMAX', self.prod_tm, 'default', saf_timing, level,
                                       pattern_name)
                    self.add_testsuite(testsuite_name + '_SHMOO', self.prod_tm, 'default', saf_timing, level,
                                       pattern_name)
                atpg_saf_group[voltage_mode].add(core_group)

                self.saf_testsuites.append(testsuite_name)
            voltage_mode_group[voltage_mode].add(atpg_saf_group[voltage_mode])

            # Add ATPG_SAF_TOPUP group
            atpg_saf_topup_group[voltage_mode] = Group_Node(False, 'ATPG_SAFTOPUP_' + voltage_mode)
            for pattern_name in self.TOPUP_pattern:
                if (pattern_name == ''):
                    continue
                testsuite_name = 'FN' + pattern_name + '_' + voltage_mode

                core_group = Group_Node(False, 'ATPG_SAFTOPUP_' + get_core_name(testsuite_name))
                if (flowtype == 'osv'):
                    self.add_testsuite(testsuite_name, self.prod_tm, self.prod_osv_sel, int_timing, level, pattern_name)
                else:
                    self.add_testsuite(testsuite_name, self.prod_tm, self.prod_sel, int_timing, level, pattern_name)

                if (flowtype in ('prod', 'osv')):
                    core_group.add(Run_and_branch_Node(testsuite_name, None, None))
                elif (flowtype == 'eng'):
                    core_group.add(Char_Shmoo_on_fail_Node(testsuite_name))
                    self.add_testsuite(testsuite_name + '_VMIN', self.prod_tm, 'default', saf_timing, level,
                                       pattern_name)
                    self.add_testsuite(testsuite_name + '_FMAX', self.prod_tm, 'default', saf_timing, level,
                                       pattern_name)
                    self.add_testsuite(testsuite_name + '_SHMOO', self.prod_tm, 'default', saf_timing, level,
                                       pattern_name)
                atpg_saf_topup_group[voltage_mode].add(core_group)

                self.saf_testsuites.append(testsuite_name)
            voltage_mode_group[voltage_mode].add(atpg_saf_topup_group[voltage_mode])

            # Add ATPG_SAF_FS group
            atpg_saf_fs_group[voltage_mode] = Group_Node(False, 'ATPG_FS_' + voltage_mode)
            for pattern_name in self.FS_pattern:
                if (pattern_name == ''):
                    continue
                testsuite_name = 'FN' + pattern_name + '_' + voltage_mode
                core_group = Group_Node(False, 'ATPG_FS_' + get_core_name(testsuite_name))
                if (flowtype == 'osv'):
                    self.add_testsuite(testsuite_name, self.prod_tm, self.prod_osv_sel, int_timing, level, pattern_name)
                else:
                    self.add_testsuite(testsuite_name, self.prod_tm, self.prod_sel, int_timing, level, pattern_name)

                if (flowtype in ('prod', 'osv')):
                    core_group.add(Run_and_branch_Node(testsuite_name, None, None))
                elif (flowtype == 'eng'):
                    core_group.add(Char_Shmoo_on_fail_Node(testsuite_name))
                    self.add_testsuite(testsuite_name + '_VMIN', self.prod_tm, 'default', saf_timing, level,
                                       pattern_name)
                    self.add_testsuite(testsuite_name + '_FMAX', self.prod_tm, 'default', saf_timing, level,
                                       pattern_name)
                    self.add_testsuite(testsuite_name + '_SHMOO', self.prod_tm, 'default', saf_timing, level,
                                       pattern_name)
                atpg_saf_fs_group[voltage_mode].add(core_group)

                self.saf_testsuites.append(testsuite_name)
            voltage_mode_group[voltage_mode].add(atpg_saf_fs_group[voltage_mode])

            # Add scan_sync
            scan_sync[voltage_mode] = Run_Node('atpg_scansync_%s' % voltage_mode)
            self.add_testsuite('atpg_scansync_%s' % voltage_mode, 'MSM_SOC_tml.custom.Digital.QScanPlus.ScanSync', \
                               'default')

            voltage_mode_group[voltage_mode].add(scan_sync[voltage_mode])
            voltage_mode_group[voltage_mode].add(If_Node('@FAILED_SCAN_TML == 1', MultiBin_Node(), None))

            # Add each volatage mode group to main flow
            self.testflow.add(voltage_mode_group[voltage_mode])

    def create_testtable(self, flowtype):
        self.testtable = TesttableEditor()

        # Global settings
        self.testtable.set_tnum_start(self.tnum_start).set_tnum_step(1000) \
            .set_hbin_name('FAIL_STRUC').set_hbin_number(3).set_sbin_step(1000)

        # Settings for atpg_int
        self.testtable.set_sbin_start(self.prod_int_sbin_start)

        for testsuite_name in self.int_testsuites:
            if (flowtype == 'prod'):
                self.testtable.add_qscan_limits(testsuite_name)
            elif (flowtype == 'char'):
                self.testtable.add_vmin_limits(testsuite_name)
                self.testtable.add_fmax_limits(testsuite_name)
            elif (flowtype == 'eng'):
                self.testtable.add_vmin_limits(testsuite_name + '_VMIN')
                self.testtable.add_fmax_limits(testsuite_name + '_FMAX')

        # Settings for atpg_saf
        self.testtable.set_sbin_start(self.prod_saf_sbin_start)
        for testsuite_name in self.saf_testsuites:
            if (flowtype == 'prod'):
                self.testtable.add_qscan_limits(testsuite_name)
            elif (flowtype == 'char'):
                self.testtable.add_vmin_limits(testsuite_name)
                self.testtable.add_fmax_limits(testsuite_name)
            elif (flowtype == 'eng'):
                self.testtable.add_vmin_limits(testsuite_name + '_VMIN')
                self.testtable.add_fmax_limits(testsuite_name + '_FMAX')

        # Write testtable file
        if (flowtype == 'prod'):
            self.testtable.write(self.testtable_file)
            if (os.path.basename(os.getcwd()) == 'testflow'):
                shutil.move(self.testtable_file, os.path.join('..', 'testtable', self.testtable_file))
                info_msg('Testtable %s is moved to ../testtable.' % self.testtable_file)
        elif (flowtype == 'char'):
            testtable_char = self.testtable_file.replace('.csv', '_char.csv')
            self.testtable.write(testtable_char)
            if (os.path.basename(os.getcwd()) == 'testflow'):
                shutil.move(testtable_char, os.path.join('..', 'testtable', testtable_char))
                info_msg('Testtable %s is moved to ../testtable.' % testtable_char)
        elif (flowtype == 'eng'):
            testtable_eng = self.testtable_file.replace('.csv', '_eng.csv')
            self.testtable.write(testtable_eng)
            if (os.path.basename(os.getcwd()) == 'testflow'):
                shutil.move(testtable_eng, os.path.join('..', 'testtable', testtable_eng))
                info_msg('Testtable %s is moved to ../testtable.' % testtable_eng)
        elif (flowtype == 'osv'):
            testtable_osv = self.testtable_file.replace('.csv', '_osv.csv')
            self.testtable.write(testtable_osv)
            if (os.path.basename(os.getcwd()) == 'testflow'):
                shutil.move(testtable_osv, os.path.join('..', 'testtable', testtable_osv))
                info_msg('Testtable %s is moved to ../testtable.' % testtable_osv)


if __name__ == '__main__':
    flowtype = 'prod'

    editor = SAF_Generator()
    editor.init()

    flowtype = editor.flow_type

    # Create saf flow
    editor.create_saf_flow(flowtype)

    if (flowtype == 'prod'):
        editor.write('ATPG_SAF_PROD.ttf')
        editor.create_testtable('prod')
        editor.create_testtable('char')
    elif (flowtype == 'eng'):
        editor.create_testtable('eng')
        editor.write('ATPG_SAF_ENG.ttf')
    elif (flowtype == 'osv'):
        editor.create_testtable('osv')
        editor.write('ATPG_SAF_OSV.ttf')
    else:
        warning_msg('Unknow flow type: "' + flowtype + '".\n' + \
                    'Available tpyes: "prod", "eng", "osv"')
