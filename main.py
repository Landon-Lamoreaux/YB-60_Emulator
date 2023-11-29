import numpy as np
import sys
import re
from bitstring import BitArray


class YB_60:
    memory = []
    registers = []
    pc = 0

    def __init__(self):
        self.memory = np.zeros(1048576, dtype=int)
        self.registers = np.zeros(32, dtype=int)

    def read_in_file(self, file):
        data_string = file.read()
        data_string = data_string.split(':')
        offset = 0

        for i in range(1, len(data_string)):
            data = re.findall('..', data_string[i])
            if data[3] == '02':
                offset = int(data[4] + data[5], 16) * 16
                continue
            sum = count = 0

            for j in data[4:4+int(data[0], 16)]:
                if int(data[1]+data[2], 16) + count > self.memory.size:
                    print("Error: Memory is full, not all data was loaded from file.")
                    break
                self.memory[int(data[1]+data[2], 16) + count + offset] = int(j, 16)
                count += 1

            for j in data:
                byte = int(j, 16)
                if byte > 127:
                    byte = -128 + (byte & 0x7F)
                sum = (sum + byte) & 0x7F

            if sum != 0:
                print("Format input error. ", sys.argv[1])
                exit(-1)

        file.close()
        return

    def display_mem_address(self, address):
        # Printing out the data in hex at the given address if it is a valid address.
        if self.memory.size > address >= 0:
            print(format(int(self.memory[address]), 'x').upper().zfill(2))
        else:
            print("Invalid address.")
        return

    def display_range_mem_address(self, addresses):
        nums = addresses.split('.')

        i = start_add = int(nums[0], 16)
        end_add = int(nums[1], 16)

        # Checking if each memory address is valid.
        if not (self.memory.size > start_add >= 0) or not (self.memory.size > end_add >= 0) or (start_add >= end_add):
            print("Invalid Memory Range.")
            return

        # Printing out all the data in the provided memory range.
        print(format(i, 'x').upper(), end='    ')
        while i < end_add:
            print(format(int(self.memory[i]), 'x').upper().zfill(2), end=' ')
            i += 1
            if (i - start_add) % 8 == 0:
                print()
                if (end_add - i) != 0:
                    print(format(i, 'x').upper(), end='    ')

        # Printing a new line if the range was a multiple of 8.
        print('\n' if (i - start_add) % 8 != 0 else '', end='')
        return

    def edit_mem_address(self, input):
        strs = input.split(':')
        data = strs[1].split(' ')
        j = int(strs[0], 16)

        # Updating the memory from the starting location with the data given.
        for i in data[1:]:
            self.memory[j] = int(i, 16)
            j += 1
        return

    def run_program(self, address):
        split = address.split('r')
        self.pc = int(split[0], 16)
        self.registers = np.zeros(32, dtype=int)
        instruction = '0'

        # Printing out the header.
        print(format('PC', '>5') + format('OPC', '>9') + format('INST', '>7') + '  rd  ' + '  rs1  ' + 'rs2/imm')

        # Reading through and printing out all the instructions from the given address to the terminator.
        while format(int(instruction, 2), 'x') != '100073':
            # Grabbing the instruction from memory.
            instruction = (format(int(self.memory[self.pc + 3]), "08b") + format(int(self.memory[self.pc + 2]), "08b") +
                           format(int(self.memory[self.pc + 1]), "08b") + format(int(self.memory[self.pc]), "08b"))

            # Printing out the program counter and the instruction in hexadecimal.
            print(format(self.pc, 'x').upper().zfill(5) + format(format(int(instruction, 2), 'x').upper().zfill(8), '>9'), end='')

            # Printing out 'EBREAK' if that is the next instruction.
            if format(int(instruction, 2), 'x') == '100073':
                print(' EBREAK')
                continue

            # Parsing the instruction and determining the name of the instruction.
            opcode, rd, funct3, rs1, rs2, funct7, imm, instr_format = self.parse_instruction(instruction)
            name = lookup_instruction(opcode, funct3, funct7, imm)

            # Running the instruction.
            self.run_line(name, imm, rd, rs1, rs2)

            # Printing out the name then the rd value if there is a rd in the instruction.
            print(format(name.upper(), '>7') + (format(str(rd), '>6') if rd != '0' else '      '), end='')

            # Printing out the rs1 value if there is a rs1 in the instruction.
            print(format(str(rs1), '>6') if rs1 != '0' else '      ', end='')

            # Printing out the rs2 and or immediate register.
            print((' ' + format(str(rs2), '<5') if rs2 != '0' else '') + ' ' + format(imm, 'b').zfill(5))
            self.pc += 4  # Updating the program counter.
        return

    def display_info(self):
        # Printing out the contents of all 32 registers.
        for i in range(0, 32):
            print(f"{'x' + str(i) : >3}" + ' ' + format(self.registers[i] & 0xFFFFFFFF, 'x').upper().zfill(8))
        return

    def disassemble(self, data):
        split = data.split('t')
        pc = int(split[0], 16)  # Setting the program counter
        self.registers = np.zeros(32, dtype=int)
        instruction = '0'

        while format(int(instruction, 2), 'x') != '100073':

            # Grabbing the next instruction from memory.
            instruction = (format(int(self.memory[pc + 3]), "08b") + format(int(self.memory[pc + 2]), "08b") +
                           format(int(self.memory[pc + 1]), "08b") + format(int(self.memory[pc]), "08b"))

            # Printing out the termination statement if the instruction is the terminator.
            if format(int(instruction, 2), 'x') == '100073':
                print('ebreak')
                continue

            # Parsing the instruction and determining the instructions name.
            opcode, rd, funct3, rs1, rs2, funct7, imm, instr_format = self.parse_instruction(instruction)
            name = lookup_instruction(opcode, funct3, funct7, imm)

            # Printing out the instruction and all the following values.
            print_instruction(opcode, name, str(int(rd, 2)), str(int(rs1, 2)), str(int(rs2, 2)), imm, instr_format, int(instruction, 2))

            # Running the instruction.
            self.run_line(name, sign_imm(imm, instr_format), rd, rs1, rs2)

            pc += 4
        return


    def parse_instruction(self, data):
        # Setting up our variables.
        op = int(data[25:32], 2)
        opcode = data[25:32]
        imm = 0
        rd, funct3, rs1, rs2, funct7, formats = '0', '0', '0', '0', '0', ''
        instr = BitArray(bin=data).int

        # Parsing the instruction into its parts and determining what type it is.
        if op == 51:     # R Format.
            formats = 'R'
            funct7 = data[0:7]
        elif op == 3 or op == 15 or op == 19 or op == 103 or op == 115:   # I Format.
            formats = 'I'
            # imm = copy_vals(imm, data[0:12], 0, 1)
            imm = (instr & int("FFF00000", 16)) >> 20  # Bit [11:0]
        elif op == 35:               # S Format.
            formats = 'S'
            # imm = copy_vals(imm, data[0:7], 11, -1)
            # imm = copy_vals(imm, data[20:25], 4, -1)
            imm = (instr & int("F80", 16)) >> 7  # Bit [4:0]
            imm += (instr & int("FE000000", 16)) >> 20  # Bit [11:5]
        elif op == 99:              # SB Format.
            formats = 'SB'
            # imm = copy_vals(imm, data[20:24], 1, 1)
            # imm[11], imm[12] = data[24], data[0]
            # imm = copy_vals(imm, data[1:7], 10, -1)
            imm = (instr & int("F00", 16)) >> 7  # Bit [4:1]
            imm += (instr & int("7E000000", 16)) >> 20  # Bit [10:5]
            imm += (instr & int("80", 16)) << 4  # Bit [11]
            imm += (instr & int("80000000", 16)) >> 19  # Bit [12]
        elif op == 23 or op == 55:   # U Format.
            formats = 'U'
            # imm = copy_vals(imm, data[0:20], 12, 1)
            imm = (instr & int("FFFFF000", 16)) >> 12  # Bit [31:12]
        elif op == 111:              # UJ Format.
            formats = 'UJ'
            # imm[20], imm[11] = int(data[0]), int(data[11])
            # imm = copy_vals(imm, data[1:11], 1, 1)
            # imm = copy_vals(imm, data[12:20], 12, 1)
            imm = (instr & int("7FE00000", 16)) >> 20  # Bit [10:1]
            imm += (instr & int("100000", 16)) >> 9  # Bit [11]
            imm += (instr & int("FF000", 16))  # Bit [19:12]
            imm += (instr & int("80000000", 16)) >> 11  # Bit [20]

        # Splitting up the instruction into its parts for these instruction formats.
        if formats == 'R' or formats == 'I' or formats == 'U' or formats == 'UJ':
            rd = data[20:25]
        if formats == 'R' or formats == 'I' or formats == 'S' or formats == 'SB':
            funct3 = data[17:20]
            rs1 = data[12:17]
        if formats == 'R' or formats == 'S' or formats == 'SB':
            rs2 = data[7:12]

        # Returning the instruction split into its different components.
        return opcode, rd, funct3, rs1, rs2, funct7, imm, formats


    def step_thru(self, strInput):
        split = strInput.split('s')
        self.pc = int(split[0], 16)
        self.registers = np.zeros(32, dtype=int)
        instruction = '0'

        while format(int(instruction, 2), 'x') != '100073':

            user_input = '0'

            # Grabbing the next instruction from memory.
            instruction = (format(int(self.memory[self.pc + 3]), "08b") + format(int(self.memory[self.pc + 2]), "08b") +
                           format(int(self.memory[self.pc + 1]), "08b") + format(int(self.memory[self.pc]), "08b"))

            while user_input != 's' and format(int(instruction, 2), 'x') != '100073':
                user_input = str(input('(s, i, q):> '))
                if user_input == 'i':
                    self.display_info()
                elif user_input == 'q':
                    return

            # Printing out the termination statement if the instruction is the terminator.
            if format(int(instruction, 2), 'x') == '100073':
                print('ebreak')
                continue

            # Parsing the instruction and determining the instructions name.
            opcode, rd, funct3, rs1, rs2, funct7, imm, instr_format = self.parse_instruction(instruction)
            name = lookup_instruction(opcode, funct3, funct7, imm)

            # Printing out the instruction and all the following values.
            print_instruction(opcode, name, str(int(rd, 2)), str(int(rs1, 2)), str(int(rs2, 2)), imm, instr_format, int(instruction, 2))
            self.run_line(name, sign_imm(imm, instr_format), rd, rs1, rs2)
            self.pc += 4



    def run_line(self, name, imm, rd, rs1, rs2):
        urd, urs1, urs2 = BitArray(bin=rd).uint, BitArray(bin=rs1).uint, BitArray(bin=rs2).uint
        rd, rs1, rs2 = int(rd, 2), int(rs1, 2), int(rs2, 2)
        imm = int(imm)

        match name:
            case 'add':
                self.registers[rd] = self.registers[rs1] + self.registers[rs2]
            case 'addi':
                self.registers[rd] = self.registers[rs1] + imm
            case 'sub':
                self.registers[rd] = self.registers[rs1] - self.registers[rs2]
            case 'mul':
                self.registers[rd] = self.registers[rs1] * self.registers[rs2]
            case 'mulh':
                self.registers[rd] = (self.registers[rs1] * self.registers[rs2]) & 0xFFFFFFFFFFFFFFFF0000000000000000
            case 'mulhsu' | 'mulhu':
                self.registers[rd] = ((self.registers[rs1] & 0xFFFFFFFF) * (self.registers[rs2] & 0xFFFFFFFF)) & 0xFFFFFFFFFFFFFFFF0000000000000000
            case 'div':
                self.registers[rd] = self.registers[rs1] / self.registers[rs2]
            case 'divu':
                self.registers[rd] = (self.registers[rs1] & 0xFFFFFFFF) / (self.registers[rs2] & 0xFFFFFFFF)
            case 'rem':
                self.registers[rd] = self.registers[rs1] % self.registers[rs2]
            case 'remu':
                self.registers[rd] = (self.registers[rs1] & 0xFFFFFFFF) % (self.registers[rs2] & 0xFFFFFFFF)
            case 'and':
                self.registers[rd] = self.registers[rs1] & self.registers[rs2]
            case 'andi':
                self.registers[rd] = self.registers[rs1] & imm
            case 'or':
                self.registers[rd] = self.registers[rs1] | self.registers[rs2]
            case 'ori':
                self.registers[rd] = self.registers[rs1] | imm
            case 'xor':
                self.registers[rd] = self.registers[rs1] ^ self.registers[rs2]
            case 'xori':
                reg = self.registers[rs1]
                self.registers[rd] = reg ^ imm
            case 'beq':
                if self.registers[rs1] == self.registers[rs2]:
                    self.pc += imm >> 1
            case 'bge':
                if self.registers[rs1] >= self.registers[rs2]:
                    self.pc += imm >> 1
            case 'bgeu':
                if (self.registers[rs1] & 0xFFFFFFFF) >= (self.registers[rs2] & 0xFFFFFFFF):
                    self.pc += imm >> 1
            case 'blt':
                if self.registers[rs1] < self.registers[rs2]:
                    self.pc += imm >> 1
            case 'bltu':
                if (self.registers[rs1] & 0xFFFFFFFF) < (self.registers[rs2] & 0xFFFFFFFF):
                    self.pc += imm >> 1
            case 'bne':
                if self.registers[rs1] != self.registers[rs2]:
                    self.pc += imm >> 1
            case 'jal':
                self.registers[rd] = self.pc + 4
                self.pc = self.pc + imm >> 1
            case 'jalr':
                self.registers[rd] = self.pc + 4
                self.pc = self.registers[rs1] + imm
            case 'lb':
                self.registers[rd] = self.memory[int(self.registers[rs1] + imm)]
            case 'lbu':
                loc = int(self.registers[rs1] + imm)
                self.registers[rd] = self.memory[loc] & 0xFFFFFFFF
            case 'lh':
                loc = int(self.registers[rs1] + imm)
                self.registers[rd] = (self.memory[loc + 1] << 8) + self.memory[loc]
            case 'lhu':
                loc = int(self.registers[rs1] + imm)
                self.registers[rd] = (self.memory[loc + 1] << 8) + self.memory[loc] & 0xFFFFFFFF
            case 'lw':
                loc = int(self.registers[rs1] + imm)
                self.registers[rd] = (self.memory[loc + 3] << 24) + (self.memory[loc + 2] << 16) + (self.memory[loc + 1] << 8) + self.memory[loc]
            case 'slli':
                val = imm
                self.registers[rd] = (self.registers[rs1] << val)
            case 'sll':
                self.registers[rd] = (self.registers[rs1] << self.registers[rs2])
            case 'srli':
                self.registers[rd] = (self.registers[rs1] >> (imm & 0x1F))
            case 'srai':
                if self.registers[rs1] >= 0:
                    self.registers[rd] = (self.registers[rs1] >> (imm & 0x1F))
                else:
                    self.registers[rd] = (self.registers[rs1] >> (imm & 0x1F)) | (-(self.registers[rs1]) >> (imm & 0x1F))
            case 'srl':
                self.registers[rd] = (self.registers[rs1] >> self.registers[rs2])
            case 'sra':
                if self.registers[rs1] >= 0:
                    self.registers[rd] = (self.registers[rs1] >> self.registers[rs2])
                else:
                    self.registers[rd] = (self.registers[rs1] >> self.registers[rs2]) | (-(self.registers[rs1]) >> self.registers[rs2])
            case 'slt':
                self.registers[rd] = 1 if self.registers[rs1] < self.registers[rs2] else 0
            case 'slti':
                self.registers[rd] = 1 if self.registers[rs1] < imm else 0
            case 'sltiu':
                num1 = self.registers[rs1] & 0xFFFFFFFF
                num2 = imm & 0xFFFFFFFF
                self.registers[rd] = 1 if num1 < num2 else 0
            case 'auipc':
                self.registers[rd] = self.pc + (imm << 12)
            case 'lui':
                self.registers[rd] = imm << 12
            case 'sb':
                self.memory[self.registers[rs1] + imm] = (self.registers[rs2] & 0xFF)
            case 'sh':
                val = (self.registers[rs2] & 0xFFFF)
                self.memory[self.registers[rs1] + imm + 1] = int(val & 0xFF00)
                self.memory[self.registers[rs1] + imm] = int(val & 0x00FF)
            case 'sw':
                val = (self.registers[rs2] & 0xFFFFFFFF)
                self.memory[self.registers[rs1] + imm + 3] = int(val & 0xFF000000)
                self.memory[self.registers[rs1] + imm + 2] = int(val & 0xFF0000)
                self.memory[self.registers[rs1] + imm + 1] = int(val & 0xFF00)
                self.memory[self.registers[rs1] + imm ] = int(val & 0x00FF)
        self.registers[0] = 0
        if self.registers[rd] >= 0:
            self.registers[rd] &= 0xFFFFFFFF



# Copies data into imm starting at j and incrementing.
def copy_vals(imm, data, j, dir):
    for i in data:
        imm[j] = i
        j += dir
    return imm


# Finding what the instruction is based on its opcode, funct3, and func7 bits.
def lookup_instruction(op, fun3, fun7, imm):
    try:
        opcode = format(int(op, 2), 'x')
        funct3 = int(fun3, 2)
        funct7 = format(int(fun7, 2), 'x')
    finally:
        instr = [['add', 'sll', 'slt', 'sltu', 'xor', 'srl', 'or', 'and'], ['addi', 'slli', 'slti', 'sltiu', 'xori', 'srli', 'ori', 'andi'],
                 ['ecall', 'csrrw', 'csrrs', 'csrrc', 'csrrwi', 'csrrsi', 'csrrci'], ['lb', 'lh', 'lw', '', 'lbu', 'lhu'], ['fence', 'fence.i'],
                 ['beq', 'bne', '', '', 'blt', 'bge', 'bltu', 'bgeu'], ['sb', 'sh', 'sw'], ['mul', 'mulh', 'mulhsu', 'mulhu', 'div', 'divu', 'rem', 'remu']]
        r_instr, i_instr1, i_instr2, i_instr3, i_instr4, sb_instr, s_instr, r_instr2 = 0, 1, 2, 3, 4, 5, 6, 7

        # Looking up what instruction it is.
        match opcode:
            case '33':
                if funct7 == '1':
                    return instr[r_instr2][funct3]
                return ('sub' if format(funct3, 'x') == '0' else 'sra' if format(funct3, 'x') == '5' else '') if funct7 == '20' else instr[r_instr][funct3]
            case '13':
                if funct3 == 5 and format(imm >> 5, 'x') == '20':
                    return 'srai'
                return instr[i_instr1][funct3]
            case '73':
                return instr[i_instr2][funct3]
            case '3':
                return instr[i_instr3][funct3]
            case '0F':
                return instr[i_instr4][funct3]
            case '63':
                return instr[sb_instr][funct3]
            case '23':
                return instr[s_instr][funct3]

        # Returning the special cases, or an error if the instruction given is not supported.
        return 'jalr' if opcode == '67' else 'jal' if opcode == '6f' else 'lui' if opcode == '37' else 'auipc' if opcode == '17' else 'Instruction Not Supported'


# Printing out the RISC-V instruction that we disassembled.
def print_instruction(opcode, name, rd, rs1, rs2, imm, instr_format, instr):
    if name != 'Instruction Not Supported':
        print(format(name, '>6') + ' x', end="")

    # Printing out the instruction based on what type of instruction it is.
    # imm_str = get_immstr(instr_format, imm)
    if instr_format == 'R':
        print(rd + ', x' + rs1 + ', x' + rs2)
    elif instr_format == 'I':
        func3 = (instr & int("7000", 16)) >> 12
        imm = sign_imm(imm, instr_format)
        if func3 == 1 or func3 == 5:
            imm = (instr & int("1F00000", 16)) >> 20
        if opcode == '0000011' or opcode == '1100111':
            print(rd + ', ' + str(imm) + '(x' + rs1 + ')')
        else:
            print(rd + ', x' + rs1 + ', ' + str(imm))
    elif instr_format == 'S':
        imm = sign_imm(imm, instr_format)
        print(rs2 + ', ' + str(imm) + '(x' + rs1 + ')')
    elif instr_format == 'UJ' or instr_format == 'U':
        imm = sign_imm(imm, instr_format)
        print(rd + ', ' + str(imm))
    elif instr_format == 'SB':
        imm = sign_imm(imm, instr_format)
        print(rs1 + ', x' + rs2 + ', ' + str(imm))
    return


def sign_imm(imm, instr_format):
    match instr_format:
        case 'I':
            if imm > 2**11:
                imm = two_compl(imm, 12)
        case 'S':
            if imm > 2**11:
                imm = two_compl(imm, 12)
        case 'U':
            if imm > 2**31:
                imm = two_compl(imm, 32)
        case 'UJ':
            if imm > 2**20:
                imm = two_compl(imm, 21)
        case 'SB':
            if imm > 2**12:
                imm = two_compl(imm, 13)
    return imm


def get_immstr(instr_format, imm):
    imm_str = ''
    if instr_format == 'I' or instr_format == 'S':
        imm_str = ''.join([str(i) for i in imm[0:12]])
    elif instr_format == 'SB':
        imm_str = ''.join([str(i) for i in imm[0:13]])
    elif instr_format == 'U':
        imm_str = ''.join([str(i) for i in imm[12:32]])
    elif instr_format == 'UJ':
        imm_str = ''.join([str(i) for i in imm[1:21]])
    if instr_format == 'S' or instr_format == 'UJ' or instr_format == 'SB':
        imm_str = imm_str[::-1]
    return imm_str


# Define 2's complement
def two_compl(number, bits):
    return ~((2 ** bits - 1) ^ number)


if __name__ == '__main__':

    YB = YB_60()
    if len(sys.argv) == 2:
        YB.read_in_file(open(sys.argv[1]))

    strInput = str(input('> '))
    while strInput != 'exit' and strInput != '\04':

        # Determining what to do with the users input.
        try:
            if strInput.isalnum() and not ('r' in strInput) and not ('t' in strInput) and not ('info' == strInput) and not ('s' in strInput):
                YB.display_mem_address(int(strInput, 16))
            elif '.' in strInput:
                YB.display_range_mem_address(strInput)
            elif ':' in strInput:
                YB.edit_mem_address(strInput)
            elif 'r' in strInput:
                YB.run_program(strInput)
            elif 't' in strInput:
                YB.disassemble(strInput)
            elif 's' in strInput:
                YB.step_thru(strInput)
            elif 'info' == strInput:
                YB.display_info()
            else:
                print('Not a valid command, try again.', strInput)
        except ValueError:
            print('Error: Address provided is not a hexadecimal number.')
        except Exception:
            print('Problem Encountered.')

        strInput = str(input('> '))
