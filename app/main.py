import sys


def main():
    # Uncomment this block to pass the first stage
    sys.stdout.write("$ ")

    # Wait for user input
    command = input()
    argv = command.split()

    if command == 'exit 0':
        exit(0)

    elif command.startswith('echo'):
        print(" ".join(argv[1:]))

    else:
        print(f"{command}: command not found")
    main()

if __name__ == "__main__":
    main()
