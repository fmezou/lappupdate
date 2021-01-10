' _logmgr
' This script offers logging facilities.
' 
' This script is a Windows Script one.  Thus, it must be used launch with 
' cscript command.(e.g. cscript.exe _appfilter.vbs x64) 
' 
' The log files are specified in the below environment variables.
'   %SUMMARY_LOGFILE%: contains the installation summary
'   %WARNING_LOGFILE%: contains the warning messages occurred while script 
'   execution
'   %UPDATE_LOGFILE%: contains all messages occurred while script execution
'

' Constant for the run-time
Private Const LOG_FOR_READING    = 1
Private Const LOG_FOR_APPENDING  = 8

Dim objShell, objFileSystem, numReturn
Dim objSummaryLogFile, objWarningLogFile, objUpdateLogFile, numSilentMode
Dim blnLogError, blnLogWarning, blnLogInfo, blnLogDebug

Sub InitializeLog
    ' see InstallApp script for details about the logging system
    Dim lstrLogFileName, lstrString
    Set objShell = WScript.CreateObject("WScript.Shell")
    Set objFileSystem = CreateObject("Scripting.FileSystemObject")
    
    lstrLogFileName=objShell.ExpandEnvironmentStrings("%SUMMARY_LOGFILE%")
    If (objFileSystem.FileExists(lstrLogFileName)) Then
        Set objSummaryLogFile = objFileSystem.OpenTextFile(lstrLogFileName, LOG_FOR_APPENDING)
    Else
        Set objSummaryLogFile = objFileSystem.CreateTextFile(lstrLogFileName)
    End If
    
    lstrLogFileName = objShell.ExpandEnvironmentStrings("%WARNING_LOGFILE%")
    If (objFileSystem.FileExists(lstrLogFileName)) Then
        Set objWarningLogFile = objFileSystem.OpenTextFile(lstrLogFileName, LOG_FOR_APPENDING)
    Else
        Set objWarningLogFile = objFileSystem.CreateTextFile(lstrLogFileName)
    End If
     
    lstrLogFileName = objShell.ExpandEnvironmentStrings("%UPDATE_LOGFILE%")
    If (objFileSystem.FileExists(lstrLogFileName)) Then
        Set objUpdateLogFile = objFileSystem.OpenTextFile(lstrLogFileName, LOG_FOR_APPENDING)
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
