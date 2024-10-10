"""

###########################################
# FUNCTIONS AND LOOPING COMMAND ASSEMBLY CODES
###########################################

def return_comand():
    return ("@LCL\nAM=M-1\nD=M\n@SP\nAM=M-1\nD=M-D\n"
            "@ISTRUE\nD;JGT\nD=0\n@ISFALSE\n0;JMP\n"
            "(ISTRUE)\nD=-1\n(ISFALSE)\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
"""

"""Below are just assembly codes for functions asm as well as branching asm. will have to work on them later"""
"""            
             return
               @LCL
               D=M
               @frame
               M=D // FRAME = LCL
               @5
               D=D-A
               A=D
               D=M
               @return_address
               M=D // RET = *(FRAME-5)
               @SP
               M=M-1
               A=M
               D=M
               @ARG
               A=M
               M=D // *ARG = pop()
               @ARG
               D=M+1
               @SP
               M=D // SP = ARG+1
               @frame
               D=M-1
               A=D
               D=M
               @THAT
               M=D // THAT = *(FRAME-1)
               @2
               D=A
               @frame
               D=M-D
               A=D
               D=M
               @THIS
               M=D // THIS = *(FRAME-2)
               @3
               D=A
               @frame
               D=M-D
               A=D
               D=M
               @ARG
               M=D // ARG = *(FRAME-3)
               @4
               D=A
               @frame
               D=M-D
               A=D
               D=M
               @LCL
               M=D // LCL = *(FRAME-4)
               @return_address
               A=M
               0;JMP // goto RET
               
               """
"""
               @return address
               D=A
               @SP
               A=M
               M=D
               @SP
               M=M+1
               // push LCL
               @LCL
               D=M
               @SP
               A=M
               M=D
               @SP
               M=M+1
               // push ARG
               @ARG
               D=M
               @SP
               A=M
               M=D
               @SP
               M=M+1
               // push THIS
               @THIS
               D=M
               @SP
               A=M
               M=D
               @SP
               M=M+1
               // push THAT
               @THAT
               D=M
               @SP
               A=M
               M=D
               @SP
               M=M+1
               // ARG = SP-n-5
               @SP
               D=M
               @{n_args}
               D=D-A
               @5
               D=D-A
               @ARG
               M=D
               // LCL = SP
               @SP
               D=M
               @LCL
               M=D
               // goto f
               @{function_name}
               0;JMP
               (returnaddress)
               
               """
"""
if got to
 @SP
               M=M-1
               A=M
               D=M
               @{label}
               D;JNE
"""
""""Darcy


// return"
	;; Step 1: Save the local segment address in R13
	"@LCL"	; Goto LCL, which points to the local segment ...
	"D=M" 	; ... store that address in D ...
	"@R13"	; ... goto R13 ...
	"M=D" 	; ... store that address in R13.
	;; Step 2: Save the return address in R14
	"@5"  	; Get value 5 ...
	"A=D-A"   ; ... and subtract it from D, so A points to the retun address.
	"D=M" 	; Save the return address in M ...
	"@R14"	; ... goto R14 ...
	"M=D" 	; ... store the return address in R14.
	;; Step 3: Write the return value in @ARG
	"@SP" 	; Stack pointer
	"A=M" 	; Goto the address indicated by the pointer
	"A=A-1"   ; Move to the top of the working stack (the return value)
	"D=M" 	; Store the value of the working stack in D
	"@SP" 	; Stack pointer
	"M=M-1"   ; Move the stack pointer back
	"@ARG"	; Goto ARG, which points to the argument segment ...
	"A=M" 	; ... jump to Argument 0
	"M=D" 	; ... set Argument 0 to the return value.
	;; Step 4: Move SP to after Argumet 0
	"@ARG"	; Goto ARG, which now holds the return value ...
	"D=M+1"   ; ... store ARG address + 1 ...
	"@SP" 	; Stack pointer ...
	"M=D" 	; ... now points to ARG address +1.
	;; Step 5: Restore THAT from saved frame
	"@R13"	; Goto R13 (pointing to the start of the local segment) ...
	"A=M" 	; ... jump to the start of the local segment ...
	"A=A-1"   ; ... step back 1 to THAT in saved frame ...
	"D=M" 	; ... store saved-frame THAT in D ...
	"@R13"	; ... goto R13 ...
	"M=M-1"   ; ... point to saved-frame THAT ...
	"@THAT"   ; Goto THAT ...
	"M=D" 	; ... and set it to the value of the saved THAT.
	;; Step 6: Restore THIS from saved frame
	"@R13"	; Goto R13 (pointing to saved THAT) ...
	"A=M" 	; ... jump to the THIS in saved frame ...
	"A=A-1"   ; ... step back 1 to saved-frame THIS ...
	"D=M" 	; ... store saved-frame THIS in D ...
	"@R13"	; ... goto R13 ...
	"M=M-1"   ; ... point to saved-frame THIS ...
	"@THIS"   ; Goto THIS ...
	"M=D" 	; ... and set it to the value of the saved THIS.
	;; Step 7: Restore ARG from saved frame
	"@R13"	; Goto R13 (pointing to saved THIS)
	"A=M" 	; ... jump to saved THIS ...
	"A=A-1"   ; ... step back 1 to saved-frame ARG ...
	"D=M" 	; ... store saved-frame THIS in D ...
	"@R13"	; ... goto R13 ...
	"M=M-1"   ; ... point to saved-frame ARG ...
	"@ARG"	; Goto ARG ...
	"M=D" 	; ... and set it to the value of the saved ARG.
	;; Step 8: Restore LCL from saved frame
	"@R13"	; Goto R13 (pointing to saved ARG)
	"A=M" 	; ... jump to saved ARG ...
	"A=A-1"   ; ... step back 1 to saved-fram LCL ...
	"D=M" 	; ... store saved-frame LCL in D ...
	"@LCL"	; Goto LCL ...
	"M=D" 	; ... and set it to the value of the saved LCL.
	;; Step 9: Jump to return address
	"@R14"	; Goto R14 (pointing to the return address)
	"A=M" 	; ... set address to the return address ...
	"0;JMP"], ; ... and jump unconditionally.
"""