@echo off
del .\status_lock.apworld
robocopy .\worlds\status_lock .\status_lock\status_lock /E /XF gen_apworld.bat archive.py /NFL /NDL /NJH
python .\worlds\status_lock\archive.py -Path .\status_lock\ -DestinationPath .\status_lock.zip -Force
del /Q /S .\status_lock >nul
move .\status_lock.zip .\status_lock.apworld
start .\status_lock.apworld
