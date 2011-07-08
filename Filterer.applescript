on run
	tell application "BibDesk"
		try
			set alertResult to display alert ("Really remove all linked files and private notes from " & name of first document as string) & "?" buttons {"Cancel", "OK"} default button "OK" cancel button "Cancel" as warning
			
			if button returned of alertResult is "OK" then
				save first document in "Filtered " & (name of first document as string) & ".bib"
				repeat with thePub in first document's publications
					set thePub's note to my splitNote(thePub's note)
					repeat with theFile in thePub's linked files
						remove theFile from thePub
					end repeat
				end repeat
				save first document
			end if
		on error -128
			display dialog "User cancelled."
		end try
	end tell
end run

to splitNote(theNoteText)
	try
		set oldDelims to AppleScript's text item delimiters
		set AppleScript's text item delimiters to {"---"}
		
		set theParts to every text item of theNoteText
		
		if length of theParts is greater than 1 then
			set outText to text 2 through end of last item of theParts
		else
			set outText to ""
		end if
		set AppleScript's text item delimiters to oldDelims
	on error
		set AppleScript's text item delimiters to oldDelims
	end try
	return outText
end splitNote