import numpy as np


class YB_60:
    memory = []
    program_counter = 0

    def __init__(self):
        self.memory = np.zeros(1048576)

    def parse_input(self, user_input):
        if user_input.isnumeric():
            return 0
        if '.' in user_input:
            return 1
        if ':' in user_input:
            return 2
        if 'R' in user_input:
            return 3
        return -1

    def display_mem_address(self, address):
        # Printing out the data in hex at the given address if it is a valid address.
        if self.memory.size > address >= 0:
            a = format(int(self.memory[address]), 'x')
            print(a.upper().zfill(2))
        else:
            print("Invalid address.")
        return

    def display_range_mem_address(self, addresses):
        nums = addresses.split('.')

        # Checking if the range is valid.
        if int(nums[0], 16) >= int(nums[1], 16):
            print("Invalid Memory Access, memory locations are not sequential.")
            return

        # Checking if each memory address is valid.
        if not (self.memory.size > int(nums[0], 16) >= 0) or not (self.memory.size > int(nums[1], 16) >= 0):
            print("Invalid Memory Address.")
            return

        # Printing out all the data in the provided memory range.
        i = int(nums[0], 16)
        print(format(i, 'x').upper(), end='    ')
        while i < int(nums[1], 16):
            a = format(int(self.memory[i]), 'x')
            print(a.upper().zfill(2), end=' ')
            i = i + 1
            if (i - int(nums[0], 16)) % 8 == 0:
                print()
                if (int(nums[1], 16) - i) != 0:
                    print(format(i, 'x').upper(), end='    ')

        # Printing a new line if the range was a multiple of 8.
        if (i - int(nums[0], 16)) % 8 != 0:
            print()
        return

    def edit_mem_address(self, input):
        strs = input.split(':')
        data = strs[1].split(' ')

        j = int(strs[0], 16)
        for i in data[1:]:
            self.memory[j] = int(i, 16)
            j = j + 1

        return

    def run_program(self, address):
        split = address.split('R')
        self.program_counter = int(split[0], 16)
        print('  PC        ' + 'OPC    ' + 'INST    ' + 'Rd    ' + 'Rs1    ' + 'Rs2')
        print(format(self.program_counter, 'x').upper().zfill(5))
        return


if __name__ == '__main__':

    YB = YB_60()

    print('>', end=' ')
    strInput = str(input())
    while strInput != 'exit':
        match YB.parse_input(strInput):
            case 0:
                YB.display_mem_address(int(strInput))
            case 1:
                YB.display_range_mem_address(strInput)
            case 2:
                YB.edit_mem_address(strInput)
            case 3:
                YB.run_program(strInput)
        print('>', end=' ')
        strInput = str(input())
