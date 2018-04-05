'''

@author: Dylan
'''
import csv
import os
import shutil


class TestFlowChecker(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''

    def export_testmethodparameters(self, tm_param_file, testsuite_name_regex='.*', testmethod_regex='.*', ):
        items_list = []
        rows = []
        with open(tm_param_file, 'a', newline='') as dstFile:
            csvwriter = csv.writer(dstFile, dialect='excel', quoting=csv.QUOTE_ALL, lineterminator='\n')
            for testsuite_name in self.reader.get_testsuites_name_list():
                testmethod = self.reader.get_testmethod_by_testsuite_name(testsuite_name)
                parameters_selector = testsuite_name
                testmethodparameters = self.reader.get_testmethodparameters_by_testsuite_name(testsuite_name)
                if (testmethodparameters):
                    row = [testmethod, parameters_selector] + testmethodparameters[2:]
                    item_str = testmethod + ''.join(testmethodparameters[2:])
                    if (item_str not in items_list):
                        rows.append(row)
                        rows.sort()
                        items_list.append(item_str)
            csvwriter.writerows(rows)

    def __export_parameters(self):
        if ('--export' in self.option_value_dict):
            exported_tm_parameters = self.option_value_dict['--export']

            src = os.path.join(self.working_path, '.sys', 'templete', 'tm_parameters.csv')
            self.exported_tm_parameters = os.path.join(os.getcwd(), exported_tm_parameters)
            shutil.copy(src, self.exported_tm_parameters)

            self.export_testmethodparameters(self.exported_tm_parameters)
