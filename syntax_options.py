'''
This file contains the various delimiter characters, and other options for the assembler.

Below is an example line

Label: mnemomic op1,op2 ;comment

'''

label_delim = ':'  # labels come before a colon

comment_delim = ';'  # comments come after a semi-colon

operand_delim = ','  # operands are separated by a comma

mnemonic_delim = ' '  # instruction mnemonic and any # operand(s) are separated by space

source_start = 'START:'  # label defining that whatever comes after this line should be worked on by the assembler

source_end = 'END:'  # signals the end of the source

