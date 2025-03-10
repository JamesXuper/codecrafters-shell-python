import sys
import shutil

def main():
    BUILTIN_COMMANDS = ["echo", "exit", "type"]

    # Uncomment this block to pass the first stage
    sys.stdout.write("$ ")

    # Wait for user input
    command = input()
    argv = command.split()

    if command == 'exit 0':
        exit(0)

    elif command.startswith('echo'):
        print(" ".join(argv[1:]))

    elif command.startswith('type'):
        if argv[1] in BUILTIN_COMMANDS:
            print(f"{argv[1]} is a shell builtin")
        elif path := shutil.which(argv[1]):
            print(f"{argv[1]} is {path}")
        else:
            print(f"{argv[1]} not found")

    else:
        print(f"{command}: command not found")
    main()

if __name__ == "__main__":
    main()
