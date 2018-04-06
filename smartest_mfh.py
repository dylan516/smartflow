#!/usr/bin/env python3

import os
import re
import shutil
from optparse import OptionParser


class SmartestMFH:
    """
    SmartestMFH class
    """
    # Declare constants
    MFH_LOC = '/opt/hp93000/soc/com/SETUP_MAN/smartest_mfh '
    CMD_CREATE = MFH_LOC + 'create '
    CMD_SPLIT = MFH_LOC + 'split '
    CMD_ASSEMBLE = MFH_LOC + 'assemble '
    FILE_TYPE = (
        'level', 'timing', 'waveform', 'analog_control', 'testtable', 'testflow', 'routing', 'config', 'testtable')

    def __init__(self):
        # Declare variables
        self.working_path = os.getcwd()
        self.filetype = self.get_filetype()

        # -c
        self.tester_file_to_be_split = ''
        self.master_file_to_be_created = ''
        self.subfolder_testerfile = ''

        # -a
        self.master_file_to_be_assembled = ''
        self.tester_file_to_be_created = None
        self.tester_file_name = ''

        # -d
        self.is_delete_subfile_folder = False

        # -s
        self.specified_subfiles = None

        self.basename = ''
        self.fileExt = ''
        self.subfiles_folder_path = ''

    def __parse_options(self):
        description = "Create or assemble master file."

        parser = OptionParser(description=description, version='V1.0')
        parser.add_option('-c', dest='tester_file_to_be_split', metavar='TESTER_FILE',
                          help='Create master file from the specified tester file.')
        parser.add_option('-a', dest='master_file_to_be_assembled', metavar='MASTER_FILE',
                          help='Assemble the specified master file to tester file.')
        parser.add_option('-o', dest='output_file', metavar='FILE',
                          help='Specify the name of output master file or tester file.')
        parser.add_option('-s', dest='subfiles_folder_basename', metavar='FOLDER', default='subfiles',
                          help='Specify the subfiles folder name for creating master file.')
        parser.add_option('-d', action='store_true', dest='is_delete_subfile_folder', default=False,
                          help='Delete master file and subfiles folder along with assembling.')

        options, () = parser.parse_args()
        # Parse options
        if options.tester_file_to_be_split and options.master_file_to_be_assembled:
            parser.error("Options -c and -a are mutually exclusive")
        elif options.tester_file_to_be_split:
            self.tester_file_to_be_split = options.tester_file_to_be_split
            if options.output_file:
                self.basename = os.path.splitext(options.output_file)[0]
            else:
                self.basename = os.path.splitext(self.tester_file_to_be_split)[0]
            if options.subfiles_folder_basename:
                self.subfiles_folder_basename = options.subfiles_folder_basename
            else:
                self.subfiles_folder_basename = 'subfiles_' + self.basename
            self.create_mfh()
        elif options.master_file_to_be_assembled:
            self.master_file_to_be_assembled = options.master_file_to_be_assembled
            self.is_delete_subfile_folder = options.is_delete_subfile_folder
            self.basename = os.path.splitext(options.master_file_to_be_assembled)[0]
            if options.output_file:
                self.tester_file_name = options.output_file
                self.tester_file_to_be_created = os.path.join(self.working_path, self.tester_file_name)
            self.assemble_mfh()
        else:
            parser.print_help()

    def get_filetype(self):
        filetype = os.path.split(self.working_path)[1]
        if filetype == 'levels':
            filetype = 'level'
        elif filetype == 'configuration':
            filetype = 'config'
        return filetype

    def create_mfh(self):
        # Create subfiles folder
        if self.filetype in self.FILE_TYPE:
            self.subfiles_folder_path = os.path.join(self.working_path, self.subfiles_folder_basename)
            if not os.path.exists(self.subfiles_folder_path):
                os.mkdir(self.subfiles_folder_path)

        # Create the master file
        self.master_file_to_be_created = os.path.join(self.working_path, self.basename + '.mfh')
        os.system(self.CMD_CREATE + self.filetype + ' ' + self.master_file_to_be_created)

        # Copy mfh file to subfolder
        subfolder_mfh_file = os.path.join(self.subfiles_folder_path, self.basename + '.mfh')
        shutil.copy(self.master_file_to_be_created, subfolder_mfh_file)

        # Copy tester file to subfolder
        self.subfolder_testerfile = os.path.join(self.subfiles_folder_path, self.basename)
        shutil.copy(self.tester_file_to_be_split, self.subfolder_testerfile)

        # Split the tester file into master file
        os.system(self.CMD_SPLIT + subfolder_mfh_file)

        # Update the master file and move it to working path
        with open(self.master_file_to_be_created, 'w') as dstFile:
            with open(subfolder_mfh_file, 'r') as srcFile:
                for line in srcFile:
                    matcher = re.match('testerfile : (.*)', line)
                    if matcher:
                        line = 'testerfile : ' + self.tester_file_to_be_split + '\n\n'
                    else:
                        matcher = re.match('(.*: )(.*\.\w+)', line)
                        if matcher:
                            line = matcher.group(1) + self.subfiles_folder_basename + '/' + matcher.group(2) + '\n'
                    dstFile.write(line)

        # Clean up
        os.unlink(subfolder_mfh_file)
        os.unlink(self.subfolder_testerfile)

    def assemble_mfh(self):
        subfile_list = []
        subfile_folder_list = []

        with open(self.master_file_to_be_assembled, 'r') as srcFile:
            lines = srcFile.readlines()

        with open(self.master_file_to_be_assembled, 'w') as dstFile:
            for line in lines:
                matcher = re.match('testerfile : (.*)', line)
                if matcher:
                    if self.tester_file_to_be_created is None:
                        self.tester_file_name = matcher.group(1)
                        self.tester_file_to_be_created = os.path.join(self.working_path, self.tester_file_name)
                    line = 'testerfile : ' + self.tester_file_name + '\n'

                matcher = re.match('.*:\s+((.*)/.*)', line)
                if matcher:
                    subfile_list.append(matcher.group(1))
                    if not matcher.group(2) in subfile_folder_list:
                        subfile_folder_list.append(matcher.group(2))
                dstFile.write(line)

        # Assemble the master file into tester file
        os.system(self.CMD_ASSEMBLE + self.master_file_to_be_assembled)

        # Delete log
        if os.path.exists(os.path.join(self.working_path, 'changelog.txt')):
            os.system('rm -rf ' + os.path.join(self.working_path, 'changelog.txt'))

        # Delete master file and subfiles if '-d' is selected
        if self.is_delete_subfile_folder:
            for subfile in subfile_list:
                if os.path.exists(os.path.join(self.working_path, subfile)):
                    os.system('rm -rf ' + os.path.join(self.working_path, subfile))

            for subfile_folder in subfile_folder_list:
                subfile_folder_path = os.path.join(self.working_path, subfile_folder)
                log_file = os.path.join(subfile_folder_path + '/changelog.txt')
                if os.path.exists(log_file):
                    os.system('rm ' + log_file)
                if not os.listdir(subfile_folder_path):
                    if os.path.exists(subfile_folder_path):
                        os.system('rm -rf ' + subfile_folder_path)
                os.system('rm -rf ' + self.master_file_to_be_assembled)

    def run(self):
        self.__parse_options()


if __name__ == '__main__':
    smartMFH = SmartestMFH()
    smartMFH.run()
