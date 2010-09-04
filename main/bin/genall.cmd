@echo off
setlocal
	set BASE=%~dp0
	%BASE%..\GenerateAll.py %*
endlocal
