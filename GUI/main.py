import datetime
import os
from tkinter import *
from tkinter import messagebox, scrolledtext, simpledialog
from tabulate import tabulate

ASSEMBLY_INPUT_FILE = "assembly_input.txt"
MACHINE_OUTPUT_FILE = "machine_output.txt"
MACHINE_INPUT_FILE = "machine_input.txt"
ASSEMBLY_OUTPUT_FILE = "assembly_output.txt"
LOG_FILE = "register_log.txt"

registers = {
    "AR": 0,
    "PC": 0,
    "DR": 0,
    "AC": 0,
    "IR": 0,
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
    "HLT": "7001",
}

machine_to_assembly = {v: k for k, v in assembly_to_machine.items()}


def initialize_files():
    for file in [
        ASSEMBLY_INPUT_FILE,
        MACHINE_INPUT_FILE,
        MACHINE_OUTPUT_FILE,
        ASSEMBLY_OUTPUT_FILE,
        LOG_FILE,
    ]:
        with open(file, "w") as f:
            f.write("")


def log_register_operation(operation, register, value):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    memory_state = {k: v for k, v in registers.items()}
    log_entry = {
        "Timestamp": timestamp,
        "Operation": operation,
        "Register": register,
        "Value": value,
        "Registers": memory_state,
    }
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{log_entry}\n")


def update_register(register, value):
    registers[register] = value
    log_register_operation("UPDATE", register, value)


def convert_assembly_to_machine():
    try:
        with open(ASSEMBLY_INPUT_FILE, "r") as asm_file:
            assembly_code = asm_file.readlines()
    except FileNotFoundError:
        display_message(f"Error: {ASSEMBLY_INPUT_FILE} not found.")
        return
    except Exception as e:
        display_message(f"Error reading {ASSEMBLY_INPUT_FILE}: {e}")
        return

    if not assembly_code:
        display_message("Error: Assembly input file is empty.")
        return

    machine_code = []
    for line in assembly_code:
        parts = line.strip().split()
        if len(parts) == 1:
            instruction = parts[0]
            if instruction in assembly_to_machine:
                machine_code.append(f"{assembly_to_machine[instruction]}\n")
                update_register("IR", int(assembly_to_machine[instruction], 16))
            else:
                display_message(f"Error: Invalid instruction {instruction}")
                return
        else:
            instruction, operand = parts
            if instruction in assembly_to_machine:
                opcode = assembly_to_machine[instruction]
                machine_code.append(f"{opcode}{operand}\n")
                update_register("IR", int(f"{opcode}{operand}", 16))
                update_register("AR", int(operand, 16))
            else:
                display_message(f"Error: Invalid instruction {instruction}")
                return

        registers["PC"] += 1
        log_register_operation("INCREMENT", "PC", registers["PC"])

    try:
        with open(MACHINE_OUTPUT_FILE, "w") as mach_file:
            mach_file.writelines(machine_code)
    except Exception as e:
        display_message(f"Error writing {MACHINE_OUTPUT_FILE}: {e}")
        return

    display_message("Assembly code has been converted to machine language.")


def convert_machine_to_assembly():
    try:
        with open(MACHINE_INPUT_FILE, "r") as mach_file:
            machine_code = mach_file.readlines()
    except FileNotFoundError:
        display_message(f"Error: {MACHINE_INPUT_FILE} not found.")
        return
    except Exception as e:
        display_message(f"Error reading {MACHINE_INPUT_FILE}: {e}")
        return

    if not machine_code:
        display_message("Error: Machine input file is empty.")
        return

    assembly_code = []
    for line in machine_code:
        line = line.strip()
        if len(line) == 4 and line in machine_to_assembly:
            instruction = machine_to_assembly[line]
            assembly_code.append(f"{instruction}\n")
            update_register("IR", int(line, 16))
        else:
            opcode = line[0]
            operand = line[1:]
            instruction = [
                key for key, value in assembly_to_machine.items() if value == opcode
            ]
            if instruction:
                assembly_code.append(f"{instruction[0]} {operand}\n")
                update_register("IR", int(f"{opcode}{operand}", 16))
                update_register("AR", int(operand, 16))
            else:
                display_message(f"Error: Invalid machine code {line}")
                return

        registers["PC"] += 1
        log_register_operation("INCREMENT", "PC", registers["PC"])

    try:
        with open(ASSEMBLY_OUTPUT_FILE, "w") as asm_file:
            asm_file.writelines(assembly_code)
    except Exception as e:
        display_message(f"Error writing {ASSEMBLY_OUTPUT_FILE}: {e}")
        return

    display_message("Machine code has been converted to assembly language.")


def view_register_state():
    table = [[k, v] for k, v in registers.items()]
    display_message(tabulate(table, headers=["Register", "Value"]))


def display_log_file():
    try:
        with open(LOG_FILE, "r") as log_file:
            log_contents = log_file.readlines()
        if not log_contents:
            display_message("Log file is empty.")
            return
        display_message("Log File Contents:\n" + "".join(log_contents))
    except FileNotFoundError:
        display_message(f"Error: {LOG_FILE} not found.")
    except Exception as e:
        display_message(f"Error reading {LOG_FILE}: {e}")


def display_file_contents(file_path, file_description):
    try:
        with open(file_path, "r") as file:
            contents = file.readlines()
        if not contents:
            display_message(f"{file_description} file is empty.")
            return
        display_message(f"{file_description} File Contents:\n" + "".join(contents))
    except FileNotFoundError:
        display_message(f"Error: {file_path} not found.")
    except Exception as e:
        display_message(f"Error reading {file_path}: {e}")


def add_assembly_code():
    input_window("Enter Assembly Code", "Enter assembly code:", ASSEMBLY_INPUT_FILE)


def add_machine_code():
    input_window("Enter Machine Code", "Enter machine code:", MACHINE_INPUT_FILE)


def input_window(title, prompt, file_path):
    def save_code():
        code = text_area.get("1.0", END).strip()
        if code:
            with open(file_path, "w") as file:
                file.write(code)
            display_message(f"{title.split()[1]} code has been added.")
            window.destroy()
        else:
            messagebox.showerror("Error", "No code entered.")

    window = Toplevel()
    window.title(title)
    window.geometry("800x600")

    Label(window, text=prompt, font=("Arial", 12)).pack(pady=10)
    text_area = scrolledtext.ScrolledText(
        window, wrap=WORD, width=70, height=25, font=("Arial", 12)
    )
    text_area.pack(padx=10, pady=10)

    Button(
        window,
        text="Save",
        command=save_code,
        font=("Arial", 12),
        bg="#4CAF50",
        fg="white",
    ).pack(pady=10)


def display_message(message):
    text_area.delete("1.0", END)
    text_area.insert(END, message)


class ManoAssemblerApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("Maurice Mano GUI Assembler")
        self.state("zoomed")
        initialize_files()
        self.create_widgets()

    def create_widgets(self):
        self.create_menu()
        self.create_welcome_message()
        self.create_main_buttons()
        self.create_text_area()

    def create_menu(self):
        menubar = Menu(self)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Clear Files", command=initialize_files)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.config(menu=menubar)

    def create_welcome_message(self):
        welcome_message = [
            ["Welcome to the Maurice Mano GUI Assembler Project"],
            ["Supervisor: Mr. Mohsen Farhadi"],
            ["Course: Computer Architecture"],
            ["Student: Yasin Rezvani"],
            ["Date: Spring 2024"],
            ["Shahrood University of Technology"],
        ]
        message = "\n".join([f"{row[0]}" for row in welcome_message])
        Label(
            self, text=message, font=("Helvetica", 13, "bold"), justify=CENTER, pady=8
        ).pack()
    def create_main_buttons(self):
        frame = Frame(self, bg="#2E2E2E")
        frame.pack(pady=10)

        buttons = [
            ("Convert Assembly to Machine Language", convert_assembly_to_machine),
            ("Convert Machine Language to Assembly", convert_machine_to_assembly),
            ("View Register State", view_register_state),
            ("Display Log File", display_log_file),
            ("Display Assembly Input File", lambda: display_file_contents(ASSEMBLY_INPUT_FILE, "Assembly Input")),
            ("Display Assembly Output File", lambda: display_file_contents(ASSEMBLY_OUTPUT_FILE, "Assembly Output")),
            ("Display Machine Input File", lambda: display_file_contents(MACHINE_INPUT_FILE, "Machine Input")),
            ("Display Machine Output File", lambda: display_file_contents(MACHINE_OUTPUT_FILE, "Machine Output")),
            ("Add Assembly Code", add_assembly_code),
            ("Add Machine Code", add_machine_code)
        ]

        for i, (text, command) in enumerate(buttons):
            Button(frame, text=text, command=command, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white", width=40, height=2, relief=RAISED, bd=5).grid(row=i//2, column=i%2, padx=10, pady=10)

    def create_text_area(self):
        global text_area
        text_area = scrolledtext.ScrolledText(self, wrap=WORD, width=150, height=20, font=("Helvetica", 12), bg="#1E1E1E", fg="white", insertbackground="white")
        text_area.pack(padx=10, pady=10)


if __name__ == "__main__":
    app = ManoAssemblerApp()
    app.mainloop()
