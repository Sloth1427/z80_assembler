# z80_assembler

As part of designing and building my own z80-based 8-bit computer, I needed to write an assembler to turn z80 assembly code into machine code that the CPU understands.

The assembler checks for errors, and then produces a 'prn' file with the machine code next to the assembly language.

This version is not quite the final version (which is on a raspberry Pi which I can't find at the moment), so the input assembler file path is awkwardly set in the error_checking.py file.

Run assemble_prn.py to produce a prn output (a text file of the hex machine code annotated with the assembly code).
