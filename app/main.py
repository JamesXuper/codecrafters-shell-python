import sys
import os
import shutil
import subprocess

BUILTIN_COMMANDS = ["echo", "exit", "type", "pwd", "cd"]

def input_exit(argv):
    exit(int(argv[0]))

def input_echo(argv):
    sys.stdout.write(" ".join(argv) + "\n")

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