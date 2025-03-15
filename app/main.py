import sys
import shutil

# def main():

#     BUILTIN_COMMANDS = ["echo", "exit", "type"]

#     # Uncomment this block to pass the first stage
#     sys.stdout.write("$ ")

#     # Wait for user input
#     command = input()
#     argv = command.split()

#     if command == "exit 0":
#         exit(0)
#     elif command.startswith("echo"):
#         print(" ".join(argv[1:]))
#     elif command.startswith("type"):
#         if argv[1] in BUILTIN_COMMANDS:
#             print(f"{argv[1]} is a shell builtin")
#         elif path := shutil.which(argv[1]):
#             print(f"{argv[1]} is {path}")
#         else:
#             print(f"{argv[1]} not found")
#     else:
#         print(f"{command}: command not found")
    
#     main()

def main():
    BUILTIN_COMMANDS = ["echo", "exit", "type"]

    
    #prints the $ once after command begins
    sys.stdout.write("$ ")

    #REPL set up
    while True:
        user_input = input()
        argv = user_input.split() #splits the input string into an array separated by white space

        if argv[0] == "exit 0":
            exit(0)

        elif argv[0] == "echo":
            print(" ".join(argv[1:]))

        elif argv[0] == "type": #checking whether we know the 'type' of the builtin function
            if argv[1] in BUILTIN_COMMANDS:
                print(f"{argv[1]} is a shell builtin")
            elif path := shutil.which(argv[1]):
                print(f"{argv[1]} is {path}")
            else:
                print(f"{argv[1]} not found")

        else:
            print(f"{argv[0]}: command not found")

if __name__ == "__main__":
    main()