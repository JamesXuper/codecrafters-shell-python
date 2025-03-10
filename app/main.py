import sys


def main():
    # Uncomment this block to pass the first stage
    sys.stdout.write("$ ")

    # Wait for user input
    user_input = input()
    user_input_parts = user_input.split()

    if user_input == 'exit 0':
        exit(0)
        
    elif user_input.startswith('echo'):
        print(f"{user_input_parts[1:]}")

    else:
        print(f"{user_input}: command not found")
    main()

if __name__ == "__main__":
    main()
