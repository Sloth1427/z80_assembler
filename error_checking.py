'''
This script will do a first pass over the assembler source file, checking the all mnemomics are valid
and have the appropriate operands etc.

It will read each line, and after the 'START:' label is found, will check if any EQU statements are made, e.g.

EQU PORT1 00

It will then collect all EQU nicknames in a dict.

The script will then split each line into the following, ignoring lines with only whitespace or a comment

- Label (if any)
- Mnemonic
- Operand 1 (if any)
- Operand 2 (if any)
- Comment (if any)

Each mnemonic will be checked to see if it is in the opcode table. Each instruction will also be checked to see that it
has the correct number and type of operands, or that one or more operands is in the EQU dict, and its value is
appropriate

As labels are detected, they will be collected in a list, in order to test if operands that are not in the opcode table
are in the label list. If a label is used but does not appear as an operand, an error will be thrown (and vice versa)

'''

import csv  # needed to read the opcode table (is standard python lib)
import syntax_options as syntax
import assembler_functions as assembler



#### initialise some variables ####

asm_line_counter = 0  # keeps track of the line of asm text file being read to display with error messages

#memory_address = '(0000)'  # string representing the current address in hex. Only needed for pre-assembly

asm_file_name = 'barden.asm'  # name of asm file for testing

equ_dict = {}  # to hold names and values of static variables declared with EQU statements at start of source

label_dict = {}  # used to collect labels and the line on which they were used (for error messages)

error_flag = False  # flag is set to true if error is given

#### open the opcode table csv and read each column into a list ####

#NB: this was taken from
# https://stackoverflow.com/questions/19486369/extract-csv-file-specific-columns-to-list-in-python

# open the file in universal line ending mode
with open('z80_opcodes_table.csv', 'rU') as infile:
    # read the file as a dictionary for each row ({header : value})
    reader = csv.DictReader(infile)
    data = {}
    for row in reader:
        for header, value in row.items():
            try:
                data[header].append(value)
            except KeyError:
                data[header] = [value]

# put each column into a list, with the list name as col name
table_mnemonic = data['\ufeffMnemonic']  # first col header has string prefix, presumably to do with text formatting
table_op1 = data['Op1']
table_op2 = data['Op2']
table_byte1 = data['byte1']
table_byte2 = data['byte2']
table_byte3 = data['byte3']
table_byte4 = data['byte4']



#### read in asm_file asfile object ####

asm_file = open(asm_file_name, 'r')  # open asm file into file object
num_lines = sum(1 for line in asm_file)
asm_file.seek(0)  # reset file reading pointer to start of file


#### search line-by-line to find 'START' and 'END', while incrementin the line_counter ####

start_line = 0
end_line = 0

#search for START
for line in asm_file:
    asm_line_counter += 1  # increment line counter
    line = line.strip()  # remove whitespace from string
    if line == 'START':
        start_line = asm_line_counter  # update variable
        asm_file.seek(0)  # reset file reading pointer to start of file
        break  # break from loop of START found
    elif asm_line_counter == num_lines:  # or of no START found by last line, exit
        print('ERROR: '+asm_file_name+' does not contain START flag')
        asm_file.close()
        quit()

asm_line_counter = 0  # reset line counter for second pass

# search for END
for line in asm_file:
    asm_line_counter += 1  # increment line counter
    line = line.strip()  # remove whitespace from string
    if line == 'END':
        end_line = asm_line_counter  # update variable
        if end_line > start_line:
            asm_file.seek(0)  # reset file reading pointer to start of file
            break  # break from loop if START comes before END
        else:
            print('ERROR: ' + asm_file_name + ' has END flag before START flag to signal start of source')
            asm_file.close()
            quit()
    elif asm_line_counter == num_lines:  # or of no END found by last line, exit
        print('ERROR: '+asm_file_name+' does not contain END flag to signal end of source')
        asm_file.close()
        quit()

#### Collect labels ####
#### Starting at line after 'START', read each line with text and parse ####
#### into label, mnemonic, op1, op2, and comment                        ####

# this first pass is just to collect all the labels up

asm_file.seek(0)  # reset file reading pointer to start of file
asm_line_counter = 0  # reset line counter for third pass


for line in asm_file:

    asm_line_counter += 1  # increment line counter, so can print line with error messages

    if '>' in line:
        print('Assembler error in line' + str(asm_line_counter) + ': ">" is not allowed')
        error_flag = True

    if '<' in line:
        print('Assembler error in line' + str(asm_line_counter) + ': "<" is not allowed')
        error_flag = True

    # start reading instructions between START and END labels only
    if asm_line_counter > start_line and asm_line_counter < end_line:

        if line.strip() != '':  # if line is not empty
            label, mnemonic, op1, op2, comment = assembler.parse_instruction(line)  # get instruction fields

            if label != '':  # if there is a label
                if label in label_dict.keys():
                    print('Assembler error in line ' + str(asm_line_counter) +': Label "' + label + '" already used on line ' + str(label_dict[label]))
                    error_flag = True  # set error flag
                elif label in table_mnemonic:
                    print('Assembler error in line ' + str(asm_line_counter) + ': label "' + label + '" is same as instruction mnemonic')
                    error_flag = True
                else:
                    label_dict[label] = asm_line_counter  # add label to label list



#### Starting at line after 'START', read each line with text and parse ####
#### into label, mnemonic, op1, op2, and comment                        ####


asm_file.seek(0)  # reset file reading pointer to start of file
asm_line_counter = 0  # reset line counter for fourth pass


for line in asm_file:

    asm_line_counter += 1  # increment line counter, so can print line with error messages

    # start reading instructions between START and END labels only
    if asm_line_counter > start_line and asm_line_counter < end_line:

        # check for 'ORG' on first line after START
        if asm_line_counter == start_line+1:  # if is first line after START
            label, mnemonic, op1, op2, comment = assembler.parse_instruction(line)  # get instruction fields
            if mnemonic == 'ORG':
                if assembler.operand_type(op1) != ['(XXxx)']:
                    print('Assembler error on line '+str(asm_line_counter)+ ': '+'"' + op1 + '" is not a valid operand for "ORG" statement. Must be 16-bit hex address in form "(XXxx)"')
                    error_flag = True  # set error flag
                elif assembler.is_hex(op1[1:5], 2) == False:
                    error_flag = True  # set error flag
                    print('Assembler error on line '+str(asm_line_counter)+ ': '+'"' + op1 + '" is not a valid operand for "ORG" statement. Must be valid 16-bit address in hex in form "(XXxx)"')
                elif op2 != '':
                    error_flag = True  # set error flag
                    print('Assembler error on line '+str(asm_line_counter)+ ': '+'"ORG" statement does not take an operand 2')

                org = op1  # get org for assemble_prn

            else:
                error_flag = True  # set error flag
                print('Assembler error on line '+str(asm_line_counter)+ ': '+'First line after START must contain "ORG" statement, in form "ORG (XXxx)"')

        if line.strip() != '':  # if line is not empty
            label, mnemonic, op1, op2, comment = assembler.parse_instruction(line)  # get instruction fields


            # if line is not just a comment, and if line is not EQU or ORG statement (which is are instructions to
            # the assembler, not a z80 instruction (and therefore not in opcode table),
            if (label + mnemonic + op1 + op2) != '' and mnemonic != 'EQU' and mnemonic != 'ORG':

                check, error = assembler.validate_instruction(mnemonic, op1, op2, table_mnemonic, table_op1, table_op2, equ_dict, label_dict)
                if check == False:
                    error_flag = True  # set error flag
                    print('Assembler error on line '+str(asm_line_counter)+ ': '+ error)

            # if the instruction is an EQU statement, e.g. 'EQU PORT1, 3D', make entry to EQU dict
            if mnemonic == 'EQU':
                equ_dict[op1] = op2  # add pair to equ dictionary
                #print(op1 + ' = ' + equ_dict[op1])  # it works! Love dictionaries!



if error_flag == True:  # if errors were thrown
    asm_file.close()  # close file to prevent accidents
    print('Assembly aborted due to errors')
    quit()
else:
    print('No errors detected in asm file')
    asm_file.close()

