import os
def main():
    # we are going to take a case sensitive file name from the user, add .vm extension to it and then look it up in the directory
    input_file = input("Enter the finename that you want to translate (Case Sensitive): ")
    vm_file = input_file + ".vm"
    asm_file = input_file + ".asm"

    #lets first check if the type file name really exists
    if not os.path.isfile(vm_file):
        raise FileNotFoundError("The file you specified does not exist, please make sure it exists in the same directory as this code")
    
    #lets open the input file as read, and create an output file with write priviledges
    with open(vm_file, 'r') as file, open(asm_file,'w') as output:
        for line in file:
            stripped_line = line.strip()
            if stripped_line.startswith("//") or stripped_line == "":
                continue
            command_type, command_elements = parser(stripped_line)
            code_writer(output, command_type, command_elements, stripped_line)

    print("Translation has been completed")
 #Lets create a parser function that takes a single line as command and splits it into its elements
 
def parser(command):
    elements = command.split()
    # lets determine if the command is either a memory segmentation command or an Arithmentic command or an invalid command for now,
    # later should modify this to take in Branching commands 
    if elements[0] in ["push","pop"]:
        command_type =  "memory"
        return command_type, elements
    elif elements[0] in ["add","sub","neg","eg","gt","lt","and","or","not"]:
        command_type = "arithmetic"
        return command_type, elements
    else:
        raise ValueError("Unknown command found")

def code_writer(output, command_type, elements, original_command):
    #lets first write a comment that is the VM command on top before the ASM code, will be helpful in troubleshooting
    output.write(f"//{original_command}\n")

    if command_type =="memory":
        operation, segment, index = elements[0], elements[1], elements[2]
        if operation == "push":
            output.write(push_command(segment, index))
        elif operation =="pop":
            output.write(pop_command(segment, index))
    
    elif command_type == "arithmetic":
        output.write(arithmetic_command(elements[0]))
#here goes our push command operations, universal for all segment types except constant
def push_command(segment, index):
    if segment == "constant":
        return f"@{index}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
    else:
        segment_map = {
        "local": "LCL",
        "argument": "ARG",
        "this": "THIS",
        "that": "THAT"
    }
        asm_segment = segment_map.get(segment)
        return f"@{index}\nD=A\n@{asm_segment}\nA=M+D\nD=M\n@{asm_segment}\nA=M\nM=D\n@SP\nM=M+1\n"

    
    return ""

#here goes our pop command operations
def pop_command(segment, index):
    segment_map = {
        "local": "LCL",
        "argument": "ARG",
        "this": "THIS",
        "that": "THAT"
    }
    asm_segment = segment_map.get(segment)

    return f"@{index}\nD=A\n@{asm_segment}\nD=D+M\n@SP\nA=M\nM=D\n@SP\nA=M-1\nD=M\n@SP\nA=M\nA=M\nM=D\n@SP\nM=M-1\n"  
#here goes our arithmetic operations translations
def arithmetic_command(operation):
    
    if operation == "add":
        return "@SP\nAM=M-1\nD=M\nA=A-1\nM=M+D\n"
    elif operation == "sub":
        return "@SP\nAM=M-1\nD=M\nA=A-1\nM=M-D\n"
    elif operation == "neg":
        return "@SP\nA=M\nA=A-1\nM=-M\n"
    elif operation == "and":
        return "@SP\nAM=M-1\nD=M\nA=A-1\nM=D&M\n"
    elif operation == "or":
        return "@SP\nAM=M-1\nD=M\nA=A-1\nM=D|M\n"
    elif operation == "not":
        return "@SP\nA=M-1\nM=!M\n"
    elif operation == "eq":
        return eq_command()
    elif operation == "gt":
        return gt_command()
    elif operation == "lt":
        return lt_command()
    
    return ""

# Just for layout, writting all the big/long functions here as separate functions that will get called inside the arithmetic_command function
def eq_command():
    return ("@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nD=M-D\n"
            "@ISTRUE\nD;JEQ\nD=0\n@ISFALSE\n0;JMP\n"
            "(ISTRUE)\nD=-1\n(ISFALSE)\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
def gt_command():
    return ("@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nD=M-D\n"
            "@ISTRUE\nD;JGT\nD=0\n@ISFALSE\n0;JMP\n"
            "(ISTRUE)\nD=-1\n(ISFALSE)\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
def lt_command():
    return ("@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nD=M-D\n"
            "@ISTRUE\nD;JLT\nD=0\n@ISFALSE\n0;JMP\n"
            "(ISTRUE)\nD=-1\n(ISFALSE)\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")

#main process
if __name__ == "__main__":
    main()


###########################################
# FUNCTIONS AND LOOPING COMMAND ASSEMBLY CODES
###########################################
"""Below are just assembly codes for functions asm as well as branching asm."""
"""            @LCL
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
