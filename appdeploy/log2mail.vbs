' log2mail
' This script send the current AppDeploy log messages to a sysadmin in a mail.
'
' Usage : log2mail
'
' Exit code
'   0 : no error
'   1 : the summary log doesn't exist
'
' The log files are specified in the below environment variables.
'   %SUMMARY_LOGFILE% : contains the installation summary
'   %WARNING_LOGFILE% : contains the warning messages occurred while script
'    execution 
'   %UPDATE_LOGFILE% : contains all messages occurred while  script execution 
'
' The SMTP configuration is specified in the below environment variables.
'   %SYSADM_TO_ADDR% : contains the mail address where log files are sent.       
'   %SMTP_SERVER% : contains the fully qualified name of the SMTP server to use.  
'   %SMTP_SERVER_PORT% : contains the SMTP server's port number to use. 
'
' This script use the Collaboration Data Objects Messaging 
' (see https://msdn.microsoft.com/en-us/library/ms527568%28v=exchg.10%29.aspx)
' and is inspired from the "VBScript To Send Email Using CDO" from Paul Sadowski
' (http://www.paulsadowski.com/wsh/cdo.htm)

Option Explicit
' Constant for the run-time
Private Const ForReading = 1

Private Const STR_SUBJECT = "AppDeploy"

Dim wshShell, objFileSystem, objMessage
Dim strLogFileName, objLogFile
Dim numLog2MailError

' Set the useful object and default value
Set wshShell = WScript.CreateObject("WScript.Shell")
Set objFileSystem = CreateObject("Scripting.FileSystemObject")
numLog2MailError=0

' Create the mail
Set objMessage = CreateObject("CDO.Message")
objMessage.Subject = STR_SUBJECT
objMessage.From = LCase(wshShell.ExpandEnvironmentStrings("%COMPUTERNAME%") & "." & wshShell.ExpandEnvironmentStrings("%USERDNSDOMAIN%")& "@free.fr")
objMessage.To = wshShell.ExpandEnvironmentStrings("%SYSADM_TO_ADDR%")
objMessage.TextBody = LCase(wshShell.ExpandEnvironmentStrings("%COMPUTERNAME%") & "." & wshShell.ExpandEnvironmentStrings("%USERDNSDOMAIN%")) & " AppDeploy log messages" & vbCrlf 

' Add the summary
strLogFileName=wshShell.ExpandEnvironmentStrings("%SUMMARY_LOGFILE%")
objMessage.TextBody = objMessage.TextBody & "* Summary *" & vbCrlf 
If not (objFileSystem.FileExists(strLogFileName)) Then
    objMessage.Subject = STR_SUBJECT & " Error"
    objMessage.TextBody = objMessage.TextBody & "The AppDeploy summary log ("&strLogFileName&") doesn't exist." & vbCrlf
    numLog2MailError=1
Else
    ' Add the content of the current log
    Set objLogFile = objFileSystem.OpenTextFile(strLogFileName, ForReading, False)
    objMessage.TextBody = objMessage.TextBody & objLogFile.ReadAll
    objLogFile.Close
End If

if (numLog2MailError=0) Then 
    ' Add the Warning (optional)
    strLogFileName=wshShell.ExpandEnvironmentStrings("%WARNING_LOGFILE%")
    if (objFileSystem.FileExists(strLogFileName)) Then
        ' Add the content of the current log 
        objMessage.TextBody = objMessage.TextBody & "-------------------------------------------------------------------------" & vbCrlf
        objMessage.TextBody = objMessage.TextBody & "* Warning *" & vbCrlf 
        Set objLogFile = objFileSystem.OpenTextFile(strLogFileName, ForReading, False)
        objMessage.TextBody = objMessage.TextBody & objLogFile.ReadAll
        objLogFile.Close
    End If

    ' Add the today log file in attachment (optional)
    strLogFileName=wshShell.ExpandEnvironmentStrings("%UPDATE_LOGFILE%")
    if (objFileSystem.FileExists(strLogFileName)) Then
        objMessage.AddAttachment objFileSystem.GetAbsolutePathName(strLogFileName)
    End If
End If

' Set the mailer configuration
objMessage.Configuration.Fields.Item("http://schemas.microsoft.com/cdo/configuration/sendusing")=2
objMessage.Configuration.Fields.Item("http://schemas.microsoft.com/cdo/configuration/smtpserver")=wshShell.ExpandEnvironmentStrings("%SMTP_SERVER%")
objMessage.Configuration.Fields.Item("http://schemas.microsoft.com/cdo/configuration/smtpserverport")=wshShell.ExpandEnvironmentStrings("%SMTP_SERVER_PORT%")
objMessage.Configuration.Fields.Update

'Send
objMessage.Send

Set objMessage = nothing
Set objFileSystem = nothing
Set wshShell = nothing

WScript.Quit(numLog2MailError)
