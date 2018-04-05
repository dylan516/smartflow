'''

@author: Dylan
'''
import os

if __name__ == '__main__':
    os.chdir(os.path.join(os.path.dirname(__file__), 'modules'))
    for module in os.listdir():
        if (module.endswith('.tar.gz')):
            os.system('pip3 install ' + module)

    # Copy smartflow examples
    os.system('cp /home/wafer/python3/lib/python3.6/site-packages/smartflow/examples/*.py .')
