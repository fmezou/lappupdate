@echo off
rem test
rem This script is the test launcher. 
rem
rem Exit code
rem     0: no error
rem     1: an error occurred while filtering application
rem     2: invalid argument. An argument of the command line is not valid (see Usage)
rem 
setlocal
pushd "%~dp0"

if /i "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
  set OS_ARCH=x64
) else (
  if /i "%PROCESSOR_ARCHITEW6432%"=="AMD64" (
    set OS_ARCH=x64
  ) else (
    set OS_ARCH=x86
  )
)
  
set LOGMAIL=0
set UPDATE_LOGFILE=.\appdeploy_today.log
set WARNING_LOGFILE=.\appdeploy_warn_today.log
set SUMMARY_LOGFILE=.\appdeploy_summary_today.log
set SILENT=0
set LOGLEVEL=INFO
if exist "%UPDATE_LOGFILE%" del "%UPDATE_LOGFILE%"
if exist "%WARNING_LOGFILE%" del "%WARNING_LOGFILE%"
if exist "%SUMMARY_LOGFILE%" del "%SUMMARY_LOGFILE%"

set APPLIST=.\test_applist.txt
set APPLIST_TO_INSTALL=.\test_appinstall.txt
if exist "%APPLIST_TO_INSTALL%" del "%APPLIST_TO_INSTALL%"

rem *** Setting the environment ***
set CSCRIPT_PATH=%SystemRoot%\System32\cscript.exe
if not exist %CSCRIPT_PATH% goto NoCScript
set JOB=//Job:test_appfilter
if not "%1" == "" set JOB=//Job:%1

%CSCRIPT_PATH% //Nologo %JOB% test_appfilter.wsf %OS_ARCH%
goto Cleanup

:NoCScript
echo (ERROR) VBScript interpreter %CSCRIPT_PATH% not found
endlocal                                                       
exit /b 1

:NoReg
echo (ERROR) Registry tool %REG_PATH% not found
endlocal                                                       
exit /b 1

:Cleanup 
popd
endlocal
exit /b 0