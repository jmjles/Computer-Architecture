"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.pc = 0
        self.sp = 7
        self.reg = [0] * 8
        self.reg[self.sp] = 0xf4
        self.fl = [0] * 8

    LDI = 130
    MULT = 162
    PRN = 71
    PUSH = 69
    POP = 70
    CALL = 80
    RET = 17
    CMP = 167
    JMP = 84
    JEQ = 85
    JNE = 86
    HLT = 1
    RUN = True

    def load(self):
        """Load a program into memory."""
        # For now, we've just hardcoded a program:
        file = sys.argv[1]
        with open(file) as f:
            address = 0
            for line in f:
                line = line.split('#')
                try:
                    v = int(line[0], 2)
                except ValueError:
                    continue
                self.ram[address] = v
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MULT":
            return self.reg[reg_a] * self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl[-1] = 1
                self.fl[-2] = 0
                self.fl[-3] = 0
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl[-1] = 0
                self.fl[-2] = 1
                self.fl[-3] = 0
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl[-1] = 0
                self.fl[-2] = 0
                self.fl[-3] = 1
        else:
            raise Exception("Unsupported ALU operation")

    def ldi_op(self):
        pos = self.ram[self.pc+1]
        val = self.ram[self.pc+2]
        self.reg[pos] = val

    def reg_read(self):
        target = self.ram[self.pc+1]
        print(self.reg[target])

    def pop(self):
        reg_num = self.ram_read(self.pc + 1)
        self.reg[reg_num] = self.ram[self.reg[self.sp]]

        self.reg[self.sp] += 1

    def push(self):
        # decrement SP
        self.reg[self.sp] -= 1
        # Get the value we want to store from the register
        reg_num = self.ram_read(self.pc + 1)
        value = self.reg[reg_num]
        # Figure out where to store it
        top_of_stack_addr = self.reg[self.sp]
        # Store it
        self.ram[top_of_stack_addr] = value

    def call(self):
        return_addr = self.pc + 2  # Where we're going to RET to

        # Push on the stack
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = return_addr

        # Get the address to call
        reg_num = self.ram[self.pc + 1]
        subroutine_addr = self.reg[reg_num]

        # Call it
        self.pc = subroutine_addr

    def ram_read(self, i):
        return self.ram[i]

    def ram_write(self, val, pos):
        self.ram[pos] = val
        self.pc += 1

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

    def jmp(self):
        pos = self.ram[self.pc+1]
        self.pc = self.reg[pos]

    def jeq(self):
        if self.fl[-1] == 1:
            self.jmp()
        else:
            self.pc += 2

    def jne(self):
        if self.fl[-1] == 0:
            self.jmp()
        else:
            self.pc += 2

    def run(self):
        """Run the CPU."""
        while self.RUN:
            ir = self.ram_read(self.pc)
            if ir == self.HLT:
                self.RUN = False
                self.pc += 1
            elif ir == self.LDI:
                self.ldi_op()
                self.pc += 3

            elif ir == self.PRN:
                self.reg_read()
                self.pc += 2

            elif ir == self.MULT:
                num1 = self.ram[self.pc+1]
                num2 = self.ram[self.pc+2]
                self.reg[num1] = self.alu("MULT", num1, num2)
                self.pc += 3

            elif ir == self.CMP:
                num1 = self.ram[self.pc+1]
                num2 = self.ram[self.pc+2]
                self.alu("CMP", num1, num2)
                self.pc += 3

            elif ir == self.PUSH:
                self.push()
                self.pc += 2

            elif ir == self.POP:
                self.pop()
                self.pc += 2

            elif ir == self.CALL:
                self.call()

            elif ir == self.RET:
                pass

            elif ir == self.JEQ:
                self.jeq()
            elif ir == self.JNE:
                self.jne()
            elif ir == self.JMP:
                self.jmp()
            else:
                self.pc += 1
