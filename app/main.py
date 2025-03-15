import sys
import shutil
import subprocess

BUILTIN_COMMANDS = ["echo", "exit", "type"]

def input_exit(argv):
    exit(int(argv[0]))

def input_echo(argv):
    sys.stdout.write(" ".join(argv) + "\n")

def input_type(cmd, argv):
    if cmd in BUILTIN_COMMANDS:
        print(f"{argv[0]} is a shell builtin")
    elif path := shutil.which(argv[0]):
        print(f"{argv[0]} is {path}")
    else:
        print(f"{argv[0]} not found")

def main():
    #prints the $ once after command begins
    sys.stdout.write("$ ")

    #REPL set up
    while True:
        user_input = input()
        cmd, *argv = user_input.split() #splits the input string into an array separated by white space

        if cmd == "exit":
            input_exit(argv)
        elif cmd == "echo":
            input_echo(argv)
        elif cmd == "type": #checking whether we know the 'type' of the builtin function
            input_type(cmd, argv)
        else:
            # Check if the command exists in PATH
            executable_path = shutil.which(cmd)
            if executable_path:
                # Execute the command with its arguments
                try:
                    process = subprocess.run(cmd + argv)
                    # No need to print the output as subprocess.run will print 
                    # stdout and stderr by default
                except Exception as e:
                    print(f"Error executing {cmd}: {e}")
            else:
                print(f"{cmd}: command not found")

if __name__ == "__main__":
    main()