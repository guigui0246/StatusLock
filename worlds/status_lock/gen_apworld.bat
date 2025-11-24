del .\status_lock.apworld
xcopy .\worlds\status_lock\*.* .\status_lock\status_lock\ /E /I /Y
powershell -command "Compress-Archive -Path '.\status_lock\*' -DestinationPath '.\status_lock.zip' -Force"
del /Q /S .\status_lock
move .\status_lock.zip .\status_lock.apworld
