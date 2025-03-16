import sys
import os
import shutil
import subprocess
import shlex

BUILTIN_COMMANDS = ["echo", "exit", "type", "pwd", "cd"]

def input_exit(argv):
    exit(int(argv[0]))

def input_echo(user_input):
    # Use shlex.split to properly handle quoted arguments
    parts = shlex.split(user_input[5:])  # Remove "echo " prefix
    print(" ".join(parts))

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
        
        # Handle empty input
        if not user_input.strip():
            continue
            
        # Use shlex.split for command parsing to properly handle quotes
        try:
            parts = shlex.split(user_input)
            cmd = parts[0]
            argv = parts[1:]
        except IndexError:
            # Handle empty input that might pass the strip check
            continue
        except ValueError as e:
            print(f"Syntax error: {e}")
            continue

        if cmd == "exit":
            input_exit(argv)
        elif cmd == "echo":
            input_echo(user_input)  # Pass the full input for echo
        elif cmd == "type":
            input_type(argv)
        elif cmd == "pwd":
            input_pwd()
        elif cmd == "cd":
            input_cd(argv)
        else:
            if shutil.which(cmd):  # Check if the command exists in PATH
                try:
                    # Use the parts already split by shlex for subprocess
                    process = subprocess.run(parts)
                except Exception as e:
                    print(f"Error executing {cmd}: {e}")
            else:
                print(f"{cmd}: command not found")

if __name__ == "__main__":
    main()