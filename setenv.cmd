@echo off
rem Set the environment variables for the project
rem Add the source root
set PYTHONPATH = %PYTHONPATH%; %CD%\lapptrack; %CD%\tests
ver
echo Environment tuned for the lAppUpdate project
