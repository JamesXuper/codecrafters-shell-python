import sys
import os
import shutil
import subprocess
import shlex

BUILTIN_COMMANDS = ["echo", "exit", "type", "pwd", "cd"]

def input_exit(argv):
    exit(int(argv[0]))

def input_echo(user_input, stdout_file=None, stderr_file=None):
    # Use shlex.split to properly handle quoted arguments
    parts = shlex.split(user_input[5:])  # Remove "echo " prefix
    output = " ".join(parts)
    
    if stdout_file:
        with open(stdout_file, 'w') as f:
            f.write(output + "\n")
    else:
        print(output)

def input_type(argv, stdout_file=None, stderr_file=None):
    if argv[0] in BUILTIN_COMMANDS:
        result = f"{argv[0]} is a shell builtin"
    elif path := shutil.which(argv[0]):
        result = f"{argv[0]} is {path}"
    else:
        error = f"{argv[0]} not found"
        if stderr_file:
            with open(stderr_file, 'w') as f:
                f.write(error + "\n")
        else:
            print(error, file=sys.stderr)
        return
    
    if stdout_file:
        with open(stdout_file, 'w') as f:
            f.write(result + "\n")
    else:
        print(result)

def input_pwd(stdout_file=None, stderr_file=None):
    cwd = os.getcwd()
    
    if stdout_file:
        with open(stdout_file, 'w') as f:
            f.write(cwd + "\n")
    else:
        print(cwd)

def input_cd(argv, stderr_file=None):
    if os.path.exists(argv[0]):
        os.chdir(argv[0])
    elif argv[0] == "~":
        os.chdir(os.path.expanduser("~"))
    else:
        error = f"cd: {argv[0]}: No such file or directory"
        if stderr_file:
            with open(stderr_file, 'w') as f:
                f.write(error + "\n")
        else:
            print(error, file=sys.stderr)

def parse_redirection(command_parts):
    """Parse command parts to identify redirection operators and files."""
    cmd_parts = []
    stdout_file = None
    stderr_file = None
    
    i = 0
    while i < len(command_parts):
        part = command_parts[i]
        
        # Check for redirection operators
        if part == ">" or part == "1>":
            if i + 1 < len(command_parts):
                stdout_file = command_parts[i + 1]
                i += 2  # Skip the operator and the filename
                continue
        elif part == "2>":
            if i + 1 < len(command_parts):
                stderr_file = command_parts[i + 1]
                i += 2  # Skip the operator and the filename
                continue
        
        cmd_parts.append(part)
        i += 1
    
    return cmd_parts, stdout_file, stderr_file

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
        cmd_parts, stdout_file, stderr_file = parse_redirection(parts)
        
        if not cmd_parts:
            continue
        
        cmd = cmd_parts[0]
        argv = cmd_parts[1:]
        
        # Modified original input without redirection for echo command
        modified_input = user_input
        if stdout_file or stderr_file:
            # This is a simple way to strip the redirection part from the input
            # It's not perfect but works for basic cases
            if ">" in user_input:
                modified_input = user_input.split(" >")[0]
            if "1>" in user_input:
                modified_input = user_input.split(" 1>")[0]
            if "2>" in user_input:
                modified_input = user_input.split(" 2>")[0]
        
        if cmd == "exit":
            input_exit(argv)
        elif cmd == "echo":
            input_echo(modified_input, stdout_file, stderr_file)
        elif cmd == "type":
            input_type(argv, stdout_file, stderr_file)
        elif cmd == "pwd":
            input_pwd(stdout_file, stderr_file)
        elif cmd == "cd":
            input_cd(argv, stderr_file)
        else:
            if shutil.which(cmd):  # Check if the command exists in PATH
                try:
                    # Configure stdout and stderr redirection
                    stdout = subprocess.PIPE if stdout_file else None
                    stderr = subprocess.PIPE if stderr_file else None
                    
                    # Run the command with appropriate redirection
                    process = subprocess.run(cmd_parts, stdout=stdout, stderr=stderr, text=True)
                    
                    # Handle stdout redirection
                    if stdout_file and process.stdout is not None:
                        with open(stdout_file, 'w') as f:
                            f.write(process.stdout)
                    elif process.stdout is not None:
                        print(process.stdout, end='')
                    
                    # Handle stderr redirection
                    if stderr_file and process.stderr is not None:
                        with open(stderr_file, 'w') as f:
                            f.write(process.stderr)
                    elif process.stderr is not None:
                        print(process.stderr, end='', file=sys.stderr)
                        
                except Exception as e:
                    error_message = f"Error executing {cmd}: {e}"
                    if stderr_file:
                        with open(stderr_file, 'w') as f:
                            f.write(error_message + "\n")
                    else:
                        print(error_message, file=sys.stderr)
            else:
                error_message = f"{cmd}: command not found"
                if stderr_file:
                    with open(stderr_file, 'w') as f:
                        f.write(error_message + "\n")
                else:
                    print(error_message, file=sys.stderr)

if __name__ == "__main__":
    main()