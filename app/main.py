import sys
import os
import shutil
import subprocess
import shlex
import readline
import time

BUILTIN_COMMANDS = ["echo", "exit", "type", "pwd", "cd"]

# Track the last tab completion time to detect double-tabs
last_tab_time = 0
last_tab_text = None
last_tab_matches = []

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

def get_matches(text):
    """Get all commands (builtins and executables) that match the given prefix"""
    matches = []
    
    # Add matching builtin commands
    matches.extend([cmd for cmd in BUILTIN_COMMANDS if cmd.startswith(text)])
    
    # Add matching executables in PATH
    executables = get_executables_in_path()
    matches.extend([cmd for cmd in executables if cmd.startswith(text)])
    
    return sorted(matches)

def complete(text, state):
    """Tab completion function for readline."""
    global last_tab_time, last_tab_text, last_tab_matches
    
    # Check if this is a second tab press for the same text within a short time window
    current_time = time.time()
    double_tab = (text == last_tab_text and 
                   current_time - last_tab_time < 0.5 and 
                   last_tab_matches and len(last_tab_matches) > 1)
    
    if state == 0:
        # First state call: get all matches
        matches = get_matches(text)
        
        # Store for potential double-tab
        last_tab_text = text
        last_tab_time = current_time
        last_tab_matches = matches
        
        if len(matches) == 1:
            # Single match
            completion = matches[0]
            
            # Directly manipulate the line buffer for single matches to ensure space
            line_buffer = readline.get_line_buffer()
            cursor_pos = readline.get_endidx()
            
            # Replace the text with the completed command
            new_buffer = line_buffer[:cursor_pos - len(text)] + completion + " " + line_buffer[cursor_pos:]
            
            # Set the new line buffer
            readline.insert_text('')  # Clear first
            readline.insert_text(new_buffer[len(readline.get_line_buffer()):])
            
            return None  # Return None to indicate we've handled it
        elif len(matches) > 1:
            # Multiple matches
            if double_tab:
                # Second tab press: print all matches
                print()
                print("  ".join(matches))
                print(f"$ {text}", end="")
                # Return none so readline doesn't modify the line
                return None
            else:
                # First tab press: ring the bell
                sys.stdout.write("\a")
                sys.stdout.flush()
                # Find common prefix if any
                if matches:
                    common_prefix = matches[0]
                    for match in matches[1:]:
                        i = 0
                        while i < len(common_prefix) and i < len(match) and common_prefix[i] == match[i]:
                            i += 1
                        common_prefix = common_prefix[:i]
                    
                    if common_prefix and len(common_prefix) > len(text):
                        return common_prefix
            
            # No completion yet, but store the matches for potential double-tab
            complete.matches = matches
            return None
        else:
            # No matches
            complete.matches = []
            return None
    else:
        # Subsequent state calls after multiple matches on second tab
        if double_tab:
            # Already printed the list, don't complete anything
            return None
        
        # Return the matches in order by state
        try:
            if state < len(complete.matches):
                return complete.matches[state]
            return None
        except (IndexError, AttributeError):
            return None

# Initialize the attributes
complete.matches = []

def setup_custom_completer():
    """Set up a custom readline completer function that wraps our completer
    to ensure spaces are added correctly to tab completions."""
    
    old_completer = readline.get_completer()
    
    def custom_complete_wrapper(text, state):
        result = old_completer(text, state)
        if result is not None and state == 0 and len(get_matches(text)) == 1:
            # For a single match, make sure a space is appended
            # This may never be reached due to our direct buffer manipulation,
            # but is here as a fallback
            line_buffer = readline.get_line_buffer()
            cursor_pos = readline.get_endidx()
            if cursor_pos == len(line_buffer):  # If cursor at end
                if not result.endswith(" "):
                    result += " "
        return result
    
    return custom_complete_wrapper

def main():
    # Set up readline for autocomplete
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete)
    
    # REPL set up
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()  # Make sure the prompt is displayed
        
        try:
            user_input = input()
        except EOFError:
            print()  # Add a newline
            break
        
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

if __name__ == "__main__":
    main()