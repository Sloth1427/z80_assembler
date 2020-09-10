'''
This script will run the error check, and then assemble a prn file.

- Create new blank prn text file.
- For all lines up to, and including ORG declaration, simply copy asm file lines to prn file lines
- Thereafter, split line into instruction fields, and directly copy any blank lines, or lines containing
  only a comment.

- If line contains instruction without label field, or reference to label, look up/generate correct machine
  code bytes.
- write address and first byte before the instruction line.
- Any further byte instruction should be on a new line each, preceeded by their address.


'''


import error_checking  # runs the error checking
import assembler_functions as assembler

#### some variables ####

org = error_checking.org  # get from previously run error_checking.py
address = org
start_line = error_checking.start_line  # get from previously run error_checking.py
end_line = error_checking.end_line  # get from previously run error_checking.py

label_occurrence_dict = {}  # dictionary to hold label names, and the memory location of the instruction
 # that it is used to call, i.e. the address of the first byte of the instruction on whose line it appears
 # at the start of

#### open asm file, and create new blank prn file ####

## read in asm_file as file object

asm_file = open(error_checking.asm_file_name, 'r')  # open asm file into file object
num_lines = sum(1 for line in asm_file)
asm_file.seek(0)  # reset file reading pointer to start of file
asm_file_data = asm_file.readlines()  # read each line in to element of list

#asm_file.seek(0)  # reset file reading pointer to start of file

## create new prn file using asm file name

prn_file_name = error_checking.asm_file_name.split('.', 1)[0] + '.prn'  # create name
prn_file_data = []  # create empty list to take line data. Will then write this to file at end
#prn_file = open(prn_file_name, 'w').close()  # open prn file into file object, and clear any contents with .close()


#### start reading asm_file_data line by line, and copying lines up to and including ORG to prn_data ####
#### then for lines after, get instruction fields and get instruction bytes

line_counter = 0
for line in asm_file_data:
    line_counter += 1

    # if before start
    if line_counter <= start_line + 1:  # if line is ORG line, or before
        prn_file_data = prn_file_data + [line]  # just copy line to prn_data

    # if between start and end
    elif line_counter >= start_line + 1 and line_counter < end_line:

        # if line is blank, copy blank line
        if line.strip() == '':
            prn_file_data = prn_file_data + [line]  # just copy line to prn_data

        else:

            label, mnemonic, op1, op2, comment = assembler.parse_instruction(line)  # get instruction fields

            if (label + mnemonic + op1 + op2) == '':  # if there is only comment (or no comment)
                prn_file_data = prn_file_data + [line]  # just copy line to prn_data

            else:

                # check if op1 or op2 are equ aliases
                if op1 in error_checking.equ_dict.keys():
                    op1 = error_checking.equ_dict[op1]
                if op2 in error_checking.equ_dict.keys():
                    op2 = error_checking.equ_dict[op2]

                # check if there is a label, put it, and the address at which it is references in
                # label_occurrence_dict.
                if label != '':
                    label_occurrence_dict[label] = address


                    # if mneminic is not assembler instruction, get bytes etc
                if mnemonic != 'EQU':
                    machine_bytes = assembler.get_machine_codes(mnemonic,
                                                op1,
                                                op2,
                                                error_checking.table_mnemonic,
                                                error_checking.table_op1,
                                                error_checking.table_op2,
                                                error_checking.table_byte1,
                                                error_checking.table_byte2,
                                                error_checking.table_byte3,
                                                error_checking.table_byte4,
                                                error_checking.label_dict,
                                                label_occurrence_dict)

                    for i in range(0, 4):
                        if machine_bytes[i] != '':  # if byte is not unused
                            if i == 0:
                                prn_file_data = prn_file_data + [address + ' <' + machine_bytes[i] + '>    ' + line]
                            else:
                                prn_file_data = prn_file_data + [address + ' <' + machine_bytes[i] + '>\n']
                            address = assembler.inc_address(address)






    # if after end
    elif line_counter >= end_line:  # if line is END line, or after
        prn_file_data = prn_file_data + [line]  # just copy line to prn_data


#### Now need go through prn_file_data changing any temp bytes due to labels
#### to the actual bytes using label occurrence dict

for i in range(0, len(prn_file_data)):

    # if line contains '<' and '<'
    if '<' and '>' in prn_file_data[i]:
        # get <byte>
        byte_string = prn_file_data[i].split('<')[len(prn_file_data[i].split('<')) -1].split('>')[0]

        # if byte string contains space, must be temp byte label
        if ' ' in byte_string:
            label_name = ''
            print('temp byte detected')
            label_name = byte_string.split(' ',1)[0]
            print(byte_string.split(' ', 1)[1])
            if byte_string.split(' ', 1)[1] == 'xx':
                byte_string = label_occurrence_dict[label_name][3:5]
                print(byte_string)
            elif byte_string.split(' ', 1)[1] == 'XX':
                byte_string = label_occurrence_dict[label_name][1:3]
                print(byte_string)

            prn_file_data[i] = prn_file_data[i].split('<',1)[0] + '<' + byte_string + '>' + prn_file_data[i].split('>',1)[1]





#### write prn_file_data to prn_file ####

prn_file = open(prn_file_name, 'w').close()# open prn file into file object, and clear any contents with .close()
prn_file = open(prn_file_name, 'w')

with prn_file as file:
    file.writelines(prn_file_data)

#### close files ####

asm_file.close()
prn_file.close()

