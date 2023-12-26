# CENG 325 YB-60 Emulator

This is a YB-60 emulator that runs RISC-V instructions.

The program is run as follows:
  1.	Starting the program with an object file as an argument will load that program into the emulator.
  2.	Typing in an address will print the data at that location.
  3.	Typing in 2 addresses with a “.” between them will print all the data between those 2 locations.
  4.	Typing in an address with a “:” then bytes with spaces between them will replace anything after that address with the data entered in.
  5.	Typing in an address followed by an “r” will run all the code starting at that address.
  6.	Typing in an address followed by a “t” will disassemble the code and print out the instructions that they once were.
  7.	Typing in “info” will print out the contents of every register.
  8.	Typing in an address followed by an “s” will open a step through menu where the user can run one line of code at a time or print out the contents of the registers in-between lines of executed code.
    a.	Typing in a “s” in the submenu will step to the next instruction.
    b.	Typing in a “I” in the submenu will print out all the registers.
    c.	Typing in a “q” in the submenu will quit the step through function.
9.	You can exit the program by entering “exit”, ctrl-C, or ctrl-D.

The program imports and uses the following packages:
  1.	numpy
  2.	sys
  3.	re
  4.	BitArray from bitstring
This emulator was developed in python 3.10.

If a user gives an address or data that is not in hexadecimal, then the program will output an error message and does not preform the function specified. It then prompts the user for new input.
If an error occurs that causes the program to fail, the error message: “Problem Encountered.” Will be printed out. The program will quit what it was doing and return to the main menu.
There are 32, 32-bit registers, and 1048576 memory locations.

When a memory location followed by an “r” is entered the program counter is set to that memory address. The first 4 bytes are then grabbed and concatenated into the first instruction. That instruction is then parsed, and we determine the instruction format. Once it is parsed, we can print out all the bits in each section of the instruction to the screen. We can also determine the label for the instruction and print that out as well. Then the instruction is executed and the program counter is incremented, then the next instruction is grabbed, parsed and printed until the ebreak instruction is encountered.
When a memory location followed by a “t” is entered the program counter is once again set to that memory address. The 4 bytes after that address are then concatenated and turned into a string for the instruction. The instruction string is then parsed to discover what each part of it means. We can then take the opcode, fnuct3, funct7, and imm and look up the instructions name. Next it prints out the full assembly instruction from what it was before it was turned into object code.
When a memory location followed by an “s” is entered, the program counter is again set to that memory address. The 4 bytes after that address are then concatenated and turned into a string for the instruction. The instruction string is then parsed to discover what each part of it means. We can then take the opcode, fnuct3, funct7, and imm and look up the instructions name. Next it prints out the full assembly instruction from what it was before it was turned into object code. It runs that line of code then prompts the user if they want to step to the next line of code, print out all the registers, or quit the execution.

I have included some example object code files that were used for testing, you can also look at them to know how to create an object file for this emulator.

The following instructions are supported:
add, addi, sub, mul, mulh, mulhu, mulhsu, div, divu, rem, remu, and, andi, or, ori, xor, xori beq, bge, bgeu, blt, bltu, bne, jal, jalr, lb, lbu, lh, lhu, lw, slli, sll, srli, srai, srl, sra, slt, sltu, slti, sltiu, auipc, lui, sb, sh, sw.
