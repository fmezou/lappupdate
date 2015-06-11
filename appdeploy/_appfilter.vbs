' _appfilter
' This script filters an applist file by verifying which applications were 
' installed and if it needed to be updated. See Usage description syntax for 
' details about used syntax.
' 
' This script is a Windows Script one.  Thus, it must be used launch with 
' cscript command.(e.g. cscript.exe _appfilter.vbs x64) 
' 
' Usage: _appfilter.vbs [{x86|x64}]
'   x86: specifies that the target architecture is a 32 bits one, therefore only 
'   32 bits installation packages taken into account. This is the default value.
'   x64: specifies that the target architecture is a 64 bits one, therefore only
'   64 bits installation packages taken into account.
' 
' Exit code
'   0: no error
'   1: an error occurred while filtering application
'   2: invalid argument. An argument of the command line is not valid 
' 
' The applist files are specified in the below environment variables.
'   %APPLIST%: contain the full pathname of the applist input file
'   %APPLIST_TO_INSTALL%: contain the full pathname of the output file. This 
'   file matches a subset of applist syntax by containing only appName, 
'   appVersion, appPackage and appArgs columns.
' 
' The log files are specified in the below environment variables.
'   %SUMMARY_LOGFILE%: contains the installation summary
'   %WARNING_LOGFILE%: contains the warning messages occurred while script 
'   execution
'   %UPDATE_LOGFILE%: contains all messages occurred while script execution
'
Option Explicit
' Constant for the run-time
Private Const FOR_READING    = 1
Private Const FOR_APPENDING  = 8

Private Const HKEY_LOCAL_MACHINE        = &H80000002
Private Const REG_KEY_UNINSTALL        = "Software\Microsoft\Windows\CurrentVersion\Uninstall"
Private Const REG_KEY_UNINSTALL32      = "Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
Private Const REG_VAL_DISPLAY_NAME      = "DisplayName"
Private Const REG_VAL_DISPLAY_VERSION   = "DisplayVersion"
Private Const APP_TOKEN = ";"

Dim objShell, objFileSystem, numReturn
Dim strTempFolder, strOutFileName, objOutFile
Dim strAppFileName, objAppFile
Dim strItems, strAppTarget, strArch, strAppName, strAppVersion, strAppPackage, strAppArgs
Dim objSummaryLogFile, objWarningLogFile, objUpdateLogFile, numSilentMode
Dim blnLogError, blnLogWarning, blnLogInfo, blnLogDebug

Sub InitializeLog
    ' see InstallApp script for details about the logging system
    Dim lstrLogFileName, lstrString
    Set objShell = WScript.CreateObject("WScript.Shell")
    Set objFileSystem = CreateObject("Scripting.FileSystemObject")
    
    lstrLogFileName=objShell.ExpandEnvironmentStrings("%SUMMARY_LOGFILE%")
    If (objFileSystem.FileExists(lstrLogFileName)) Then
        Set objSummaryLogFile = objFileSystem.OpenTextFile(lstrLogFileName, FOR_APPENDING)
    Else
        Set objSummaryLogFile = objFileSystem.CreateTextFile(lstrLogFileName)
    End If
    
    lstrLogFileName = objShell.ExpandEnvironmentStrings("%WARNING_LOGFILE%")
    If (objFileSystem.FileExists(lstrLogFileName)) Then
        Set objWarningLogFile = objFileSystem.OpenTextFile(lstrLogFileName, FOR_APPENDING)
    Else
        Set objWarningLogFile = objFileSystem.CreateTextFile(lstrLogFileName)
    End If
     
    lstrLogFileName = objShell.ExpandEnvironmentStrings("%UPDATE_LOGFILE%")
    If (objFileSystem.FileExists(lstrLogFileName)) Then
        Set objUpdateLogFile = objFileSystem.OpenTextFile(lstrLogFileName, FOR_APPENDING)
    Else
        Set objUpdateLogFile = objFileSystem.CreateTextFile(lstrLogFileName)
    End If
    
    numSilentMode=CInt(objShell.ExpandEnvironmentStrings("%SILENT%"))
    lstrString = objShell.ExpandEnvironmentStrings("%LOGLEVEL%")
    'in case of error, the info level is selected
    blnLogError     = True
    blnLogWarning   = True
    blnLogInfo      = True
    blnLogDebug     = False
    Select Case lstrString
        Case "ERROR"
            blnLogError     = True
            blnLogWarning   = False
            blnLogInfo      = False
            blnLogDebug     = False
        
        Case "WARNING"
            blnLogError     = True
            blnLogWarning   = True
            blnLogInfo      = False
            blnLogDebug     = False
            
        Case "DEBUG"
            blnLogError     = True
            blnLogWarning   = True
            blnLogInfo      = True
            blnLogDebug     = True
    End Select
 End Sub

Sub TerminateLog
    Dim lobjFile, lstrLogFileName
   
    objSummaryLogFile.Close
    objWarningLogFile.Close
    objUpdateLogFile.Close
    
    Set objFileSystem = CreateObject("Scripting.FileSystemObject")
    Set objShell = WScript.CreateObject("WScript.Shell")
    ' If a log is empty, the file is deleted to prevent error in _log2mail script
    lstrLogFileName=objShell.ExpandEnvironmentStrings("%SUMMARY_LOGFILE%")
    Set lobjFile = objFileSystem.GetFile(lstrLogFileName)
    If lobjFile.Size <= 2 Then
        lobjFile.Delete
    End If    
   
    lstrLogFileName = objShell.ExpandEnvironmentStrings("%WARNING_LOGFILE%")
    Set lobjFile = objFileSystem.GetFile(lstrLogFileName)
    If lobjFile.Size <= 2 Then
        lobjFile.Delete
    End If    
     
    lstrLogFileName = objShell.ExpandEnvironmentStrings("%UPDATE_LOGFILE%")
    Set lobjFile = objFileSystem.GetFile(lstrLogFileName)
    If lobjFile.Size <= 2 Then
        lobjFile.Delete
    End If
    Set objShell = Nothing
    Set objFileSystem = Nothing
End Sub

' WriteErrorLog
'   Write a error entry in log file or on console output (based on the syslog format) 
'   Usage: WriteErrorLog string
'       string: is the string explaining the log entry 
Sub WriteErrorLog (lstrEntry)
    Dim lstrTime, lstrDate, lstrComputerName, lstrScriptName, lstrFormated
    
    If (blnLogError) Then 
        lstrDate        = FormatDateTime(Now, vbShortDate)
        lstrTime        = FormatDateTime(Now, vbLongTime)& ",00" ' the millisecond are nore returned is VBscript so... 
        lstrComputerName= objShell.ExpandEnvironmentStrings("%COMPUTERNAME%")
        lstrScriptName  = WScript.ScriptName
        lstrFormated = lstrDate & " " & lstrTime & "; " & lstrComputerName & "; " & lstrScriptName & " [ERROR]; " & lstrEntry 
        objUpdateLogFile.WriteLine lstrFormated
        objWarningLogFile.WriteLine lstrFormated
        If (numSilentMode = 0) Then
             WScript.Echo(lstrFormated)
        End If
    End If
End Sub

' WriteWarningLog
'   Write a Warning entry in log file or on console output (based on the syslog format) 
'   Usage: WriteWarningLog string
'       string: is the string explaining the log entry 
Sub WriteWarningLog (lstrEntry)
    Dim lstrTime, lstrDate, lstrComputerName, lstrScriptName, lstrFormated
    
    If (blnLogWarning) Then 
        lstrDate        = FormatDateTime(Now, vbShortDate)
        lstrTime        = FormatDateTime(Now, vbLongTime)& ",00" ' the millisecond are nore returned is VBscript so... 
        lstrComputerName = objShell.ExpandEnvironmentStrings("%COMPUTERNAME%")
        lstrScriptName  = WScript.ScriptName
        lstrFormated = lstrDate & " " & lstrTime & "; " & lstrComputerName & "; " & lstrScriptName & " [WARNING]; " & lstrEntry 
        objUpdateLogFile.WriteLine lstrFormated
        objWarningLogFile.WriteLine lstrFormated
        If (numSilentMode = 0) Then
             WScript.Echo(lstrFormated)
        End If
    End If
End Sub

' WriteInfoLog
'   Write an informational entry in log file or on console output (based on the syslog format) 
'   Usage: WriteInfoLog string
'       string: is the string explaining the log entry 
Sub WriteInfoLog (lstrEntry)
    Dim lstrTime, lstrDate, lstrComputerName, lstrScriptName, lstrFormated
    
    If (blnLogInfo) Then
        lstrDate        = FormatDateTime(Now, vbShortDate)
        lstrTime        = FormatDateTime(Now, vbLongTime)& ",00" ' the millisecond are nore returned is VBscript so... 
        lstrComputerName = objShell.ExpandEnvironmentStrings("%COMPUTERNAME%")
        lstrScriptName  = WScript.ScriptName
        lstrFormated = lstrDate & " " & lstrTime & "; " & lstrComputerName & "; " & lstrScriptName & " [INFO]; " & lstrEntry 
        objUpdateLogFile.WriteLine lstrFormated
        If (numSilentMode = 0) Then
             WScript.Echo(lstrFormated)
        End If
    End If
End Sub

' WriteDebugLog
'   Write a debugging entry in log file or on console output (based on the syslog format) 
'   Usage: WriteDebugLog string
'       string: is the string explaining the log entry 
Sub WriteDebugLog (lstrEntry)
    Dim lstrTime, lstrDate, lstrComputerName, lstrScriptName, lstrFormated
    
    If (blnLogDebug) Then
        lstrDate        = FormatDateTime(Now, vbShortDate) 
        lstrTime        = FormatDateTime(Now, vbLongTime)& ",00" ' the millisecond are nore returned is VBscript so... 
        lstrComputerName = objShell.ExpandEnvironmentStrings("%COMPUTERNAME%")
        lstrScriptName  = WScript.ScriptName
        lstrFormated = lstrDate & " " & lstrTime & "; " & lstrComputerName & "; " & lstrScriptName & " [DEBUG]; " & lstrEntry 
        objUpdateLogFile.WriteLine lstrFormated
        If (numSilentMode = 0) Then
             WScript.Echo(lstrFormated)
        End If
    End If
End Sub

' WriteSummary
'   Write a summary entry in summary file or on console output
'   Usage: WriteSummary string
'       string: is the string explaining the log entry 
Sub WriteSummary (lstrEntry)
    Dim lstrTime, lstrDate, lstrComputerName, lstrScriptName, lstrFormated
    objSummaryLogFile.WriteLine lstrEntry
    If (numSilentMode = 0) Then
         WScript.Echo(lstrEntry)
    End If
End Sub

Function GetCleanItem (lstrItems)
    GetCleanItem=Trim(Replace(lstrItems, vbTab, " "))
End Function

Function GetParsedItem (ByRef lstrItems)
    Dim lnumStartToken, lnumEndToken

    GetParsedItem=Null
    lnumStartToken = InStr(1, lstrItems, APP_TOKEN, vbTextCompare)
    If lnumStartToken > 0 Then
        GetParsedItem=GetCleanItem(Left(lstrItems, lnumStartToken-1))
        strItems=Trim(Right(strItems, Len(lstrItems)-lnumStartToken))
    Else
        GetParsedItem=GetCleanItem(lstrItems)
        lstrItems=""
    End If
End Function

Function IsAppInstalled (ByVal lstrAppName, ByVal lstrAppVersion)
    Dim lobjWMIService, larraySubKeys, lstrSubKey, lstrInstAppName, lstrInstAppVersion, lnumReturn
    
    ' Default values
    IsAppInstalled=False
    
    ' If the sSubKeyName parameter (#2) constain a non exist key, the EnumKey Method set the sName parameter (#3) to null
    Set lobjWMIService = GetObject("winmgmts:" & "{impersonationLevel=impersonate}!\\.\root\default:StdRegProv")
    lobjWMIService.EnumKey HKEY_LOCAL_MACHINE, REG_KEY_UNINSTALL, larraySubKeys
    If IsArray(larraySubKeys) Then
        For Each lstrSubKey In larraySubKeys
            lobjWMIService.GetStringValue HKEY_LOCAL_MACHINE, REG_KEY_UNINSTALL & "\" & lstrSubKey, REG_VAL_DISPLAY_NAME, lstrInstAppName
            lobjWMIService.GetStringValue HKEY_LOCAL_MACHINE, REG_KEY_UNINSTALL & "\" & lstrSubKey, REG_VAL_DISPLAY_VERSION, lstrInstAppVersion
            lnumReturn=StrComp(lstrInstAppName, lstrAppName, vbTextCompare)
            If (lnumReturn = 0) Then 
                lnumReturn=StrComp(lstrInstAppVersion, strAppVersion, vbTextCompare)
                If (lnumReturn >= 0 or IsNull(lstrInstAppVersion)) Then ' Only newer versions takes into account.
                    IsAppInstalled=True
                    Exit For
                End If
            End If
        Next
    End If
    
    If not IsAppInstalled Then
        lobjWMIService.EnumKey HKEY_LOCAL_MACHINE, REG_KEY_UNINSTALL32, larraySubKeys
        If IsArray(larraySubKeys) Then
            For Each lstrSubKey In larraySubKeys
                lobjWMIService.GetStringValue HKEY_LOCAL_MACHINE, REG_KEY_UNINSTALL32 & "\" & lstrSubKey, REG_VAL_DISPLAY_NAME, lstrInstAppName
                lobjWMIService.GetStringValue HKEY_LOCAL_MACHINE, REG_KEY_UNINSTALL32 & "\" & lstrSubKey, REG_VAL_DISPLAY_VERSION, lstrInstAppVersion
                lnumReturn=StrComp(lstrInstAppName, lstrAppName, vbTextCompare)
                If (lnumReturn = 0) Then 
                    lnumReturn=StrComp(lstrInstAppVersion, lstrAppVersion, vbTextCompare)
                    If (lnumReturn >= 0 or IsNull(lstrInstAppVersion)) Then ' Only newer versions takes into account.
                        IsAppInstalled=True
                        Exit For
                    End If
                End If
            Next
        End If
    End If
End Function

'On Error Resume Next
InitializeLog
strArch="x86"
If WScript.Arguments.Count >= 1 Then
    strArch=LCase(WScript.Arguments(0))
    if not (strArch = "x86" or strArch = "x64") Then
        WriteErrorLog "Invalid Argument: Unknown OS Architecture ("&strArch&"). Must be x86 either x64."
        WScript.Quit(2)
    End If
End If

strAppFileName = objShell.ExpandEnvironmentStrings("%APPLIST%")
WriteDebugLog "Input file is: ["&strAppFileName&"]"
Set objAppFile = objFileSystem.OpenTextFile(strAppFileName, FOR_READING, False)
strOutFileName = objShell.ExpandEnvironmentStrings("%APPLIST_TO_INSTALL%")
WriteDebugLog "Output file is: ["&strOutFileName&"]"
Set objOutFile = objFileSystem.CreateTextFile(strOutFileName, True)

Do While objAppFile.AtEndOfStream <> True
    strItems=GetCleanItem(objAppFile.ReadLine)
    If (Left(strItems, 1) <> "#" And strItems <> "")   Then ' a comment line begin by a # char and empty line are ignored
        strAppTarget=LCase(GetParsedItem (strItems))
        strAppName=GetParsedItem (strItems)
        strAppVersion=GetParsedItem (strItems)
        strAppPackage=GetParsedItem (strItems)
        strAppArgs=GetParsedItem (strItems)
        ' to prevent having empty columns which are not well interpreted in dos shell...
        If strAppName = "" Then
            WriteWarningLog "No application name at line " & objAppFile.Line & ". Comment this line if it isn't useful"
            strAppName="undefined"
        End If
        If strAppVersion = "" Then
            WriteWarningLog "No version specified at line " & objAppFile.Line& " (" & strAppName &")"
            strAppVersion="undefined"
        End If
        Select Case strAppTarget
            Case "" ' work on both architecture
                If not IsAppInstalled (strAppName, strAppVersion) Then
                    If strAppPackage = "" Then
                        WriteWarningLog "No installation package for ["&strAppName&"] version ["&strAppVersion&"]"
                    Else
                        objOutFile.WriteLine(strAppName & APP_TOKEN & strAppVersion & APP_TOKEN & strAppPackage & APP_TOKEN & strAppArgs)
                    End If
                End If  
            
            Case "x86" ' need an 32 bits architecture
                If (strArch = "x86") Then
                    If not IsAppInstalled (strAppName, strAppVersion) Then
                        If strAppPackage = "" Then
                            WriteWarningLog "No installation package for ["&strAppName&"] version ["&strAppVersion&"]"
                        Else
                            objOutFile.WriteLine(strAppName & APP_TOKEN & strAppVersion & APP_TOKEN & strAppPackage & APP_TOKEN & strAppArgs)
                        End If
                    End If  
                End If
            
            Case "x64" ' need an 64 bits architecture
                If (strArch = "x64") Then
                    If not IsAppInstalled (strAppName, strAppVersion) Then
                        If strAppPackage = "" Then
                            WriteWarningLog "No installation package for ["&strAppName&"] version ["&strAppVersion&"]"
                        Else
                            objOutFile.WriteLine(strAppName & APP_TOKEN & strAppVersion & APP_TOKEN & strAppPackage & APP_TOKEN & strAppArgs)
                        End If
                    End If  
                End If
                        
            Case Else
                WriteErrorLog "Invalid target architecture type items for ["&strAppName&"]. Found: "&strAppTarget&" vs [x86 or x64]"
                WScript.Quit(1)
        End Select
    End if
Loop
objOutFile.Close
objAppFile.Close

' Delete id file if it does not contain valid data
Set objOutFile = objFileSystem.GetFile(strOutFileName)
If objOutFile.Size <= 2 Then
  objOutFile.Delete
End If

TerminateLog
WScript.Quit(0)
