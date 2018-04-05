#!/home/wafer/python3/bin/python3
'''

@author: Dylan
'''
import os

if __name__ == '__main__':
    os.system('rm -rf smartflow/examples/*.py')
    os.system('cp *.py smartflow/examples/.')
    os.system('rm smartflow/examples/setup.py')
    os.system('python3 setup.py sdist')
    os.system('pip3 uninstall smartflow')
    os.system('pip3 install dist/*.tar.gz')

    # Copy smartflow examples
    os.system('rm /Unix_TAE3/ScriptsReleased/*.py')
    os.system('cp /home/wafer/python3/lib/python3.6/site-packages/smartflow/examples/*.py /Unix_TAE3/ScriptsReleased/.')

    # Setup alias
    os.chdir('/Unix_TAE3/ScriptsReleased/')
