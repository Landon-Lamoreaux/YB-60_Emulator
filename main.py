import numpy as np
import sys
import re
from bitstring import BitArray


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

        # Updating the memory from the starting location with the data given.
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

        pc = self.program_counter

        # Grabbing the instruction from memory.
        instruction = (format(int(self.memory[pc + 3]), "08b") + format(int(self.memory[pc + 2]), "08b") +
                       format(int(self.memory[pc + 1]), "08b") + format(int(self.memory[pc]), "08b"))

        # Printing out the header.
        print(format('PC', '>5') + format('OPC', '>9') + format('INST', '>7') + '  rd  ' + '  rs1  ' + 'rs2/imm')

        # Reading through and printing out all the instructions from the given address to the terminator.
        while format(int(instruction, 2), 'x') != '100073':
            imm_str = ''

            # Printing out the program counter and the instruction in hexadecimal.
            print(format(pc, 'x').upper().zfill(5) + format(format(int(instruction, 2), 'x').upper().zfill(8), '>9'), end='')

            # Parsing the instruction and determining the name of the instruction.
            opcode, rd, funct3, rs1, rs2, funct7, imm, instr_format = self.parse_instruction(instruction)
            name = lookup_instruction(opcode, funct3, funct7, imm)
            print(format(name.upper(), '>7'), end='')

            # Printing out the rd value if there is a rd in the instruction.
            if rd != '0':
                print(format(str(rd), '>6'), end='')
            else:
                print('      ', end='')

            # Printing out the rs1 value if there is a rs1 in the instruction.
            if rs1 != '0':
                print(format(str(rs1), '>6'), end='')
            else:
                print('      ', end='')

            # Printing out the rs2 and or immediate register.
            if rs2 != '0':
                print(' ' + format(str(rs2), '<5'), end='')
            if instr_format == 'I' or instr_format =='S':
                imm_str = ''.join([str(i) for i in imm[0:12]])
            elif instr_format == 'SB':
                imm_str = ''.join([str(i) for i in imm[1:13]])
            elif instr_format == 'U':
                imm_str = ''.join([str(i) for i in imm[12:32]])
            elif instr_format == 'UJ':
                imm_str = ''.join([str(i) for i in imm[1:21]])
            if instr_format == 'S' or instr_format == 'UJ' or instr_format == 'SB':
                imm_str = imm_str[::-1]
            print(' ' + imm_str, end='')

            pc += 4  # Updating the program counter.

            # Grabbing the instruction from memory.
            instruction = (format(int(self.memory[pc + 3]), "08b") + format(int(self.memory[pc + 2]), "08b") +
                           format(int(self.memory[pc + 1]), "08b") + format(int(self.memory[pc]), "08b"))

            print('')  # Printing out a new line.

            # Printing out 'EBREAK' if that is the next instruction.
            if format(int(instruction, 2), 'x') == '100073':
                print(format(pc, 'x').upper().zfill(5) + format(format(int(instruction, 2), 'x').upper().zfill(8), '>9') + ' EBREAK')
        return

    def display_info(self):
        count = 0
        # Printing out the contents of all 32 registers.
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

        pc = address  # Setting the program counter

        # Grabbing the first instruction from memory.
        instruction = (format(int(self.memory[pc + 3]), "08b") + format(int(self.memory[pc + 2]), "08b") +
                       format(int(self.memory[pc + 1]), "08b") + format(int(self.memory[pc]), "08b"))

        while format(int(instruction, 2), 'x') != '100073':
            pc += 4

            # Parsing the instruction and determining the instructions name.
            opcode, rd, funct3, rs1, rs2, funct7, imm, instr_format = self.parse_instruction(instruction)
            name = lookup_instruction(opcode, funct3, funct7, imm)

            # Printing out the instruction and all the following values.
            print_instruction(opcode, name, str(int(rd, 2)), str(int(rs1, 2)), str(int(rs2, 2)), imm, instr_format)

            # Grabbing the next instruction from memory.
            instruction = (format(int(self.memory[pc + 3]), "08b") + format(int(self.memory[pc + 2]), "08b") +
                           format(int(self.memory[pc + 1]), "08b") + format(int(self.memory[pc]), "08b"))

            # Printing out the termination statement if the instruction is the terminator.
            if format(int(instruction, 2), 'x') == '100073':
                print('ebreak')
        return


    def parse_instruction(self, data):
        # Setting up our variables.
        op = int(data[25:32], 2)
        opcode = data[25:32]
        imm = np.zeros(32, dtype=int)
        formats = ''
        rd, funct3, rs1, rs2, funct7 = '0', '0', '0', '0', '0'

        # Parsing the instruction into its parts and determining what type it is.
        if op == 51:     # R Format.
            formats = 'R'
            funct7 = data[0:7]
        elif op == 3 or op == 15 or op == 19 or op == 103 or op == 115:   # I Format.
            formats = 'I'
            imm = copy_vals(imm, data[0:12], 0)
        elif op == 35:               # S Format.
            formats = 'S'
            imm = copy_vals2(imm, data[0:7], 11)
            imm = copy_vals2(imm, data[20:25], 4)
        elif op == 99:              # SB Format.
            formats = 'SB'
            imm = copy_vals(imm, data[20:24], 1)
            imm[11] = data[24]
            imm[12] = data[0]
            imm = copy_vals2(imm, data[1:7], 10)
        elif op == 23 or op == 55:   # U Format.
            formats = 'U'
            imm = copy_vals(imm, data[0:20], 12)
        elif op == 111:              # UJ Format.
            formats = 'UJ'
            imm[20] = int(data[0])
            imm = copy_vals(imm, data[1:11], 1)
            imm[11] = int(data[11])
            imm = copy_vals(imm, data[12:20], 12)

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


# Copies data into imm starting at j and incrementing.
def copy_vals(imm, data, j):
    for i in data:
        imm[j] = i
        j += 1
    return imm


# Copies data into imm starting at j and decrementing.
def copy_vals2(imm, data, j):
    for i in data:
        imm[j] = i
        j -= 1
    return imm


# Finding what the instruction is based on its opcode, funct3, and func7 bits.
def lookup_instruction(op, fun3, fun7, imm):
    try:
        opcode = format(int(op, 2), 'x')
        funct3 = int(fun3, 2)
        funct7 = format(int(fun7, 2), 'x')
    finally:

        r_instr = ['add', 'sll', 'slt', 'sltu', 'xor', 'srl', 'or', 'and']
        i_instr1 = ['addi', 'slli', 'slti', 'sltiu', 'xori', 'srli', 'ori', 'andi']
        i_instr2 = ['ecall', 'csrrw', 'csrrs', 'csrrc', 'csrrwi', 'csrrsi', 'csrrci']
        i_instr3 = ['lb', 'lh', 'lw', 'lbu', 'lhu']
        i_instr4 = ['fence', 'fence.i']
        sb_instr = ['beq', 'bne', '', '', 'blt', 'bge', 'bltu', 'bgeu']
        s_instr = ['sb', 'sh', 'sw']

        # Looking up what instruction it is.
        match opcode:
            case '33':
                if format(funct3, 'x') == '0' and funct7 == '20':
                    return 'sub'
                if format(funct3, 'x') == '5' and funct7 == '20':
                    return 'sra'
                return r_instr[funct3]
            case '13':
                if funct3 == '5' and format(int(imm[5:11], 2), 'x') == '20':
                    return 'srai'
                return i_instr1[funct3]
            case '73':
                return i_instr2[funct3]
            case '3':
                return i_instr3[funct3]
            case '0F':
                return i_instr4[funct3]
            case '63':
                return sb_instr[funct3]
            case '23':
                return s_instr[funct3]
            case '67':
                return 'jalr'
            case '6f':
                return 'jal'
            case '37':
                return 'lui'
            case '17':
                return 'auipc'

    # If no instruction was found we return this.
    return 'Instruction Not Supported'


# Printing out the RISC-V instruction that we disassembled.
def print_instruction(opcode, name, rd, rs1, rs2, imm, instr_format):
    name = format(name, '>6')
    if name != 'Instruction Not Supported':
        print(name + ' x', end="")

    # Printing out the instruction based on what type of instruction it is.
    match instr_format:
        case 'R':
            print(rd + ', x' + rs1 + ', x' + rs2)
        case 'I':
            if opcode == '0000011' or opcode == '1100111':
                print(rd + ', ' + str(int(''.join([str(i) for i in imm[0:12]]), 2)) + '(x' + rs1 + ')')
            else:
                print(rd + ', x' + rs1 + ', ' + str(int(''.join([str(i) for i in imm[0:12]]), 2)))
        case 'S':
            imm_num = BitArray(bin=''.join([str(i) for i in imm[0:12]])[::-1])
            print(rs2 + ', ' + str(imm_num.uint) + '(x' + rs1 + ')')
        case 'UJ':
            imm_num = BitArray(bin=''.join([str(i) for i in imm[1:21]])[::-1])
            print(rd + ', ' + str(imm_num.int))
        case 'U':
            imm_num = BitArray(bin=''.join([str(i) for i in imm[12:32]]))
            print(rd + ', ' + str(imm_num.int))
        case 'SB':
            imm_num = BitArray(bin=''.join([str(i) for i in imm[0:13]])[::-1])
            print(rs1 + ', x' + rs2 + ', ' + str(imm_num.int))
    return


if __name__ == '__main__':

    YB = YB_60()

    if len(sys.argv) == 2:
        YB.read_in_file(sys.argv[1])

    strInput = str(input('>'))
    while strInput != 'exit' and strInput != '\04':

        # Determining what to do with the users input.
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
