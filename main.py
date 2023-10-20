import numpy as np
import sys
import re


class YB_60:
    memory = []
    program_counter = 0
    registers = []

    def __init__(self):
        self.memory = np.zeros(1048576)
        self.registers = np.zeros(32)

    def parse_input(self, user_input):
        if user_input.isalnum() and not ('r' in user_input) and not ('t' in user_input) and not ('info' == user_input):
            return 0
        if '.' in user_input:
            return 1
        if ':' in user_input:
            return 2
        if 'r' in user_input:
            return 3
        if 't' in user_input:
            return 4
        if 'info' == user_input:
            return 5
        return -1

    def read_in_file(self, file_data):
        file = open(file_data)
        data_string = file.read()
        data_string = data_string.split(':')
        offset = 0
        checksum = 0;

        for i in range(1, len(data_string)):
            data = re.findall('..', data_string[i])
            if data[3] == '02':
                offset = int(data[4] + data[5], 16) * 16
                continue
            count = 0

            for j in data[4:4+int(data[0], 16)]:
                if int(data[1]+data[2], 16) + count > self.memory.size:
                    print("Error: Memory is full, not all data was loaded from file.")
                    break

                self.memory[int(data[1]+data[2], 16) + count + offset] = int(j, 16)
                count = count + 1

            sum = 0
            for j in data:
                byte = int(j, 16)
                if byte > 127:
                    byte = -128 + (byte & 0x7F)
                sum = sum + byte
                sum = sum & 0x7F

            checksum = int(data[len(data) - 1], 16)
            if sum != 0:
                print("Format input error. ", sys.argv[1])
                exit(-1)

        file.close()
        return

    def display_mem_address(self, straddress):
        try:
            address = int(straddress, 16)
        except:
            print('Error, not a hexedecimal number.')
            return

        # Printing out the data in hex at the given address if it is a valid address.
        if self.memory.size > address >= 0:
            a = format(int(self.memory[address]), 'x')
            print(a.upper().zfill(2))
        else:
            print("Invalid address.")
        return

    def display_range_mem_address(self, addresses):
        nums = addresses.split('.')

        try:
            start_add = int(nums[0], 16)
            end_add = int(nums[1], 16)
        except:
            print('Addresses provided are not in hexadecimal.')
            return

        # Checking if the range is valid.
        if start_add >= end_add:
            print("Invalid Memory Access, memory locations are not sequential.")
            return

        # Checking if each memory address is valid.
        if not (self.memory.size > start_add >= 0) or not (self.memory.size > end_add >= 0):
            print("Invalid Memory Address.")
            return

        # Printing out all the data in the provided memory range.
        i = start_add
        print(format(i, 'x').upper(), end='    ')
        while i < end_add:
            a = format(int(self.memory[i]), 'x')
            print(a.upper().zfill(2), end=' ')
            i = i + 1
            if (i - start_add) % 8 == 0:
                print()
                if (end_add - i) != 0:
                    print(format(i, 'x').upper(), end='    ')

        # Printing a new line if the range was a multiple of 8.
        if (i - start_add) % 8 != 0:
            print()
        return

    def edit_mem_address(self, input):
        strs = input.split(':')
        data = strs[1].split(' ')

        try:
            j = int(strs[0], 16)
        except:
            print('Error: Address provided is not a hexadecimal number.')
            return

        for i in data[1:]:
            self.memory[j] = int(i, 16)
            j = j + 1

        return

    def run_program(self, address):
        split = address.split('r')
        try:
            self.program_counter = int(split[0], 16)
        except:
            print('Error: Address provided is not a hexadecimal number.')
            return
        print('  PC        ' + 'OPC    ' + 'INST    ' + 'rd    ' + 'rs1    ' + 'rs2/imm')
        print(format(self.program_counter, 'x').upper().zfill(5))
        return

    def display_info(self):
        count = 0
        for i in self.registers:
            print(f"{'x' + str(count) : >3}" + ' ' + str(int(i)).zfill(8))
            count += 1
        return

    def disassemble(self, data):
        split = data.split('t')
        try:
            address = int(split[0], 16)
        except:
            print('Error: Address provided is not a hexadecimal number.')
            return

        pc = address
        instruction = bytearray.fromhex(
            format(int(self.memory[pc + 3]), 'x') + format(int(self.memory[pc + 2]), 'x') +
            format(int(self.memory[pc + 1]), 'x') + format(int(self.memory[pc]), 'x'))

        instruction = (format(int(self.memory[pc + 3]), "08b") + format(int(self.memory[pc + 2]), "08b") +
                       format(int(self.memory[pc + 1]), "08b") + format(int(self.memory[pc]), "08b"))

        while format(int(instruction, 2), 'x') != '100073':
            pc += 4
            opcode, rd, funct3, rs1, rs2, funct7, imm = self.parse_instruction(instruction)
            name = lookup_instruction(opcode, funct3, funct7)
            print('\t' + name + ' x' + str(int(rd, 2)) + ', x' + str(int(rs1, 2)) + ', x' + str(int(rs2, 2)))
            instruction = (format(int(self.memory[pc + 3]), "08b") + format(int(self.memory[pc + 2]), "08b") +
                           format(int(self.memory[pc + 1]), "08b") + format(int(self.memory[pc]), "08b"))
            if format(int(instruction, 2), 'x') == '100073':
                print('ebreak')
        return

# 300: B3 02 5A 01 33 03 5B 01 B3 89 62 40 73 00 10 00

    def parse_instruction(self, data):
        op = int(data[25:30], 2)
        opcode = data[25:32]
        imm = np.zeros(32)
        formats = ''
        rd, funct3, rs1, rs2, funct7 = bytearray(0), bytearray(0), bytearray(0), bytearray(0), bytearray(0)

        if op == 4 or op == 12:     # R Format.
            formats = 'R'
            funct7 = data[0:7]
        elif op == 0 or op == 25:   # I Format.
            formats = 'I'
            imm[0:11] = data[0:12]
        elif op == 8:               # S Format.
            formats = 'S'
            imm[5:11] = data[0:7]
            imm[0:4] = data[20:25]
        elif op == 24:              # SB Format.
            formats = 'SB'
            imm[4:(1 | 11)] = data[20:25]
            imm[(12 | 10):5] = data[0:7]
        elif op == 5 or op == 13:   # U Format.
            formats = 'U'
            imm[12:32] = data[0:20]
        elif op == 27:              # UJ Format.
            formats = 'UJ'
            imm[(20 | 10):(1 | 11 | 19):12] = data[0:20]

        if formats == 'R' or 'I' or 'U' or 'UJ':
            rd = data[20:25]

        if formats == 'R' or 'I' or 'S' or 'SB':
            funct3 = data[17:20]
            rs1 = data[12:17]

        if formats == 'R' or 'S' or 'SB':
            rs2 = data[7:12]

        return opcode, rd, funct3, rs1, rs2, funct7, imm


def lookup_instruction(op, fun3, fun7):
    opcode = format(int(op, 2), 'x')
    funct3 = format(int(fun3, 2), 'x')
    funct7 = format(int(fun7, 2), 'x')

    r_instr = ['add', 'sll', 'slt', 'sltu', 'xor', 'srl', 'or', 'and']

    if opcode == '33':
        if funct3 == '0' and funct7 == '20':
            return 'sub'
        if funct3 == '5' and funct7 == '20':
            return 'sra'
        return r_instr[int(funct3, 16)]


if __name__ == '__main__':

    YB = YB_60()

    if len(sys.argv) == 2:
        YB.read_in_file(sys.argv[1])

    strInput = str(input('>'))
    while strInput != 'exit' and strInput != '\04':
        match YB.parse_input(strInput):
            case 0:
                YB.display_mem_address(strInput)
            case 1:
                YB.display_range_mem_address(strInput)
            case 2:
                YB.edit_mem_address(strInput)
            case 3:
                YB.run_program(strInput)
            case 4:
                YB.disassemble(strInput)
            case 5:
                YB.display_info()
            case default:
                print('Not a valid command, try again.', strInput)

        strInput = str(input('>'))