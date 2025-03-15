import sys
import os
import shutil
import subprocess

BUILTIN_COMMANDS = ["echo", "exit", "type", "pwd", "cd"]

def input_exit(argv):
    exit(int(argv[0]))

def input_echo(argv):
    result = []
    i = 0
    
    while i < len(argv):
        arg = argv[i]
        
        # Check if this argument starts with a single quote
        if arg.startswith("'") and not arg.endswith("'"):
            # Start of a quoted section
            quoted_text = [arg[1:]]  # Remove the opening quote
            
            # Keep adding arguments until we find the closing quote
            j = i + 1
            while j < len(argv) and not argv[j].endswith("'"):
                quoted_text.append(argv[j])
                j += 1
                
            # If we found the closing quote
            if j < len(argv):
                quoted_text.append(argv[j][:-1])  # Remove the closing quote
                result.append(" ".join(quoted_text))
                i = j  # Skip to after the quoted section
            else:
                # No closing quote found, treat as normal
                result.append(arg)
        
        # If the argument is entirely enclosed in single quotes
        elif arg.startswith("'") and arg.endswith("'") and len(arg) > 1:
            # Remove the quotes and add as is
            result.append(arg[1:-1])
        
        else:
            # Regular argument
            result.append(arg)
            
        i += 1
    
    sys.stdout.write(" ".join(result) + "\n")

def input_type(argv):
    if argv[0] in BUILTIN_COMMANDS:
        print(f"{argv[0]} is a shell builtin")
    elif path := shutil.which(argv[0]):
        print(f"{argv[0]} is {path}")
    else:
        print(f"{argv[0]} not found")

def input_pwd():
    cwd = os.getcwd()
    print(cwd)

def input_cd(argv):
    if os.path.exists(argv[0]):
        os.chdir(argv[0])
    elif argv[0] == "~":
        os.chdir(os.path.expanduser("~"))
    else:
        print(f"cd: {argv[0]}: No such file or directory")

def main():

    #REPL set up
    while True:
        sys.stdout.write("$ ")
        user_input = input()
        cmd, *argv = user_input.split() #splits the input string into an array separated by white space

        if cmd == "exit":
            input_exit(argv)
        elif cmd == "echo":
            input_echo(argv)
        elif cmd == "type": #checking whether we know the 'type' of the builtin function
            input_type(argv)
        elif cmd == "pwd":
            input_pwd()
        elif cmd == "cd":
            input_cd(argv)
        else:
            if shutil.which(cmd):               #Check if the command exists in PATH
                try:
                    process = subprocess.run([cmd] + argv)
                    # No need to print the output as subprocess.run will print 
                    # stdout and stderr by default
                except Exception as e:
                    print(f"Error executing {cmd}: {e}")
            else:
                print(f"{cmd}: command not found")

if __name__ == "__main__":
    main()