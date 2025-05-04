Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "runapp.bat" & Chr(34), 0
Set WshShell = Nothing