@echo off
setlocal
	set BASE=%~dp0
	%BASE%..\ListSourceFiles.py %*
endlocal
