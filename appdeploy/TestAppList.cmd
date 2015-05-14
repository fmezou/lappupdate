@echo off
rem This command file check the applist file.
rem le 29/10/2014 - version 1.0 - F. MEZOU - creation
setlocal

rem *** Setting the environnement ***
if /i "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
  set OS_ARCH=x64
) else (
  if /i "%PROCESSOR_ARCHITEW6432%"=="AMD64" (
    set OS_ARCH=x64
  ) else (
    set OS_ARCH=x86
  )
)

rem *** parsing the command line ***
Set SETNAME=%1
goto Proceed

:CheckAppPackage
rem echo %*
if "%~1"=="AddCustomMSI" (
	call %*
	goto :EOF
)
if exist "%~1" goto :EOF
echo Warning: Installation package "%~1" don't exist
goto :EOF

:Proceed
echo Building the application list...
set APPLIST_PREFIX=applist-
set APPLIST=%TEMP%\applist.txt
if exist "%APPLIST%" del "%APPLIST%"
copy /Y "%APPLIST_PREFIX%all.txt" "%APPLIST%" >nul
if "%SETNAME%"=="" goto :SkipSet
if exist "%APPLIST_PREFIX%%SETNAME%.txt" (
  echo.>> "%APPLIST%"
  type "%APPLIST_PREFIX%%SETNAME%.txt" >> "%APPLIST%"
) else (
  echo Warning: set named %SETNAME% don't exist
)
:SkipSet
if exist "%TEMP%\appmsi.txt" del "%TEMP%\appmsi.txt"
echo Checking installations packages...
for /F "delims=; tokens=4" %%i in (%APPLIST%) do (
	call :CheckAppPackage %%i
)
if not exist "%TEMP%\appmsi.txt" goto :SkipMSI
for /F "delims=; tokens=*" %%i in (%TEMP%\appmsi.txt) do (
	call :CheckAppPackage "%%i"
)
echo Completed.
del %TEMP%\appmsi.txt
:SkipMSI
del %TEMP%\applist.txt
goto Cleanup

:CustSoftFail
echo.
echo ERROR: Executed App installation failed.
echo.
endlocal
exit /b 1

:Usage
echo.
echo Usage : %0 [computername or set].
echo     computername or set : is the computer name or set name, this software use the file
echo     named applist-[set].txt to select the application to install. all is the default value.
echo.
endlocal
exit /b 2

:Cleanup 
endlocal
exit /b 0