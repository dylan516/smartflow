#!/usr/bin/env python3

import os

if __name__ == '__main__':
    os.system('python3 setup.py sdist')
    os.system('pip3 uninstall smartflow')
    os.system('pip3 install dist/*.tar.gz')
