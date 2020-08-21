"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.stackPointerIndex = 7

    def load(self, fileName):
        """Load a program into memory."""
        address = 0
        program = []

        try:
            with open(fileName) as file:
                for line in file:
                    split_lines = line.split('#')[0]
                    command = split_lines.strip()

                    if command == '':
                        continue
                    num = int(command, 2)
                    program.append(num)

        except FileNotFoundError:
            print(f'{fileName} was not found')

        for instruction in program:
            self.ram[address] = instruction
            address += 1

        # reserve 7th register for stack pointer
        self.reg[self.stackPointerIndex] = 0xF4

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        # Math operations
        ADD = 0b10100000

        HLT = 0b00000001
        LDI = 0b10000010
        PRN = 0b01000111
        MUL = 0b10100010
        PUSH = 0b01000101
        POP = 0b01000110
        CALL = 0b01010000
        RET = 0b00010001

        running = True

        while running:
            cmd = self.ram[self.pc]
            if cmd == HLT:
                running = False
            elif cmd == ADD:
                self.alu('ADD', self.ram_read(self.pc + 1),
                         self.ram_read(self.pc + 2))
                self.pc += 1 + (cmd >> 6)

            elif cmd == LDI:
                self.reg[self.ram_read(self.pc + 1)
                         ] = self.ram_read(self.pc + 2)
                self.pc += 1 + (cmd >> 6)  # should be 3

            elif cmd == PRN:
                print(self.reg[self.ram_read(self.pc + 1)])
                self.pc += 1 + (cmd >> 6)  # should be 2

            elif cmd == MUL:
                self.alu('MUL', self.ram_read(self.pc + 1),
                         self.ram_read(self.pc + 2))
                self.pc += 1 + (cmd >> 6)  # should be 3

            elif cmd == PUSH:
                # decrement the stack pointer by one
                self.reg[self.stackPointerIndex] -= 1

                # get the index of the register
                registerNumber = self.ram[self.pc + 1]

                # get the value stored on the given register
                value = self.reg[registerNumber]

                # store the given value in the memory stack
                self.ram[self.reg[self.stackPointerIndex]] = value

                self.pc += 1 + (cmd >> 6)  # should be 2

            elif cmd == POP:
                # get the value that stack pointer is currently pointing at
                value = self.ram[self.reg[self.stackPointerIndex]]

                # store the value to the given register
                self.reg[self.ram[self.pc + 1]] = value

                # increment the stack pointer
                self.reg[self.stackPointerIndex] += 1

                self.pc += 1 + (cmd >> 6)  # should be 2

            elif cmd == CALL:
                registerNumber = self.ram_read(self.pc + 1)
                subroutineAddress = self.reg[registerNumber]

                returnAddress = self.pc + 2

                self.reg[self.stackPointerIndex] -= 1
                self.ram[self.reg[self.stackPointerIndex]] = returnAddress
                self.pc = subroutineAddress

            elif cmd == RET:
                returnAddress = self.ram[self.reg[self.stackPointerIndex]]
                self.pc = returnAddress
                self.reg[self.stackPointerIndex] += 1

    def ram_read(self, MA):
        return self.ram[MA]

    def ram_write(self, MA, MD):
        self.ram[MA] = MD
