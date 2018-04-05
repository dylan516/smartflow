#!/home/wafer/python3/bin/python3
'''
@author: Dylan

'''
import os
import shutil

if __name__ == '__main__':
    #     xls_prj_path = '/home/demo/Dylan/ScriptsReleased'
    #     prj_path = xls_prj_path

    xls_prj_path = '/home/wafer/Dylan/Hathi/ScriptsReleased'
    prj_path = '/Unix_TAE3/ScriptsReleased'

    shutil.copy('%s/smartflow/.sys/atpg_saf.xls' % xls_prj_path, 'atpg_saf.xls')
    shutil.copy('%s/smartflow/.sys/OSV_template.ttf' % xls_prj_path, '.OSV_template.ttf')
    shutil.copy('%s/smartflow/.sys/ATPG_SAF_template.ttf' % xls_prj_path, '.ATPG_SAF_template.ttf')

    os.system('python3 %s/saf_gen.py -i .ATPG_SAF_template.ttf -c atpg_saf.xls' % prj_path)
    os.system('python3 %s/saf_gen.py -i .OSV_template.ttf -c atpg_saf.xls -t osv' % prj_path)

    os.system('python3 %s/floweditor.py -i ATPG_SAF_PROD.ttf -c atpg_saf.xls -t vmin -o ATPG_SAF_VMIN.ttf' % prj_path)
    os.system('python3 %s/floweditor.py -i ATPG_SAF_PROD.ttf -c atpg_saf.xls -t fmax -o ATPG_SAF_FMAX.ttf' % prj_path)
    os.system('python3 %s/floweditor.py -i ATPG_SAF_PROD.ttf -c atpg_saf.xls -t shmoo -o ATPG_SAF_SHMOO.ttf' % prj_path)
