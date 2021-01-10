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

set LOGMAIL=0
set UPDATE_LOGFILE=.\appdeploy_today.log
set WARNING_LOGFILE=.\appdeploy_warn_today.log
set SUMMARY_LOGFILE=.\appdeploy_summary_today.log
set SILENT=0
set LOGLEVEL=INFO
if exist "%UPDATE_LOGFILE%" del "%UPDATE_LOGFILE%"
if exist "%WARNING_LOGFILE%" del "%WARNING_LOGFILE%"
if exist "%SUMMARY_LOGFILE%" del "%SUMMARY_LOGFILE%"

rem *** Setting the environment ***
set CSCRIPT_PATH=%SystemRoot%\System32\cscript.exe
if not exist %CSCRIPT_PATH% goto NoCScript
%CSCRIPT_PATH% //Nologo //Job:test_versmgr _appfilter.wsf
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