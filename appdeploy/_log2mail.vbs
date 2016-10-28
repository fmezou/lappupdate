' _log2mail
' This script sends a mail containing the current lappdeploy log messages. See
' Usage description syntax for details about used syntax.
'
' This script is a Windows Script one. Thus, it must be used launch with cscript 
' command. (e.g. cscript.exe _log2mail.vbs) 
'
' Usage: _log2mail
'
' Exit code
'   0: no error
'   1: the summary log doesn't exist
'   2: the server name is empty or not defined (fix %SMTP_SERVER% environment 
'      variable)
'   3: the recipient mail address is empty or not defined (fix %TO_MAIL_ADDR%
'      environment variable)  
'
' The SMTP configuration is specified in the below environment variables.
'   %TO_MAIL_ADDR%:  contains the mail address of the mail recipient
'   (typically a system administrator)
'   %FROM_MAIL_ADDR% :	Contain the mail address of the mail sender (typically machine mail address)       
'   %SMTP_SERVER%: contains the fully qualified name of the SMTP server to use  
'   %SMTP_SERVER_PORT%: contains the SMTP server's port number to use
'
' The log files are specified in the below environment variables.
'   %SUMMARY_LOGFILE%: contains the installation summary
'   %WARNING_LOGFILE%: contains the warning messages occurred while script
'    execution 
'   %UPDATE_LOGFILE%: contains all messages occurred while  script execution 
'
' This script use 'Microsoft Collaboration Data Objects for Windows 2000' 
' (see https://msdn.microsoft.com/en-us/library/ms527568%28v=exchg.10%29.aspx)
' and is inspired from the 'VBScript To Send Email Using CDO' from Paul Sadowski
' (see http://www.paulsadowski.com/wsh/cdo.htm)

Option Explicit
' Constant for the run-time
Private Const ForReading = 1

Private Const STR_SUBJECT = "AppDeploy"

Dim wshShell, objFileSystem, objMessage, strSMTPServer, strSMTPServerPort, strMailAddr
Dim strLogFileName, objLogFile
Dim numLog2MailError

' Set the useful object and default value
Set wshShell = WScript.CreateObject("WScript.Shell")
Set objFileSystem = CreateObject("Scripting.FileSystemObject")
numLog2MailError=0

' Check environment
' When the environment variable is not defined, the ExpandEnvironmentStrings 
' method returns the name of environment variable including % character.
strSMTPServer=Trim(wshShell.ExpandEnvironmentStrings("%SMTP_SERVER%"))
If (strSMTPServer="" Or Left(strSMTPServer,1)="%") Then
    numLog2MailError=2
Else
    strSMTPServerPort=Trim(wshShell.ExpandEnvironmentStrings("%SMTP_SERVER_PORT%"))
    If (strSMTPServerPort="" Or Left(strSMTPServerPort,1)="%") Then
        strSMTPServerPort="25" ' Default value for SMTP port number.
    End If
End If
If (numLog2MailError=0) Then 
    strMailAddr=Trim(wshShell.ExpandEnvironmentStrings("%TO_MAIL_ADDR%"))
    If (strMailAddr="" Or Left(strMailAddr,1)="%") Then
        numLog2MailError=3
    End If
End If

If (numLog2MailError=0) Then 
    ' Create the mail
    Set objMessage = CreateObject("CDO.Message")
    objMessage.Subject = LCase(wshShell.ExpandEnvironmentStrings("%COMPUTERNAME%")) & " lappdeploy results"
    objMessage.From = LCase(wshShell.ExpandEnvironmentStrings("%FROM_MAIL_ADDR%"))
    objMessage.To = strMailAddr
    objMessage.TextBody = LCase(wshShell.ExpandEnvironmentStrings("%COMPUTERNAME%")) & " lappdeploy log messages" & vbCrlf

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

    ' Set the mailer configuration
    objMessage.Configuration.Fields.Item("http://schemas.microsoft.com/cdo/configuration/sendusing")=2
    objMessage.Configuration.Fields.Item("http://schemas.microsoft.com/cdo/configuration/smtpserver")=strSMTPServer
    objMessage.Configuration.Fields.Item("http://schemas.microsoft.com/cdo/configuration/smtpserverport")=strSMTPServerPort
    objMessage.Configuration.Fields.Update

    'Send
    objMessage.Send
End If

Set objMessage = nothing
Set objFileSystem = nothing
Set wshShell = nothing

WScript.Quit(numLog2MailError)
