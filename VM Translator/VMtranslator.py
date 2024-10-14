import os

def main():
    # we are going to take a case-sensitive filename or directory from the user
    input_path = input("Enter the filename or directory you want to translate (Case Sensitive): ")

    # Check if the input is a file or directory
    if os.path.isfile(input_path):
        vm_files = [input_path]  # Single file
    elif os.path.isdir(input_path):
        # If it's a directory, gather all .vm files in the directory
        vm_files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith('.vm')]
        if not vm_files:
            raise FileNotFoundError("No .vm files found in the specified directory.")
    else:
        raise FileNotFoundError("The specified file or directory does not exist.")

    # Determine the output .asm file name
    if os.path.isfile(input_path):
        # If it's a file, name the output file based on the input file name
        asm_file = os.path.splitext(input_path)[0] + ".asm"
    else:
        # If it's a directory, name the output file after the directory
        asm_file = os.path.join(input_path, os.path.basename(input_path) + ".asm")

    # Open the output file
    with open(asm_file, 'w') as output:
        #Write the bootsrap code
        output.write("// Bootstrap Code\n")
        output.write(boostrap_code())
        call_index = 0
        # Process each .vm file
        for vm_file in vm_files:
            print(f"Processing {vm_file}...")
            with open(vm_file, 'r') as file:
                for line in file:
                    stripped_line = line.strip()
                    if stripped_line.startswith("//") or stripped_line == "":
                        continue
                    # Parse the command and write the assembly code
                    command_type, command_elements = parser(stripped_line)
                    code_writer(output, command_type, command_elements, stripped_line, call_index)
                    if command_type == "function" and command_elements[0] == "call":
                        call_index += 1

    print("Translation has been completed. Output written to:", asm_file)
 
def parser(command):
    elements = command.split()
    if elements[0] in ["push","pop"]:
        command_type =  "memory"
        return command_type, elements
    elif elements[0] in ["add","sub","neg","eg","gt","lt","and","or","not"]:
        command_type = "arithmetic"
        return command_type, elements
    elif elements[0] in ["label", "goto", "if-goto"]:
        command_type = "branching"
        return command_type, elements
    elif elements[0] in ["function", "call", "return"]:
        command_type = "function"
        return command_type, elements
    else:
        command_type = "invalid"
        return command_type, elements

def code_writer(output, command_type, elements, original_command,call_index):
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
    elif command_type == "branching":
        operation = elements[0]
        label = elements[1]
        if operation == "label":
            output.write(f"({label})\n")
        elif operation == "goto":
            output.write(goto_command(label))
        elif operation == "if-goto":
            output.write(if_goto_command(label))
    elif command_type == "function":
        operation = elements[0]
        if operation == "function":
            function_name = elements[1]
            n_vars = elements[2]
            output.write(function_function(function_name, n_vars))
        elif operation == "call":
            function_name = elements[1]
            n_args = elements[2]
            output.write(call_function(function_name, n_args, call_index))
        elif operation == "return":
            output.write(return_command())

    
def push_command(segment, index):
    if segment == "constant":
        return f"@{index}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
    
    elif segment in ["local", "argument", "this", "that"]:
        segment_map = {
            "local": "LCL",
            "argument": "ARG",
            "this": "THIS",
            "that": "THAT"
        }
        asm_segment = segment_map[segment]
        return (f"@{index}\nD=A\n@{asm_segment}\nA=D+M\nD=M\n"
                "@SP\nA=M\nM=D\n@SP\nM=M+1\n")

    elif segment == "pointer":
        if index == "0":
            return "@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        elif index == "1":
            return "@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
    
    elif segment == "temp":
        temp_address = 5 + int(index)
        return f"@{temp_address}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"

    return ""


def pop_command(segment, index):
    if segment in ["local", "argument", "this", "that"]:
        segment_map = {
            "local": "LCL",
            "argument": "ARG",
            "this": "THIS",
            "that": "THAT"
        }
        asm_segment = segment_map[segment]
        return (
            f"@{index}\nD=A\n@{asm_segment}\nD=D+M\n@R13\nM=D\n"  
            "@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n"                  
        )

    elif segment == "pointer":
        if index == "0":
            return "@SP\nAM=M-1\nD=M\n@THIS\nM=D\n"
        elif index == "1":
            return "@SP\nAM=M-1\nD=M\n@THAT\nM=D\n"

    elif segment == "temp":
        temp_address = 5 + int(index)
        return f"@SP\nAM=M-1\nD=M\n@{temp_address}\nM=D\n"

    return ""

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
comparison_count = 0  # Add this as a class-level variable or within your function's scope

def eq_command():
    global comparison_count
    comp_label = comparison_count
    comparison_count += 1
    return (f"@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nD=M-D\n"
            f"@TRUE{comp_label}\nD;JEQ\nD=0\n@FALSE{comp_label}\n0;JMP\n"
            f"(TRUE{comp_label})\nD=-1\n(FALSE{comp_label})\n"
            "@SP\nA=M\nM=D\n@SP\nM=M+1\n")

def gt_command():
    global comparison_count
    comp_label = comparison_count
    comparison_count += 1
    return (f"@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nD=M-D\n"
            f"@TRUE{comp_label}\nD;JGT\nD=0\n@FALSE{comp_label}\n0;JMP\n"
            f"(TRUE{comp_label})\nD=-1\n(FALSE{comp_label})\n"
            "@SP\nA=M\nM=D\n@SP\nM=M+1\n")

def lt_command():
    global comparison_count
    comp_label = comparison_count
    comparison_count += 1
    return (f"@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nD=M-D\n"
            f"@TRUE{comp_label}\nD;JLT\nD=0\n@FALSE{comp_label}\n0;JMP\n"
            f"(TRUE{comp_label})\nD=-1\n(FALSE{comp_label})\n"
            "@SP\nA=M\nM=D\n@SP\nM=M+1\n")


def return_command():
    return ("@LCL\nD=M\n@R13\nM=D\n@5\nA=D-A\nD=M\n"
            "@R14\nM=D\n@SP\nAM=M-1\nD=M\n@ARG\nA=M\nM=D\n"
            "@ARG\nD=M+1\n@SP\nM=D\n"
            "@R13\nAM=M-1\nD=M\n@THAT\nM=D\n"
            "@R13\nAM=M-1\nD=M\n@THIS\nM=D\n"
            "@R13\nAM=M-1\nD=M\n@ARG\nM=D\n"
            "@R13\nAM=M-1\nD=M\n@LCL\nM=D\n"
            "@R14\nA=M\n0;JMP\n")
def call_function(function_name, n_args, call_index):
    return_address = f"{function_name}$ret.{call_index}"
    return (f"@{return_address}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
            "@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
            "@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
            "@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
            "@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
            "@SP\nD=M\n@LCL\nM=D\n"
            f"@5\nD=D-A\n@{n_args}\nD=D-A\n@ARG\nM=D\n"
            f"@{function_name}\n0;JMP\n({return_address})\n")
def function_function(function_name,n_vars):
    assembly_code = f"({function_name})\n"
    for i in range(int(n_vars)):
        assembly_code += "@SP\nA=M\nM=0\n@SP\nM=M+1\n" 
    return assembly_code
def if_goto_command(label):
    return (f"@SP\nM=M-1\nA=M\n@{label}\nD;JNE\n")

def goto_command(label):
    return (f"@{label}\n0;JMP\n")

def boostrap_code():
 
    return (
        "@256\n"        
        "D=A\n"
        "@SP\n"
        "M=D\n"         
        f"{call_function('Sys.init', 0, 0)}"  
    )
#main process
if __name__ == "__main__":
    main()