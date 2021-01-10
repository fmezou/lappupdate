Option Explicit
InitializeLog

TestVersionId "32.0.0.125", "32.0.0.125", 0
TestVersionId "32.0", "32.0.0.125", -1
TestVersionId "32.0.0", "32.0.0.125", -1
TestVersionId "32.0.0.125a", "32.0.0.125", 1
TestVersionId "", "32.0.0.125", Null
TestVersionId "32.a.0.125", "32.0.0.125", Null
TestVersionId "32.0.0.125", "33.0.0.125", -1
TestVersionId "32.0.0.125", "32.1.0.125", -1
TestVersionId "32.0.0.125", "32.0.1.125", -1
TestVersionId "32.0.0.125", "32.0.1.126", -1
TestVersionId "32.0.0.125", "32.10.0.125", -1
TestVersionId "32.10.0.125", "32.0.0.125", 1
TestVersionId "3.01", "3.01", 0
TestVersionId "3.01", "3.02", -1
TestVersionId "3.01", "3.00", 1
TestVersionId "3.01", "3.01a", -1
TestVersionId "3.01e", "3.01a", 1
TestVersionId "300", "301", Null
TestVersionId "v15.1.2", "v15.1.3", -1
TestVersionId "v15.1.2", "15.1.2", 0
TestVersionId "1.2.3", "1.2.4", -1
TestVersionId "3.a.0.1", "", Null
TestVersionId Empty, Empty, Null
TestVersionId Null, Null, Null

TerminateLog
WScript.Quit(0)

Sub TestVersionId (pstrVersId1, pstrVersId2, pnumExpected)
    Dim lstrExpected, lnumCmpResult
    
    If IsNull(pnumExpected) Then
        lstrExpected = PrintVersionId(pstrVersId1) & " or " &_
        PrintVersionId(pstrVersId2) & " is not a valid version identifier"
    ElseIf pnumExpected = -1 Then
        lstrExpected = PrintVersionId(pstrVersId1) & " < " &_
        PrintVersionId(pstrVersId2)
    ElseIf pnumExpected = 0 Then
        lstrExpected = PrintVersionId(pstrVersId1) & " = " &_
        PrintVersionId(pstrVersId2)
    ElseIf pnumExpected = 1 Then
        lstrExpected = PrintVersionId(pstrVersId1) & " > " &_
        PrintVersionId(pstrVersId2)
    Else
        lstrExpected = "Expected result is unknown '" & pnumExpected & "'"
    End If
        
    lnumCmpResult = CompareVersionId(pstrVersId1, pstrVersId2)
    If IsNull(lnumCmpResult) Then
        If IsNull(pnumExpected) Then
            WScript.Echo "OK: " & lstrExpected
        Else
            WScript.Echo "*KO*: " & lstrExpected
        End If
    Else 
        If lnumCmpResult = pnumExpected Then
            WScript.Echo "OK: " & lstrExpected
        Else
            WScript.Echo "*KO*: " & lstrExpected
        End If
    End If
End Sub
