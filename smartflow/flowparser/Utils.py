"""

@author: Dylan
"""
import re

# Constants
SECTION_KEYS = ("header", "information", "declarations", "implicit_declarations", "flags",
                "testmethodparameters", "testmethodlimits", "testmethods", "test_suites",
                "bin_disconnect", "test_flow", "binning", "context", "hardware_bin_descriptions")

TF_HEADER = 'hp93000,testflow,0.1\nlanguage_revision = 1;\n\n'

SEPARATOR = '-----------------------------------------------------------------'
INITIAL_INTENT = ' '
INTENT = '   '

INT_regex = 'MBURST_atpg_int_lpc_(\w+?)_XMD'
F32_regex = 'MBURST_atpg_saf_lpc_se0_(\w+?)_first32_XMD'
SAF_regex = 'MBURST_atpg_saf_lpc_se0_(\w+?)_TSLC_XMD'
TOPUP_regex = 'MBURST_atpg_saf_lpc_se0_(\w+?)_topup_XMD'
FS_regex = 'MBURST_atpg_saf_lpc_se0_(\w+?)_FS_TSLC_XMD'


def error_msg(value):
    print('\033[1;31m[ERROR] %s\033[0m' % value)


def warning_msg(value):
    print('\033[1;35m[WARNING] %s\033[0m' % value)


def info_msg(value):
    print('\033[1;34m[INFO] %s\033[0m' % value)


def cell2str(value):
    if type(value) == type(1.0):
        if value == int(value):
            value = int(value)
        else:
            value = float(value)
    value = str(value)

    return value


def popolate_local_flags_string(bitarray):
    flag = ['bypass', 'output_on_pass', 'output_on_fail', 'value_on_pass', 'value_on_fail', 'per_pin_on_pass',
            'per_pin_on_fail']
    flags_list = []
    if bitarray:
        bitarray = bitarray.strip()
    if bitarray == '':
        bitarray = 'NYYYYYY'
    if len(bitarray) != 7:
        print(bitarray)
        print("ERROR: The format should be [N|Y]{7}, change to 'NYYYYYY")
        bitarray = 'NYYYYYY'
    bit_list = list(bitarray)
    for index in range(7):
        if bit_list[index] == 'Y':
            flags_list.append(flag[index])

    return ', '.join(flags_list)


def get_block_name(testsuite_name):
    block_name = ''
    if 'atpg_int' in testsuite_name:
        block_name = "ATPG_INT"
    elif '_topup_' in testsuite_name:
        block_name = "ATPG_SAF_TOPUP"
    elif '_fs_' in testsuite_name:
        block_name = "ATPG_FS"
    elif 'atpg_saf' in testsuite_name:
        block_name = "ATPG_SAF"
    return block_name


def get_core_name(testsuite_name):
    global core_name
    matcher = re.search('%s|%s|%s|%s|%s' % (FS_regex, INT_regex, F32_regex, SAF_regex, TOPUP_regex), testsuite_name)
    if matcher:
        for index in range(1, 6):
            if matcher.group(index):
                core_name = matcher.group(index)
    else:
        core_name = testsuite_name
    return core_name


def get_voltage_mode(testsuite_name):
    voltage_mode = ''
    matcher = re.match('\w+_XMD_(\w+)', testsuite_name)
    if matcher:
        voltage_mode = matcher.group(1)
    return voltage_mode
