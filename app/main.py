import sys
import os
import shutil
import subprocess
import shlex
import readline
import time

BUILTIN_COMMANDS = ["echo", "exit", "type", "pwd", "cd"]

def input_exit(argv):
    exit(int(argv[0]) if argv else 0)

def input_echo(user_input, stdout_file=None, stderr_file=None, append_stdout=False, append_stderr=False):
    # Use shlex.split to properly handle quoted arguments
    parts = shlex.split(user_input[5:])  # Remove "echo " prefix
    output = " ".join(parts)
    
    # Always create the stderr file if specified, even if empty
    if stderr_file:
        mode = 'a' if append_stderr else 'w'
        open(stderr_file, mode).close()
    
    if stdout_file:
        mode = 'a' if append_stdout else 'w'
        with open(stdout_file, mode) as f:
            f.write(output + "\n")
    else:
        print(output)

def input_type(argv, stdout_file=None, stderr_file=None, append_stdout=False, append_stderr=False):
    # Always create the stderr file if specified, even if empty
    if stderr_file:
        mode = 'a' if append_stderr else 'w'
        open(stderr_file, mode).close()
        
    if argv[0] in BUILTIN_COMMANDS:
        result = f"{argv[0]} is a shell builtin"
    elif path := shutil.which(argv[0]):
        result = f"{argv[0]} is {path}"
    else:
        error = f"{argv[0]} not found"
        if stderr_file:
            mode = 'a' if append_stderr else 'w'
            with open(stderr_file, mode) as f:
                f.write(error + "\n")
        else:
            print(error, file=sys.stderr)
        return
    
    if stdout_file:
        mode = 'a' if append_stdout else 'w'
        with open(stdout_file, mode) as f:
            f.write(result + "\n")
    else:
        print(result)

def input_pwd(stdout_file=None, stderr_file=None, append_stdout=False, append_stderr=False):
    # Always create the stderr file if specified, even if empty
    if stderr_file:
        mode = 'a' if append_stderr else 'w'
        open(stderr_file, mode).close()
        
    cwd = os.getcwd()
    
    if stdout_file:
        mode = 'a' if append_stdout else 'w'
        with open(stdout_file, mode) as f:
            f.write(cwd + "\n")
    else:
        print(cwd)

def input_cd(argv, stderr_file=None, append_stderr=False):
    # Always create the stderr file if specified, even if empty
    if stderr_file:
        mode = 'a' if append_stderr else 'w'
        open(stderr_file, mode).close()
        
    if not argv:
        os.chdir(os.path.expanduser("~"))
    elif os.path.exists(argv[0]):
        os.chdir(argv[0])
    elif argv[0] == "~":
        os.chdir(os.path.expanduser("~"))
    else:
        error = f"cd: {argv[0]}: No such file or directory"
        if stderr_file:
            mode = 'a' if append_stderr else 'w'
            with open(stderr_file, mode) as f:
                f.write(error + "\n")
        else:
            print(error, file=sys.stderr)

def parse_redirection(command_parts):
    """Parse command parts to identify redirection operators and files."""
    cmd_parts = []
    stdout_file = None
    stderr_file = None
    append_stdout = False
    append_stderr = False
    
    i = 0
    while i < len(command_parts):
        part = command_parts[i]
        
        # Check for redirection operators
        if part == ">" or part == "1>":
            if i + 1 < len(command_parts):
                stdout_file = command_parts[i + 1]
                append_stdout = False
                i += 2  # Skip the operator and the filename
                continue
        elif part == ">>" or part == "1>>":
            if i + 1 < len(command_parts):
                stdout_file = command_parts[i + 1]
                append_stdout = True
                i += 2  # Skip the operator and the filename
                continue
        elif part == "2>":
            if i + 1 < len(command_parts):
                stderr_file = command_parts[i + 1]
                append_stderr = False
                i += 2  # Skip the operator and the filename
                continue
        elif part == "2>>":
            if i + 1 < len(command_parts):
                stderr_file = command_parts[i + 1]
                append_stderr = True
                i += 2  # Skip the operator and the filename
                continue
        
        cmd_parts.append(part)
        i += 1
    
    return cmd_parts, stdout_file, stderr_file, append_stdout, append_stderr

def ensure_directory_exists(filepath):
    """Ensure the directory for a file exists"""
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def get_executables_in_path():
    """Get all executable files in the PATH"""
    executables = set()
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)
    
    for path_dir in path_dirs:
        if os.path.isdir(path_dir):
            for item in os.listdir(path_dir):
                full_path = os.path.join(path_dir, item)
                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    executables.add(item)
    
    return executables

def my_completer(text, state):
    """Simple completer function that always adds a space after a match"""
    matches = []
    
    # Add matching builtin commands
    for cmd in BUILTIN_COMMANDS:
        if cmd.startswith(text):
            matches.append(cmd)
    
    # Add matching executables in PATH
    for cmd in get_executables_in_path():
        if cmd.startswith(text):
            matches.append(cmd)
    
    matches.sort()
    
    # Check if we're in multiple matches situation
    if len(matches) > 1 and state == 0:
        # Ring the bell for first tab with multiple matches
        sys.stdout.write("\a")
        sys.stdout.flush()
        
        # Find common prefix if any
        if matches:
            common = matches[0]
            for match in matches[1:]:
                i = 0
                while i < len(common) and i < len(match) and common[i] == match[i]:
                    i += 1
                common = common[:i]
            
            if len(common) > len(text):
                return common
    
    # For multiple tabs on multiple matches
    if len(matches) > 1 and state == 1:  # Second tab press
        print()  # Add a newline
        print("  ".join(matches))  # Print all matches
        print(f"$ {text}", end="")  # Reprint the prompt
        return None
    
    # Add a space after single match
    if state < len(matches):
        # This is what matters most - we add the space right here
        return matches[state] + " "
    else:
        return None

def main():
    try:
        # Set up the tab completion
        readline.parse_and_bind("tab: complete")
        readline.set_completer(my_completer)
    except Exception as e:
        print(f"Warning: Tab completion setup failed: {e}", file=sys.stderr)
    
    # REPL set up
    while True:
        try:
            sys.stdout.write("$ ")
            sys.stdout.flush()
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
            cmd_parts, stdout_file, stderr_file, append_stdout, append_stderr = parse_redirection(parts)
            
            # Make sure parent directories exist
            if stdout_file:
                ensure_directory_exists(stdout_file)
            if stderr_file:
                ensure_directory_exists(stderr_file)
                # Always create the stderr file, even if empty
                mode = 'a' if append_stderr else 'w'
                open(stderr_file, mode).close()
            
            if not cmd_parts:
                continue
            
            cmd = cmd_parts[0]
            argv = cmd_parts[1:]
            
            # Modified original input without redirection for echo command
            modified_input = user_input
            if stdout_file or stderr_file:
                # This is a simple way to strip the redirection part from the input
                # It's not perfect but works for basic cases
                modified_input = user_input
                for op in [" >", " 1>", " 2>", " >>", " 1>>", " 2>>"]:
                    if op in modified_input:
                        modified_input = modified_input.split(op)[0]
            
            if cmd == "exit":
                input_exit(argv)
            elif cmd == "echo":
                input_echo(modified_input, stdout_file, stderr_file, append_stdout, append_stderr)
            elif cmd == "type":
                input_type(argv, stdout_file, stderr_file, append_stdout, append_stderr)
            elif cmd == "pwd":
                input_pwd(stdout_file, stderr_file, append_stdout, append_stderr)
            elif cmd == "cd":
                input_cd(argv, stderr_file, append_stderr)
            else:
                if shutil.which(cmd):  # Check if the command exists in PATH
                    try:
                        # Configure stdout and stderr redirection
                        stdout_dest = subprocess.PIPE if stdout_file else None
                        stderr_dest = subprocess.PIPE if stderr_file else None
                        
                        # Run the command with appropriate redirection
                        process = subprocess.run(cmd_parts, stdout=stdout_dest, stderr=stderr_dest, text=True)
                        
                        # Handle stdout redirection
                        if stdout_file and process.stdout is not None:
                            mode = 'a' if append_stdout else 'w'
                            with open(stdout_file, mode) as f:
                                f.write(process.stdout)
                        elif process.stdout is not None:
                            print(process.stdout, end='')
                        
                        # Handle stderr redirection
                        if stderr_file and process.stderr is not None:
                            mode = 'a' if append_stderr else 'w'
                            with open(stderr_file, mode) as f:
                                f.write(process.stderr)
                        elif process.stderr is not None:
                            print(process.stderr, end='', file=sys.stderr)
                            
                    except Exception as e:
                        error_message = f"Error executing {cmd}: {e}"
                        if stderr_file:
                            mode = 'a' if append_stderr else 'w'
                            with open(stderr_file, mode) as f:
                                f.write(error_message + "\n")
                        else:
                            print(error_message, file=sys.stderr)
                else:
                    error_message = f"{cmd}: command not found"
                    if stderr_file:
                        mode = 'a' if append_stderr else 'w'
                        with open(stderr_file, mode) as f:
                            f.write(error_message + "\n")
                    else:
                        print(error_message, file=sys.stderr)
        
        except EOFError:
            print()  # Add a newline
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()