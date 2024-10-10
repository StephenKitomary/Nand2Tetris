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