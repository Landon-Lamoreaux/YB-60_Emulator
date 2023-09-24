import numpy as np
import sys
import re


class YB_60:
    memory = []
    program_counter = 0

    def __init__(self):
        self.memory = np.zeros(1048576)

    def parse_input(self, user_input):
        if user_input.isalnum() and not ('R' in user_input):
            return 0
        if '.' in user_input:
            return 1
        if ':' in user_input:
            return 2
        if 'R' in user_input:
            return 3
        return -1

    def read_in_file(self, file_data):
        file = open(file_data)
        data_string = file.read()
        data_string = data_string.split(':')
        offset = 0

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
        split = address.split('R')
        try:
            self.program_counter = int(split[0], 16)
        except:
            print('Error: Address provided is not a hexadecimal number.')
            return
        print('  PC        ' + 'OPC    ' + 'INST    ' + 'Rd    ' + 'Rs1    ' + 'Rs2')
        print(format(self.program_counter, 'x').upper().zfill(5))
        return


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
            case default:
                print('Not a valid command, try again.', strInput)

        strInput = str(input('>'))
