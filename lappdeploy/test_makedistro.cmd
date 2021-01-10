@echo off
echo ---------------------------------------------------------------------------
echo -- Test#1: normal use case
call make_mozilla_distro.cmd "Firefox Setup 70.0-x64.exe"
if ERRORLEVEL 0 (
	echo -- OK
) else (
	echo -- KO [make_mozilla_distro: %errorlevel%] 
)
echo ---------------------------------------------------------------------------
echo -- Test#2: corrupted installer 
call make_mozilla_distro.cmd "Firefox Setup 70.0-x64-ERR.exe"
if ERRORLEVEL 1 (
	echo -- OK
) else (
	echo -- KO [make_mozilla_distro: %errorlevel%]
)
echo ---------------------------------------------------------------------------
echo -- Test#3: missing tool
rename ..\..\..\bin\7za.exe ~7za.exe
call make_mozilla_distro.cmd "Firefox Setup 70.0-x64.exe"
if ERRORLEVEL 3 (
	echo -- OK
) else (
	echo -- KO [make_mozilla_distro: %errorlevel%]
)
rename ..\..\..\bin\~7za.exe 7za.exe
echo ---------------------------------------------------------------------------
echo -- Test#4: missing policies
rename policies.json ~policies.json
call make_mozilla_distro.cmd "Firefox Setup 70.0-x64.exe"
if ERRORLEVEL 4 (
	echo -- OK
) else (
	echo -- KO [make_mozilla_distro: %errorlevel%]
)
rename ~policies.json policies.json
