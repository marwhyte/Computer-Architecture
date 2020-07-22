"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8  # like variables you have at your disposal
        self.pc = 0  # where a computer is in its program sequence.
        self.fl = 0  # flag (for compare)
        self.reg[7] = 0xf4  # starting address

        self.func_dict = {
            1: self.HLT,
            130: self.LDI,
            71: self.PRN,
            162: self.MUL,  # 10100010
            69: self.PUSH,
            70: self.POP,
            80: self.CALL,
            17: self.RET,
            160: self.ADD,
            167: self.CMP,  # 10100111
            84: self.JMP,  # 01010100 4+16+64
            85: self.JEQ,  # 01010101 1+4+16+64
            86: self.JNE  # 01010110 2+4+16+64
        }

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self, file):
        """Load a program into memory."""
        with open(file) as f:
            for x in f:
                if x[0] != '#':
                    self.ram_write(self.pc, int(x[0:8], 2))
                    self.pc += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        # elif op == "SUB": etc
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
        self.pc = 0
        self.status = True
        while self.status == True:
            opA = self.ram_read(self.pc + 1)  # operation code
            opB = self.ram_read(self.pc + 2)
            ir = self.ram_read(self.pc)
            if ir not in self.func_dict:
                print(f"Code not valid {ir}")
                self.trace()
                self.status == False
                break
            self.func_dict[ir](opA, opB)

    def HLT(self, opA, opB):
        self.status = False

    def LDI(self, opA, opB):
        self.reg[opA] = opB
        self.pc += 3

    def PRN(self, opA, opB):
        print(self.reg[opA])
        self.pc += 2

    def MUL(self, opA, opB):
        self.alu('MUL', opA, opB)
        self.pc += 3

    def ADD(self, opA, opB):
        self.alu('ADD', opA, opB)
        self.pc += 3

    def PUSH(self, opA, opB):
        opA = self.reg[self.ram_read(self.pc + 1)]
        self.reg[7] -= 1  # stack pointer
        self.ram[self.reg[7]] = opA  # set to value we want to store
        self.pc += 2

    def POP(self, opA, opB):
        # store value
        self.reg[self.ram_read(self.pc + 1)] = self.ram_read(self.reg[7])
        self.reg[7] += 1  # stack pointer
        self.pc += 2

    def CALL(self, opA, opB):  # go to certain address but allows us to come back when subrout finish
        self.reg[7] -= 1  # pointer down
        self.ram_write(self.reg[7], self.pc + 2)
        self.pc = self.reg[self.ram_read(self.pc + 1)]

    def RET(self, opA, opB):  # returns back from subroutine
        self.pc = self.ram[self.reg[7]]
        self.reg[7] += 1

    def CMP(self, opA, opB):
        if self.reg[opA] < self.reg[opB]:
            self.fl = 3  # we'll use 3 for less then
            self.pc += 3
        elif self.reg[opA] > self.reg[opB]:
            self.fl = 2  # 2 for greater than
            self.pc += 3
        elif self.reg[opB] == self.reg[opB]:
            self.fl = 1  # 1 for equal
            self.pc += 3

    def JMP(self, opA, opB):  # go to address in regester
        self.pc = self.reg[self.ram_read(self.pc + 1)]

    def JEQ(self, opA, opB):  # When Equal FLag is set jump to correct register
        if self.fl == 1:
            self.pc = self.reg[self.ram_read(self.pc + 1)]
        else:
            self.pc += 2

    def JNE(self, opA, opB):  # Jump if not equal`
        if self.fl != 1:
            self.pc = self.reg[self.ram_read(self.pc + 1)]
        else:
            self.pc += 2
