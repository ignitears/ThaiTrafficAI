Set WshShell = CreateObject("WScript.Shell")
' Uses pythonw.exe to run the UI without a console window
WshShell.Run chr(34) & ".venv\Scripts\pythonw.exe" & chr(34) & " launcher.py", 0
Set WshShell = Nothing