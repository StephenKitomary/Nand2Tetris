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
    output.write("// {original_command}\n")

    if command_type =="memory":
        operation, segment, index = elements[0], elements[1], elements[2]

§   §1``