#!/usr/bin/env python3
'''
Master file creating and assembling tool
    
@author: dylan
@version: V1.0(2018.2.28): Initial version.
'''

import getopt
import os
import re
import shutil

import sys


class SmartestMFH():
    '''
    SmartestMFH class 
    '''

    # Declare constants
    MFH_LOC = "/opt/hp93000/soc/com/SETUP_MAN/smartest_mfh ";
    CMD_CREATE = MFH_LOC + "create ";
    CMD_SPLIT = MFH_LOC + "split ";
    CMD_ASSEMBLE = MFH_LOC + "assemble ";
    FILE_TYPE = (
    "level", "timing", "waveform", "analog_control", "testtable", "testflow", "routing", "config", "testtable")

    def __init__(self):
        '''
        Constructor: Parse arguments
        '''
        # Declare variables
        self.working_path = os.getcwd();

        # -c
        self.tester_file_to_be_split = ""
        self.master_file_to_be_created = ""

        # -a
        self.master_file_to_be_assembled = ""
        self.tester_file_to_be_created = None
        self.tester_file_name = ""

        # -d
        self.is_delete_subfile_folder = False

        # -s
        self.specified_subfiles = None

        self.basename = ""
        self.fileExt = ""
        self.filetype = ""
        self.subfiles_folder_path = ""
        self.subfiles_folder_basename = "subfiles"
        self.mfh_option = "-h";

    def get_filetype(self, working_path):
        filetype = os.path.split(working_path)[1]
        if (filetype == "levels"):
            filetype = "level"
        elif (filetype == "configuration"):
            filetype = "config"
        return filetype

    def parse_arguments(self):
        opts, () = getopt.getopt(sys.argv[1:], "c:a:o:s:dh",
                                 ["create", "assemble", "output", "subfiles", "delete", "help"])

        for op, value in opts:
            if (op in ("-c", "--create")):
                self.mfh_option = "-c"
                self.working_path = os.path.split(os.path.realpath(value))[0]
                self.basename, self.fileExt = os.path.splitext(os.path.split(os.path.realpath(value))[1])
                self.filetype = self.get_filetype(self.working_path)
                self.tester_file_to_be_split = value
            elif (op in ("-a", "--assemble")):
                self.mfh_option = "-a"
                self.working_path = os.path.split(os.path.realpath(value))[0]
                self.basename, self.fileExt = os.path.splitext(os.path.split(os.path.realpath(value))[1]);
                self.filetype = self.get_filetype(self.working_path)
                self.master_file_to_be_assembled = value
            elif (op in ("-o", "--output")):
                if (self.mfh_option == "-c"):
                    self.basename = os.path.splitext(value)[0]
                elif (self.mfh_option == "-a"):
                    self.tester_file_name = value
                    self.tester_file_to_be_created = os.path.join(self.working_path, value)
            elif (op in ("-s", "--subfiles")):
                self.specified_subfiles = value
            elif (op in ("-d", "--delete")):
                self.is_delete_subfile_folder = True
            elif (op in ("-h", "--help")):
                self.mfh_option = "-h"

    def usage(self):
        print("Usage: Create or assemble master file.")
        print("\tsmartest_mfh [OPTION]... [FILE]...")

        print("Options:")

        print("\t-c:    Create master file.")
        print("\t\t smartest_mfh -c <setup_file>\n")

        print("\t-a:    Assemble master file.")
        print("\t\t smartest_mfh -a <master_file>\n")

        print("\t-o:    Specify the name of output master file or tester file.")
        print("\t\t smartest_mfh -c <setup_file> -o <output_master_file>")
        print("\t\t smartest_mfh -a <master_file> -o <output_tester_file>\n")

        print("\t-s:    Specify the subfile folder name along with creating master file.")
        print("\t\t smartest_mfh -a <master_file> -s <subfiles_folder>")
        print("\t\t smartest_mfh -a <master_file> -s <subfiles_folder> -o <output_tester_file>\n")

        print("\t-d:    Delete master file and subfiles folder along with assembling.")
        print("\t\t smartest_mfh -a <master_file> -d")
        print("\t\t smartest_mfh -a <master_file> -o <output_tester_file> -d\n")

        print("\t-h:    Show help.")

    def create_subfiles_folder(self):
        if (self.specified_subfiles):
            self.subfiles_folder_basename = self.specified_subfiles
        else:
            self.subfiles_folder_basename = "subfiles_" + self.basename

        if (self.filetype in self.FILE_TYPE):
            self.subfiles_folder_path = os.path.join(self.working_path, self.subfiles_folder_basename)
            if not os.path.exists(self.subfiles_folder_path):
                os.mkdir(self.subfiles_folder_path);

    def create_mfh(self):
        # Create subfiles folder
        self.create_subfiles_folder()
        self.master_file_to_be_created = os.path.join(self.working_path, self.basename + ".mfh")

        # Create the master file
        os.system(self.CMD_CREATE + self.filetype + " " + self.master_file_to_be_created)

        # Copy mfh file to subfolder
        subfolder_mfh_file = os.path.join(self.subfiles_folder_path, self.basename + ".mfh")
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
                    matcher = re.match("testerfile : (.*)", line);
                    if (matcher):
                        line = "testerfile : " + self.tester_file_to_be_split + "\n\n";
                    else:
                        matcher = re.match("(.*: )(.*\.\w+)", line);
                        if (matcher):
                            line = matcher.group(1) + self.subfiles_folder_basename + "/" + matcher.group(2) + "\n";
                    dstFile.write(line);

        # Clean up
        os.system("rm " + subfolder_mfh_file);
        os.system("rm " + self.subfolder_testerfile);
        os.system("rm -rf " + os.path.join(self.working_path, "changelog.txt"));

    def assemble_mfh(self):
        subfile_list = []
        subfile_folder_list = []

        with open(self.master_file_to_be_assembled, 'r') as srcFile:
            lines = srcFile.readlines()

        with open(self.master_file_to_be_assembled, 'w') as dstFile:
            for line in lines:
                matcher = re.match("testerfile : (.*)", line)
                if (matcher):
                    if (self.tester_file_to_be_created == None):
                        self.tester_file_name = matcher.group(1)
                        self.tester_file_to_be_created = os.path.join(self.working_path, self.tester_file_name)
                    line = "testerfile : " + self.tester_file_name + "\n";

                matcher = re.match(".*:\s+((.*)/.*)", line)
                if (matcher):
                    subfile_list.append(matcher.group(1))
                    if not matcher.group(2) in subfile_folder_list:
                        subfile_folder_list.append(matcher.group(2))
                dstFile.write(line);

        # Assemble the master file into tester file
        os.system(self.CMD_ASSEMBLE + self.master_file_to_be_assembled)

        # Delete log
        if (os.path.exists(os.path.join(self.working_path, "changelog.txt"))):
            os.system("rm -rf " + os.path.join(self.working_path, "changelog.txt"));

        # Delete master file and subfiles if "-d" is selected
        if (self.is_delete_subfile_folder == True):
            for subfile in subfile_list:
                if (os.path.exists(os.path.join(self.working_path, subfile))):
                    os.system("rm -rf " + os.path.join(self.working_path, subfile));

            for subfile_folder in subfile_folder_list:
                subfile_folder_path = os.path.join(self.working_path, subfile_folder)
                log_file = os.path.join(subfile_folder_path + "/changelog.txt");
                if (os.path.exists(log_file)):
                    os.system("rm " + log_file)
                if not os.listdir(subfile_folder_path):
                    if (os.path.exists(subfile_folder_path)):
                        os.system("rm -rf " + subfile_folder_path)
                os.system("rm -rf " + self.master_file_to_be_assembled);

    def run(self):
        self.parse_arguments()

        if (self.mfh_option == "-c"):
            self.create_mfh()
        elif (self.mfh_option == "-a"):
            self.assemble_mfh()
        elif (self.mfh_option == "-h"):
            self.usage()


if __name__ == '__main__':
    smartMFH = SmartestMFH()
    smartMFH.run()
