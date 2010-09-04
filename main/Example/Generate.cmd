@echo off

::
:: This batchfile is the main demonstration of how the system generates .vcproj and .sln files.
::

setlocal
	set BASE=%~dp0
	
    pushd %BASE%
    
        call ..\bin\genall.cmd -s
    
    popd 
endlocal

pause
