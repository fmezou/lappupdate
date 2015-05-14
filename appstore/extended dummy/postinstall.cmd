@echo off
rem Ce script réalise les opérations de postinstallation.
rem Ces opérations se limite au déplacement des racourci du menu démarrer.
set StartMenuPath=\Microsoft\Windows\Start Menu\Programs
set AllUsersStartMenuPath=%ALLUSERSPROFILE%%StartMenuPath%
set LocalStartMenuPath=%APPDATA%%StartMenuPath%
echo a dummy extented postinstaller installer... dummy application fixed