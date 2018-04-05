'''

@author: Dylan
'''
import os

import sys

if __name__ == '__main__':
    print('\033[1;34m' + '=' * 80 + '\033[0m')
    print('# Added for python scripts')

    py_loc = sys.argv[1]
    for pyfile in os.listdir(py_loc):
        if (pyfile.endswith('.py')):
            alias = pyfile[:-3]
            abspath = os.path.abspath(os.path.join(py_loc, pyfile))
            print("alias %s='python3 %s'" % (alias, abspath))
    print('\033[1;34m' + '=' * 80 + '\033[0m')
    os.system('nedit ~/.bashrc &')
    print('\033[1;34mPlease copy above alias to $HOME/.bashrc.\033[0m')
