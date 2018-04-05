'''
Created on Apr 1, 2018

@author: demo
'''

import os
import py_compile

if __name__ == '__main__':
    for dirpath, dirnames, filenames in os.walk(os.getcwd()):
        for filename in filenames:
            if (filename.endswith('.py')):
                py_file = os.path.join(dirpath, filename)
                pyc_file = os.path.join(dirpath, filename.replace('.py', '.pyc'))
                print(py_file)
                py_compile.compile(py_file, pyc_file)
