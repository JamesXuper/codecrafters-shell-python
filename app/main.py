import sys
import os
import shutil
import subprocess
import shlex

BUILTIN_COMMANDS = ["echo", "exit", "type", "pwd", "cd"]

def input_exit(argv):
    exit(int(argv[0]))

def input_echo(user_input, output_file=None):
    # Use shlex.split to properly handle quoted arguments
    parts = shlex.split(user_input[5:])  # Remove "echo " prefix
    output = " ".join(parts)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(output + "\n")
    else:
        print(output)

def input_type(argv, output_file=None):
    if argv[0] in BUILTIN_COMMANDS:
        result = f"{argv[0]} is a shell builtin"
    elif path := shutil.which(argv[0]):
        result = f"{argv[0]} is {path}"
    else:
        result = f"{argv[0]} not found"
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(result + "\n")
    else:
        print(result)

def input_pwd(output_file=None):
    cwd = os.getcwd()
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(cwd + "\n")
    else:
        print(cwd)

def input_cd(argv):
    if os.path.exists(argv[0]):
        os.chdir(argv[0])
    elif argv[0] == "~":
        os.chdir(os.path.expanduser("~"))
    else:
        print(f"cd: {argv[0]}: No such file or directory")

def parse_redirection(command_parts):
    """Parse command parts to identify redirection operators and files."""
    cmd_parts = []
    output_file = None
    
    i = 0
    while i < len(command_parts):
        part = command_parts[i]
        
        # Check for redirection operators
        if part == ">" or part == "1>":
            if i + 1 < len(command_parts):
                output_file = command_parts[i + 1]
                i += 2  # Skip the operator and the filename
                continue
        
        cmd_parts.append(part)
        i += 1
    
    return cmd_parts, output_file

def main():
    #REPL set up
    while True:
        sys.stdout.write("$ ")
        user_input = input()
        
        # Handle empty input
        if not user_input.strip():
            continue
        
        # First split the input using shlex to handle quotes correctly
        try:
            parts = shlex.split(user_input)
        except ValueError as e:
            print(f"Syntax error: {e}")
            continue
        
        if not parts:
            continue
        
        # Parse for redirection
        cmd_parts, output_file = parse_redirection(parts)
        
        if not cmd_parts:
            continue
        
        cmd = cmd_parts[0]
        argv = cmd_parts[1:]
        
        # Modified original input without redirection for echo command
        modified_input = user_input
        if output_file:
            # This is a simple way to strip the redirection part from the input
            # It's not perfect but works for basic cases
            modified_input = user_input.split(" >")[0].split(" 1>")[0]
        
        if cmd == "exit":
            input_exit(argv)
        elif cmd == "echo":
            input_echo(modified_input, output_file)
        elif cmd == "type":
            input_type(argv, output_file)
        elif cmd == "pwd":
            input_pwd(output_file)
        elif cmd == "cd":
            input_cd(argv)  # cd doesn't support redirection
        else:
            if shutil.which(cmd):  # Check if the command exists in PATH
                try:
                    if output_file:
                        # Redirect stdout to the specified file
                        with open(output_file, 'w') as f:
                            process = subprocess.run(cmd_parts, stdout=f, stderr=subprocess.PIPE, text=True)
                            # Print stderr to console as it's not redirected
                            if process.stderr:
                                print(process.stderr, end='')
                    else:
                        process = subprocess.run(cmd_parts)
                except Exception as e:
                    print(f"Error executing {cmd}: {e}")
            else:
                print(f"{cmd}: command not found")

if __name__ == "__main__":
    main()