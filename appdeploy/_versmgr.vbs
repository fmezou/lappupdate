' _versmgr
' This script offers version comparison facilities.
' 
' This script is a Windows Script one.  Thus, it must be used launch with 
' cscript command.(e.g. cscript.exe _appfilter.vbs x64) 
' 
Function CompareVersionId(pstrVersId1, pstrVersId2)
    Dim lVersIdParts1, lVersIdParts2
    Dim i
    
    CompareVersionId = 0
    
    If Not(IsNull(pstrVersId1) Or IsNull(pstrVersId2)) Then
        lVersIdParts1 = ParseVersionId(pstrVersId1)
        lVersIdParts2 = ParseVersionId(pstrVersId2)
        If Not (UBound(lVersIdParts1) = 0 Or UBound(lVersIdParts2) = 0) Then
            i = 0
            Do
                If i = 3 Then
                    CompareVersionId = StrComp(lVersIdParts1(i), _
                                               lVersIdParts2(i), vbTextCompare)
                Else
                    If lVersIdParts1(i) > lVersIdParts2(i) Then
                        CompareVersionId = 1
                    Else
                        If lVersIdParts1(i) < lVersIdParts2(i) Then
                            CompareVersionId = -1
                        End If
                    End If
                End If
                WriteDebugLog "CompareVersionId - "& i &_
                "/"&UBound(lVersIdParts1)&":" & lVersIdParts1(i) & " vs " &_
                lVersIdParts2(i) & " -> "& CompareVersionId
                i = i + 1
            Loop While i < UBound(lVersIdParts1) and CompareVersionId = 0
        Else
            WriteDebugLog "ParseVersionId: " &_ 
            PrintVersionId(pstrVersId2) & " or " &_ 
            PrintVersionId(pstrVersId2) & " is not a valid version identifier"
            CompareVersionId = Null
        End If
    Else
        WriteDebugLog "ParseVersionId: " &_
        PrintVersionId(pstrVersId2) & " or " & PrintVersionId(pstrVersId2) &_ 
        " is not a valid version identifier"
        CompareVersionId = Null
    End If
End Function

Function ParseVersionId (pstrVersId)
    Dim lVersIdParts()
    
    ParseVersionId = ParseVariant2VersionId(pstrVersId)
    If UBound(ParseVersionId) <> 0 Then
        WriteDebugLog "ParseVersionId: " &_
        PrintVersionId(pstrVersId) & " is a variant #2 form"
        WriteDebugLog "ParseVersionId: " & _
        PrintVersionId(ParseVersionId) 
    Else
        ParseVersionId = ParseVariant1VersionId(pstrVersId)
        If UBound(ParseVersionId) <> 0 Then
            WriteDebugLog "ParseVersionId: " &_
            PrintVersionId(pstrVersId) & " is a vA.B.C.D form"
            WriteDebugLog "ParseVersionId: " & _
            PrintVersionId(ParseVersionId) 
        Else
            ParseVersionId = ParseUsualVersionId(pstrVersId)
            If UBound(ParseVersionId) <> 0 Then
                WriteDebugLog "ParseVersionId: " &_
                PrintVersionId(pstrVersId) & " is a A.B.C.D form"
                WriteDebugLog "ParseVersionId: " &_
                PrintVersionId(ParseVersionId) 
            Else
                ReDim lVersIdParts(0)
                ParseVersionId = lVersIdParts
                WriteDebugLog "ParseVersionId: " &_
                PrintVersionId(pstrVersId) & " is an unknown form"
            End If
        End If
    End If
End Function

Function ParseUsualVersionId (pstrVersId)
    ' Parse a version string identifer with the form A.B.C.D where each part
    ' is optional and is an positive integer except for the last part .
    Dim lParts, lVersIdParts(), lobjRegEx
    Dim i

    ReDim lVersIdParts(4)
    lVersIdParts(0) = 0 'Major
    lVersIdParts(1) = 0 'Minor
    lVersIdParts(2) = 0 'Patch
    lVersIdParts(3) = "" 'Build and other information
    
    Set lobjRegEx = New RegExp
    lobjRegEx.IgnoreCase = False
    lobjRegEx.Pattern = "(\d+\.)+\d+"
    If lobjRegEx.Test(pstrVersId) Then
        lParts = Split(pstrVersId, ".")
        For i = 0 to UBound(lParts)
            If IsNumeric(lParts(i)) Then
                lVersIdParts(i) = CInt(lParts(i))
            Else
                If i = 3 Then
                    lVersIdParts(i) = lParts(i)
                Else
                    ReDim lVersIdParts(0)
                    Exit For
                End If
            End if
        Next
    Else
        ReDim lVersIdParts(0)
    End If
    ParseUsualVersionId = lVersIdParts
End Function

Function ParseVariant1VersionId (pstrVersId)
    ' Parse a version string identifer with the form vA.B.C.D where each part
    ' is optional and is an positive integer except for the last part. The 
    ' prefix v may be a letter and will ignored.
    Dim lParts, lVersIdParts(), lobjRegEx, lstrMinorPart

    ReDim lVersIdParts(4)
    lVersIdParts(0) = 0 'Major
    lVersIdParts(1) = 0 'Minor
    lVersIdParts(2) = 0 'Patch
    lVersIdParts(3) = "" 'Build and other information
    
    Set lobjRegEx = New RegExp
    lobjRegEx.IgnoreCase = False
    lobjRegEx.Pattern = "[a-z](\d+\.)+\d+"
    If lobjRegEx.Test(pstrVersId) Then
        ParseVariant1VersionId = ParseUsualVersionId(Right(pstrVersId, _
                                                           Len(pstrVersId)-1))
    Else
        ReDim lVersIdParts(0)
        ParseVariant1VersionId = lVersIdParts
    End If
End Function

Function ParseVariant2VersionId (pstrVersId)
    ' Parse a version string identifer with the form A.BC where C is a letter
    ' specifiying the patch level
    Dim lParts, lVersIdParts(), lobjRegEx, lstrMinorPart

    ReDim lVersIdParts(4)
    lVersIdParts(0) = 0 'Major
    lVersIdParts(1) = 0 'Minor
    lVersIdParts(2) = 0 'Patch
    lVersIdParts(3) = "" 'Build and other information
    
    Set lobjRegEx = New RegExp
    lobjRegEx.IgnoreCase = False
    lobjRegEx.Pattern = "\d+\.\d+[a-z]{1}"
    If lobjRegEx.Test(pstrVersId) Then
        lParts = Split(pstrVersId, ".")
        If IsNumeric(lParts(0)) Then
            lVersIdParts(0)=CInt(lParts(0))
            lstrMinorPart = Left(lParts(1), Len(lParts(1))-1)
            If IsNumeric(lstrMinorPart) Then
                lVersIdParts(1) = CInt(lstrMinorPart)
                lVersIdParts(2) = Asc(Right(lParts(1), 1))
            Else
                ReDim lVersIdParts(0)
            End If
        Else
            ReDim lVersIdParts(0)
        End If
    Else
        ReDim lVersIdParts(0)
    End If
    ParseVariant2VersionId = lVersIdParts
End Function

Function PrintVersionId (pVersionId)
    Dim lnumType
    
    lnumType = VarType(pVersionId)
    If lnumType = 1 Then ' Null (no valid data)
        PrintVersionId = "(Null)"
    ElseIf lnumType = 0 Then ' Empty (uninitialized)
        PrintVersionId = "(Empty)"
    ElseIf (lnumType And 8192) Then ' Array
        If UBound(pVersionId) = 0 Then
           PrintVersionId = "(Empty Array)"
        Else
           PrintVersionId = "(" & PrintVersionId(pVersionId(0)) &_
                            "), (" & PrintVersionId(pVersionId(1)) &_
                            "), (" & PrintVersionId(pVersionId(2)) &_
                            "), (" & PrintVersionId(pVersionId(3)) & ")"
        End If
    ElseIf lnumType = 8 Then ' String
        PrintVersionId = "'" & pVersionId & "'"
    ElseIf lnumType = 2 Then ' Integer subtype
        PrintVersionId = CStr(pVersionId)
    Else
        PrintVersionId = "UNKNOWN TYPE ("& lnumType & ")"
    End If
End Function
