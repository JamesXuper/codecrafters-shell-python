import sys


def main():
    builtin_commands = ["echo", "exit", "type"]

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
        if argv[1] in builtin_commands:
            print(f"{argv[1]} is a shell builtin")
        else:
            print(f"{argv[1]} not found")

    else:
        print(f"{command}: command not found")
    main()

if __name__ == "__main__":
    main()
