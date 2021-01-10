@echo off
rem lappdeploy
rem This script launches the installer package of the standard application. See 
rem Usage description syntax for details about used syntax. 
rem
rem Usage: lappdeploy [set]
rem     set is the set name, the script use a file named applist-[set].txt which
rem     describing applications to install. 'all' is the default value.
rem 
rem Exit code
rem     0: no error
rem     1: an error occurred while filtering application
rem     2: invalid argument. An argument of the command line is not valid (see Usage)
rem 
setlocal
pushd "%~dp0"

rem Setting the environment
rem Execute initialization hook ***
if exist .\__init__.cmd call .\__init__.cmd

rem Theses settings may be overwritten in the current execution environment.
rem By default, data files including installer packages were stored in the appstore directory.
if not defined APP_STORE_DIR set APP_STORE_DIR=..\appstore

rem By default, no mail with the content of the below log files is sent to a sysadmin
rem (see _log2mail script). To prevent this behavior, you must set the LOGMAIL environment variable to 1.
if not defined LOGMAIL set LOGMAIL=0
if not defined SMTP_SERVER_PORT set SMTP_SERVER_PORT=25

rem By default, the message log are only write in the log file. To have a copy on the standard 
rem output, you must set the SILENT environment variable to 0. 
rem By default, only the Error, Warning or Informational entry are logged. You can tuned this behavior
rem by setting the LOGLEVEL environment variable.
rem     LOGLEVEL=ERROR: only the Error entry are logged  
rem     LOGLEVEL=WARNING: only the Error or Warning entry are logged
rem     LOGLEVEL=INFO: only the Error, Warning or Informational entry are logged
rem     LOGLEVEL=DEBUG: all the entry are logged
if not defined UPDATE_LOGFILE  set UPDATE_LOGFILE=%TEMP%\appdeploy_today.log
if not defined WARNING_LOGFILE set WARNING_LOGFILE=%TEMP%\appdeploy_warn_today.log
if not defined SUMMARY_LOGFILE set SUMMARY_LOGFILE=%TEMP%\appdeploy_summary_today.log
if not defined ARCHIVE_LOGFILE set ARCHIVE_LOGFILE=%SystemRoot%\lappdeploy.log
if not defined SILENT          set SILENT=1
if not defined LOGLEVEL        set LOGLEVEL=INFO
if exist "%UPDATE_LOGFILE%" del "%UPDATE_LOGFILE%"
if exist "%WARNING_LOGFILE%" del "%WARNING_LOGFILE%"
if exist "%SUMMARY_LOGFILE%" del "%SUMMARY_LOGFILE%"
Rem in case of error, the info level is selected
set LOGERROR=1
set LOGWARNING=1
set LOGINFO=1
set LOGDEBUG=
if %LOGLEVEL%==ERROR (
    set LOGERROR=1
    set LOGWARNING=
    set LOGINFO=
    set LOGDEBUG=
)
if %LOGLEVEL%==WARNING (
    set LOGERROR=1
    set LOGWARNING=1
    set LOGINFO=
    set LOGDEBUG=
)
if %LOGLEVEL%==DEBUG (
    set LOGERROR=1
    set LOGWARNING=1
    set LOGINFO=1
    set LOGDEBUG=1
)
rem Each release of lAppUpdate is identified by a version number that complies 
rem with the Semantic Versioning 2.0.0 standard (see http://semver.org/).
set APPDEPLOY_VERSION=0.2.5

goto Main  

rem **** This section contains the subroutine used by the script by a recurse call (see call)
rem ****
rem WriteErrorLog
rem     Write a error entry in log file or on console output (based on the syslog format) 
rem     Usage call :WriteErrorLog string...
rem         string: is the string explaining the log entry 
:WriteErrorLog
if not defined LOGERROR goto :EOF
echo %DATE% %TIME%; %COMPUTERNAME%; %~nx0 [ERROR]; %* >>"%UPDATE_LOGFILE%"
if %SILENT%==0 echo %DATE% %TIME%; %COMPUTERNAME%; %~nx0 [ERROR]; %*
echo %DATE% %TIME%; %COMPUTERNAME%; %~nx0 [ERROR]; %* >>"%WARNING_LOGFILE%"
goto :EOF

rem WriteWarningLog
rem     Write a warning entry in log file or on console output (based on the syslog format) 
rem     Usage call :WriteWarningLog string...
rem         string: is the string explaining the log entry 
:WriteWarningLog
if not defined LOGWARNING goto :EOF
echo %DATE% %TIME%; %COMPUTERNAME%; %~nx0 [WARNING]; %* >>"%UPDATE_LOGFILE%"
if %SILENT%==0 echo %DATE% %TIME%; %COMPUTERNAME%; %~nx0 [WARNING]; %*
echo %DATE% %TIME%; %COMPUTERNAME%; %~nx0 [WARNING]; %* >>"%WARNING_LOGFILE%"
goto :EOF

rem WriteInfoLog
rem     Write an informational entry in log file or on console output (based on the syslog format) 
rem     Usage call :WriteInfoLog string...
rem         string: is the string explaining the log entry 
:WriteInfoLog
if not defined LOGINFO goto :EOF
echo %DATE% %TIME%; %COMPUTERNAME%; %~nx0 [INFO]; %* >>"%UPDATE_LOGFILE%"
if %SILENT%==0 echo %DATE% %TIME%; %COMPUTERNAME%; %~nx0 [INFO]; %*
goto :EOF

rem WriteDebugLog
rem     Write a debugging entry in log file or on console output (based on the syslog format) 
rem     Usage call :WriteDebugLog string...
rem         string: is the string explaining the log entry 
:WriteDebugLog
if not defined LOGDEBUG goto :EOF
echo %DATE% %TIME%; %COMPUTERNAME%; %~nx0 [DEBUG]; %* >>"%UPDATE_LOGFILE%"
if %SILENT%==0 echo %DATE% %TIME%; %COMPUTERNAME%; %~nx0 [DEBUG]; %*
goto :EOF

rem WriteSummary
rem     Write a summary entry in summary log file or on console output
rem     Usage call :WriteSummary string...
rem         string: is the string explaining the log entry 
:WriteSummary
echo %* >>"%SUMMARY_LOGFILE%"
goto :EOF

rem ArchiveAndCleanUp
rem     Copy the today log file in the archive log file
rem     Usage call :ArchiveAndCleanUp
:ArchiveAndCleanUp
if exist "%ARCHIVE_LOGFILE%" echo -------------------------------------------------------------------------------->>"%ARCHIVE_LOGFILE%"
type "%UPDATE_LOGFILE%" >>"%ARCHIVE_LOGFILE%" 2>&1
if exist "%UPDATE_LOGFILE%" del "%UPDATE_LOGFILE%"
if exist "%WARNING_LOGFILE%" del "%WARNING_LOGFILE%"
if exist "%SUMMARY_LOGFILE%" del "%SUMMARY_LOGFILE%"
rem Execute completion hook ***
if exist .\__exit__.cmd call .\__exit__.cmd
goto :EOF

rem InstallExe
rem     Execute the installation package and the postinstall script if it exist.
rem     Usage call :Install package options...
rem         package: is the full name of the installation package
rem         options: are the command line options of the installation package (specific to the package) 
:InstallExe
call :WriteInfoLog Executing %*
call %*>>"%UPDATE_LOGFILE%" 2>&1
if errorlevel 1 (
    call :WriteWarningLog Installation of %* failed ^(Errorlevel: %errorlevel%^)
) else (
    call :WriteInfoLog Installation of %* succeded
)
if not exist "%~dp1__postinstall__.cmd" goto :EOF
call "%~dp1__postinstall__.cmd">>"%UPDATE_LOGFILE%" 2>&1
if errorlevel 1 (
    call :WriteWarningLog Post Installation of "%~dp1__postinstall__.cmd" failed ^(Errorlevel: %errorlevel%^)
) else (
    call :WriteInfoLog Post Installation of "%~dp1__postinstall__.cmd" succeded
)
goto :EOF

rem InstallMSI
rem     Execute the MSI package with the optional transform file and the postinstall script if it exist.
rem     Usage call :Install package ...
rem         package: is the full name of the installation package
:InstallMSI
if exist "%~dpn1.mst" (
  call :WriteInfoLog Installing "%~dpn1.msi" using "%~dpn1.mst"...
  @%SystemRoot%\System32\msiexec.exe /package "%~dpn1.msi" ALLUSER=2 TRANSFORMS="%~dpn1.mst" /quiet /norestart /log "%TEMP%\%~n1.log"
  if errorlevel 1 (
    call :WriteWarningLog Installation of "%~dpn1.msi" using "%~dpn1.mst" failed
  ) else (
    call :WriteInfoLog Installed "%~dpn1.msi" using "%~dpn1.mst"
  )  
) else (
  call :WriteInfoLog Installing "%~dpn1.msi"...
  @%SystemRoot%\System32\msiexec.exe /package "%~dpn1.msi" ALLUSER=2 /quiet /norestart /log "%TEMP%\%~n1.log"
  if errorlevel 1 (
    call :WriteWarningLog Installation of "%~dpn1.msi" failed ^(Errorlevel: %errorlevel%^)
  ) else (
    call :WriteInfoLog Installed "%~dpn1.msi"
  )  
)
if not exist "%~dp1__postinstall__.cmd" goto :EOF
call "%~dp1__postinstall__.cmd">>"%UPDATE_LOGFILE%" 2>&1
if errorlevel 1 (
    call :WriteWarningLog Post Installation of "%~dp1__postinstall__.cmd" failed ^(Errorlevel: %errorlevel%^)
) else (
    call :WriteInfoLog Post Installation of "%~dp1__postinstall__.cmd" succeded
)
goto :EOF

:Main
call :WriteInfoLog Starting AppDeploy (%APPDEPLOY_VERSION%)
call :WriteSummary Starting AppDeploy (%APPDEPLOY_VERSION%)
call :WriteDebugLog Used path '%CD%' on %COMPUTERNAME% (user: %USERNAME%)
call :WriteDebugLog Command line  '%CMDCMDLINE%'

rem *** Setting the environment ***
set CSCRIPT_PATH=%SystemRoot%\System32\cscript.exe
if not exist %CSCRIPT_PATH% goto NoCScript
set REG_PATH=%SystemRoot%\System32\reg.exe
if not exist %REG_PATH% goto NoReg
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
set SETNAME=%1

call :WriteInfoLog Building the application list...
set APPLIST_PREFIX=applist-
set APPLIST=%TEMP%\applist.txt
if exist "%APPLIST%" del "%APPLIST%"
echo.>> "%APPLIST%"
if exist "%APP_STORE_DIR%\%APPLIST_PREFIX%all.txt" (
    copy /Y "%APP_STORE_DIR%\%APPLIST_PREFIX%all.txt" "%APPLIST%" >nul
)
if "%SETNAME%"=="" goto :SkipSet
if exist "%APP_STORE_DIR%\%APPLIST_PREFIX%%SETNAME%.txt" (
    echo.>> "%APPLIST%"
    type "%APP_STORE_DIR%\%APPLIST_PREFIX%%SETNAME%.txt" >> "%APPLIST%"
    call :WriteInfoLog Set %SETNAME% selected
    call :WriteSummary Set %SETNAME% selected
) else (
    call :WriteWarningLog Set named %SETNAME% do not exist
)
:SkipSet
set APPLIST_TO_INSTALL=%TEMP%\apptoinstall.txt
call :WriteInfoLog Checking installed applications
if exist "%APPLIST_TO_INSTALL%" del "%APPLIST_TO_INSTALL%"
%CSCRIPT_PATH% //Nologo //Job:appfilter _appfilter.wsf %OS_ARCH%
if errorlevel 1 goto CustSoftFail

if not exist "%APPLIST_TO_INSTALL%" goto NoApp
call :WriteInfoLog Install the missing application or upgrade it
for /F "delims=; tokens=1,2,3*" %%i in (%APPLIST_TO_INSTALL%) do (
    call :WriteSummary Installing %%i ^(%%j^)
    if /i "%%~xk"==".msi" (
        call :InstallMSI "%%~k"
    ) else (
        call :InstallEXE "%%~k" %%l
    )
)
del "%APPLIST_TO_INSTALL%"
del "%APPLIST%"
set APPINSTALLED=1
call :WriteInfoLog Applications installation completed
goto Cleanup

rem this section contain the exception and error treatment
:NoApp
set APPINSTALLED=
call :WriteInfoLog no application to install
goto cleanup

:CustSoftFail
call :WriteErrorLog Applications installation failed
rem archive the current log and send a mail to sysadmin
if %LOGMAIL%==1 %CSCRIPT_PATH% //Nologo //E:vbs _log2mail.vbs "%SUMMARY_LOGFILE%" "%WARNING_LOGFILE%" "%UPDATE_LOGFILE%"
call :ArchiveAndCleanUp
endlocal                                                       
exit /b 1

:NoCScript
call :WriteErrorLog VBScript interpreter %CSCRIPT_PATH% not found
rem archive the current log and send a mail to sysadmin
call :ArchiveAndCleanUp
endlocal                                                       
exit /b 1

:NoReg
call :WriteErrorLog Registry tool %REG_PATH% not found
rem archive the current log and send a mail to sysadmin
if %LOGMAIL%==1 %CSCRIPT_PATH% //Nologo //E:vbs _log2mail.vbs "%SUMMARY_LOGFILE%" "%WARNING_LOGFILE%" "%UPDATE_LOGFILE%"
call :ArchiveAndCleanUp
endlocal                                                       
exit /b 1

:Usage
call :WriteErrorLog  Usage: %0 [set].
call :WriteErrorLog  set is the set name, the script use a file named applist-[set].txt
call :WriteErrorLog  which describing applications to install. all is the default value.
rem archive the current log and send a mail to sysadmin
if %LOGMAIL%==1 %CSCRIPT_PATH% //Nologo //E:vbs _log2mail.vbs "%SUMMARY_LOGFILE%" "%WARNING_LOGFILE%" "%UPDATE_LOGFILE%"
call :ArchiveAndCleanUp
popd
endlocal
exit /b 2

:Cleanup 
rem archive the current log and send a mail to sysadmin
if defined APPINSTALLED (
    if %LOGMAIL%==1 %CSCRIPT_PATH% //Nologo //E:vbs _log2mail.vbs "%SUMMARY_LOGFILE%" "%WARNING_LOGFILE%" "%UPDATE_LOGFILE%"
)
call :ArchiveAndCleanUp
popd
endlocal
exit /b 0