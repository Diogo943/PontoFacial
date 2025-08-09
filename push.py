import subprocess
import os
import pyautogui as auto
import time
os.startfile('C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Git\\Git Bash')

time.sleep(3)
auto.typewrite('cd PontoFacial_')
auto.press('enter')
'''
time.sleep(3)
auto.typewrite('git init')
auto.press('enter')'''

time.sleep(3)
auto.typewrite('git pull origin main')
auto.press('enter')

time.sleep(5)
usuario = os.environ.get('USERPROFILE')
os.startfile(f'{usuario}\\PontoFacial_\\model\\main.py')

time.sleep(2)
auto.typewrite('exit')
auto.press('enter')
