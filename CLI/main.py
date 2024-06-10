import datetime
from typing import Dict
from tabulate import tabulate


ASSEMBLY_INPUT_FILE = 'assembly_input.txt'
MACHINE_OUTPUT_FILE = 'machine_output.txt'
MACHINE_INPUT_FILE = 'machine_input.txt'
ASSEMBLY_OUTPUT_FILE = 'assembly_output.txt'
LOG_FILE = 'register_log.txt'


REGISTER_INITIAL_VALUES = {
    'AR': 0,
    'PC': 0,
    'DR': 0,
    'AC': 0,
    'IR': 0,
}


assembly_to_machine = {
    "AND": "8",
    "ADD": "9",
    "LDA": "A",
    "STA": "B",
    "BUN": "C",
    "BSA": "D",
    "ISZ": "E",
    "CLA": "7800",
    "CLE": "7400",
    "CMA": "7200",
    "CME": "7100",
    "CIR": "7080",
    "CIL": "7040",
    "INC": "7020",
    "SPA": "7010",
    "SNA": "7008",
    "SZA": "7004",
    "SZE": "7002",
    "HLT": "7001"
}
machine_to_assembly = {v: k for k, v in assembly_to_machine.items()}


registers = REGISTER_INITIAL_VALUES.copy()

def initialize_files() -> None:
    """Initialize the input and output files."""
    for file in [ASSEMBLY_INPUT_FILE, MACHINE_INPUT_FILE, MACHINE_OUTPUT_FILE, ASSEMBLY_OUTPUT_FILE]:
        with open(file, 'w') as f:
            f.write("")

def initialize_log_file() -> None:
    """Initialize the log file."""
    with open(LOG_FILE, 'w') as log_file:
        log_file.write("")

def log_register_operation(operation: str, register: str, value: int) -> None:
    """Log register operations with timestamps."""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    memory_state = {k: v for k, v in registers.items()}
    log_entry = {
        "Timestamp": timestamp,
        "Operation": operation,
        "Register": register,
        "Value": value,
        "Registers": memory_state
    }
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(f"{log_entry}\n")

def update_register(register: str, value: int, memory_address: str = None) -> None:
    """Update a register and log the operation."""
    registers[register] = value
    log_register_operation("UPDATE", register, value)

def convert_assembly_to_machine() -> None:
    """Convert assembly code to machine code."""
    assembly_code = read_file_lines(ASSEMBLY_INPUT_FILE, "Assembly Input")
    if assembly_code is None:
        return

    machine_code = []
    for line in assembly_code:
        parts = line.strip().split()
        if len(parts) == 1:  
            instruction = parts[0]
            if instruction in assembly_to_machine:
                machine_code.append(f"{assembly_to_machine[instruction]}\n")
                update_register('IR', int(assembly_to_machine[instruction], 16)) 
            else:
                print_in_table(f"Error: Invalid instruction {instruction}")
                return
        else:  
            instruction, operand = parts
            if instruction in assembly_to_machine:
                opcode = assembly_to_machine[instruction]
                machine_code.append(f"{opcode}{operand}\n")
                update_register('IR', int(f"{opcode}{operand}", 16)) 
                update_register('AR', int(operand, 16))
            else:
                print_in_table(f"Error: Invalid instruction {instruction}")
                return

        registers['PC'] += 1
        log_register_operation("INCREMENT", 'PC', registers['PC'])

    write_file_lines(MACHINE_OUTPUT_FILE, machine_code, "Machine Output")
    print_in_table("Assembly code has been converted to machine language.")

def convert_machine_to_assembly():
    try:
        with open(MACHINE_INPUT_FILE, 'r') as mach_file:
            machine_code = mach_file.readlines()
    except FileNotFoundError:
        print_in_table(f"Error: {MACHINE_INPUT_FILE} not found.")
        return
    except Exception as e:
        print_in_table(f"Error reading {MACHINE_INPUT_FILE}: {e}")
        return
    
    if not machine_code:
        print_in_table("Error: Machine input file is empty.")
        return
    
    assembly_code = []
    for line in machine_code:
        line = line.strip()
        if len(line) == 4 and line in machine_to_assembly:
            instruction = machine_to_assembly[line]
            assembly_code.append(f"{instruction}\n")
            update_register('IR', int(line, 16))
        else:
            opcode = line[0]
            operand = line[1:]
            instruction = [key for key, value in assembly_to_machine.items() if value == opcode]
            if instruction:
                assembly_code.append(f"{instruction[0]} {operand}\n")
                update_register('IR', int(f"{opcode}{operand}", 16))
                update_register('AR', int(operand, 16))
            else:
                print_in_table(f"Error: Invalid machine code {line}")
                return
        
        registers['PC'] += 1
        log_register_operation("INCREMENT", 'PC', registers['PC'])
    
    try:
        with open(ASSEMBLY_OUTPUT_FILE, 'w') as asm_file:
            asm_file.writelines(assembly_code)
    except Exception as e:
        print_in_table(f"Error writing {ASSEMBLY_OUTPUT_FILE}: {e}")
        return
    
    print_in_table("Machine code has been converted to assembly language.")


def read_file_lines(file_path: str, file_description: str) -> list:
    """Read lines from a file and return them."""
    try:
        with open(file_path, 'r') as file:
            contents = file.readlines()
        if not contents:
            print_in_table(f"{file_description} file is empty.")
            return None
        return contents
    except FileNotFoundError:
        print_in_table(f"Error: {file_path} not found.")
        return None
    except Exception as e:
        print_in_table(f"Error reading {file_path}: {e}")
        return None

def write_file_lines(file_path: str, lines: list, file_description: str) -> None:
    """Write lines to a file."""
    try:
        with open(file_path, 'w') as file:
            file.writelines(lines)
    except Exception as e:
        print_in_table(f"Error writing {file_path}: {e}")

def view_register_state() -> None:
    """Display the current state of the registers."""
    table = [[k, v] for k, v in registers.items()]
    print_in_table(tabulate(table, headers=["Register", "Value"]))

def display_log_file() -> None:
    """Display the contents of the log file."""
    log_contents = read_file_lines(LOG_FILE, "Log")
    if log_contents is None:
        return

    print_in_table("Log File Contents:")
    for line in log_contents:
        print(line.strip())

def display_file_contents(file_path: str, file_description: str) -> None:
    """Display the contents of a specified file."""
    contents = read_file_lines(file_path, file_description)
    if contents is None:
        return

    print_in_table(f"{file_description} File Contents:")
    for line in contents:
        print(line.strip())

def add_code_to_file(file_path: str, file_description: str) -> None:
    """Add code to a specified file."""
    print(f"Enter {file_description.lower()} code (terminate with an empty line):")
    with open(file_path, 'w') as file:
        while True:
            code = input()
            if not code:
                break
            file.write(code + "\n")
    print_in_table(f"{file_description} code has been added.")

def print_in_table(message: str) -> None:
    """Print a message in a formatted table."""
    print("\n" + tabulate([[message]], tablefmt="grid") + "\n")

def print_welcome_message() -> None:
    """Print a welcome message at the start of the program."""
    welcome_message = [
        ["Welcome to the Mano CLI Assembler Project"],
        ["Supervisor: Mr. Mohsen Farhadi"],
        ["Course: Computer Architecture"],
        ["Student: Yasin Rezvani"],
        ["Date: Spring 2024"],
        ["Shahrood University of Technology"]
    ]
    print(tabulate(welcome_message, tablefmt="fancy_grid", stralign="center"))

def main_menu() -> None:
    """Display the main menu and handle user input."""
    initialize_files()
    initialize_log_file()
    print_welcome_message()
    menu_options = [
        "Convert Assembly to Machine Language",
        "Convert Machine Language to Assembly",
        "View Register State",
        "Display Log File",
        "Display Assembly Input File",
        "Display Assembly Output File",
        "Display Machine Input File",
        "Display Machine Output File",
        "Add Assembly Code",
        "Add Machine Code",
        "Exit"
    ]
    while True:
        print(tabulate(enumerate(menu_options, 1), tablefmt="fancy_grid", stralign="center"))
        choice = input("Select an option: ").strip()
        
        if choice == '1':
            convert_assembly_to_machine()
        elif choice == '2':
            convert_machine_to_assembly()
        elif choice == '3':
            view_register_state()
        elif choice == '4':
            display_log_file()
            print('\n')
        elif choice == '5':
            display_file_contents(ASSEMBLY_INPUT_FILE, "Assembly Input")
            print('\n')
        elif choice == '6':
            display_file_contents(ASSEMBLY_OUTPUT_FILE, "Assembly Output")
            print('\n')
        elif choice == '7':
            display_file_contents(MACHINE_INPUT_FILE, "Machine Input")
            print('\n')
        elif choice == '8':
            display_file_contents(MACHINE_OUTPUT_FILE, "Machine Output")
            print('\n')
        elif choice == '9':
            add_code_to_file(ASSEMBLY_INPUT_FILE, "Assembly")
        elif choice == '10':
            add_code_to_file(MACHINE_INPUT_FILE, "Machine")
        elif choice == '11' or choice == '0':
            print_in_table("Exiting the program. Good luck, Goodbye!")
            break
        else:
            print_in_table("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()

