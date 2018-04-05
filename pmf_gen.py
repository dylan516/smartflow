'''

@author: Dylan
'''

import os
from optparse import OptionParser

import sys

from smartflow.flowparser.Utils import info_msg, error_msg


class PMF_Generator(object):
    def __init__(self):
        self.__parse_options()

    def __parse_options(self):
        description = "Generate pattern master file."

        parser = OptionParser(description=description)
        parser.add_option("-i", dest="vector_path", metavar='PATH', default='',
                          help="Specify the path of vectors. Default is <device>/vectors folder")
        parser.add_option("-s", dest="subfiles_path", metavar='NAME',
                          help="Specify the name of subfiles folder. Default is vectors path name.")
        parser.add_option("-o", dest="pmf_file", metavar='FILE',
                          help="Specify the output pattern master file. Default is <vector_path_name>.pmf")

        options, () = parser.parse_args()

        # Parse options
        self.vector_path = os.path.join(os.getcwd(), options.vector_path).rstrip('/')
        basename = os.path.basename(self.vector_path)

        if (options.subfiles_path):
            self.subfiles_path = os.path.join(os.getcwd(), options.subfiles_path)
        else:
            self.subfiles_path = 'subfiles_' + basename

        if (options.pmf_file):
            self.pmf_file = os.path.join(options.pmf_file)
        else:
            self.pmf_file = basename + '.pmf'

    def run(self):
        if (os.path.basename(os.getcwd()) != 'vectors'):
            error_msg('Please execute the tool under <device>/vectors folder.')
            sys.exit()

        if (not os.path.exists(self.subfiles_path)):
            os.makedirs(self.subfiles_path)

        # Create the main pmf
        info_msg('Create pattern master file: %s\n' % self.pmf_file)
        with open(self.pmf_file, 'w') as main_pmf:
            main_pmf.write('hp93000,pattern_master_file,0.1\n\n')
            main_pmf.write('-- this is a comment (dash dash space)\n\n')

            for dirpath, dirnames, filenames in os.walk(self.vector_path):  # @UnusedVariable
                if os.path.basename(dirpath) == '.cache':
                    continue

                if (len(filenames) > 0):
                    # Create a sub pmf
                    sub_pmf_file = '%s/%s.pmf' % (self.subfiles_path, os.path.basename(dirpath))
                    info_msg('Add: %s' % sub_pmf_file)
                    with open(sub_pmf_file, 'w+') as sub_pmf:
                        rel_path = os.path.relpath(dirpath, os.getcwd() + '../')

                        sub_pmf.write('hp93000,pattern_master_file,0.1\n\n')
                        sub_pmf.write('-- this is a comment (dash dash space)\n\n')
                        sub_pmf.write('path:\n')
                        sub_pmf.write('%s\n' % rel_path)
                        sub_pmf.write('files:\n\n')
                        if (filenames):
                            filenames.sort()
                        for filename in filenames:
                            sub_pmf.write(filename + '\n')

                        main_pmf.write('#include "%s/%s.pmf"\n' % (
                            os.path.basename(self.subfiles_path), os.path.basename(dirpath)))


if __name__ == '__main__':
    pmf = PMF_Generator()
    pmf.run()
