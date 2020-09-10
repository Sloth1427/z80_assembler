import syntax_options as syntax
import re  # standard regex library

#### Error checking functions ####

# parses in a line and splits into asm fields
def parse_instruction(line):


    label = ""
    mnemonic = ""
    op1 = ""
    op2 = ""
    comment = ""

    line = line.strip()  # strip leading and trailing whitespace from line

    #  if line is empty, return all empty instruction fields
    if line == "":
        return label, mnemonic, op1, op2, comment

    # split line string by various delimeters

    # take off comment
    if len(line.split(syntax.comment_delim, 1)) == 2:  # if line has comment
        line, comment = line.split(syntax.comment_delim, 1)

    # take off label
    if len(line.split(syntax.label_delim, 1)) == 2:  # if line has label
        label, line = line.split(syntax.label_delim, 1)

    line = line.strip()  # clean up line again

    if line == "":
        return label, mnemonic, op1, op2, comment

    # split on any white space, and take first element as mnemonic
    mnemonic = line.split(None, 1)[0]

    # if operand(s) where present
    if len(line.split(None, 1)) == 2:
        line = line.split(None, 1)[1]

        # get operands if present
        if len(line.split(syntax.operand_delim, 1)) == 2:
            op1, op2 = line.split(syntax.operand_delim, 1)
        else:
            op1 = line


    label = label.strip()
    mnemonic = mnemonic.strip()
    op1 = op1.strip()
    op2 = op2.strip()
    comment = comment.strip()

    return label, mnemonic, op1, op2, comment


# check if string is valid x-bit hexadeximal number
def is_hex(string, byte):

    hex_chars = '0123456789ABCDEF'

    if len(string) != (byte*2):
        return False

    return all(char in hex_chars for char in string)  # returns true if all chars are allowed. Otherwise False.



# determine operand type, i.e
# XXxx, zz, nn, (XXxx), (zz), (IX+nn), (IY+nn)

def operand_type(operand):

    #if operand == '':
       # return ''  # on operand

    if is_hex(operand,1) == True:
        return ['nn', 'zz']  # can't distinguish between these two types

    if is_hex(operand,2) == True:
        return ['XXxx']

    if re.match("\(....\)", operand):
        if is_hex(operand[1:5],2) == True:
            return ['(XXxx)']

    if re.match("\(..\)", operand):
        if is_hex(operand[1:3], 1) == True:
            return ['(zz)']

    if re.match("\(IX\+..\)", operand):
        if is_hex(operand[4:6], 1) == True:
            return ['(IX+nn)']

    if re.match("\(IY\+..\)", operand):
        if is_hex(operand[4:6], 1) == True:
            return ['(IY+nn)']

    else:
        return ['INVALID']





# check of instruction is valid. Returns True if it is, with empty error message

def validate_instruction(mnemonic, op1, op2, table_mnemonic, table_op1, table_op2, equ_dict, label_dict):

    error_message = ''

    ## check that both op1 and op2 are not labels, which I think should not be allowed

    if op1 in label_dict.keys() and op2 in label_dict.keys():
        error_message = 'Both operand 1, "' + op1 + '", and operand 2 "' + op2 + '" appear to be labels'
        return False, error_message

    ## first check if op1 and/or op2 are nicknames for values, i.e. are in equ_dict

    if op1 in equ_dict.keys():  # if it is
        if op1 in label_dict.keys():
            error_message = '"' + op1 + '" is both an EQU alias and a label name'
            return False, error_message
        op1 = equ_dict[op1]  # make op1 equal to the value, so it can be error checked

    if op2 in equ_dict.keys():  # if it is
        if op2 in label_dict.keys():
            error_message = '"' + op2 + '" is both an EQU alias and a label name'
            return False, error_message
        op2 = equ_dict[op2]  # make op2 equal to the value, so it can be error checked

    ## then check of mnemonic is in mnemonic list ##

    if mnemonic not in table_mnemonic:
        error_message = mnemonic + ' is not a valid mnemonic'
        return False, error_message  # return False and error message of not in table


    ## if mnemonic is valid, check if op1 is valid for given mnemonic ##

    # get indices of mnemomic in table_mnemonic
    indices_mnemonic = [i for i, x in enumerate(table_mnemonic) if x == mnemonic]

    # subset table lists based on indices_mnemonic
    table_mnemonic_sublist = [table_mnemonic[index] for index in indices_mnemonic]
    table_op1_sublist = [table_op1[index] for index in indices_mnemonic]
    table_op2_sublist = [table_op2[index] for index in indices_mnemonic]

    # check if Op1 is explicit operand, i.e. with no variable component.
    # If it isnt, it still might be valid in the form of
    # (XXxx), (IX+nn), (IY+nn), zz, XXxx, nn, or zz

    if op1 in label_dict.keys():  # if op1 is in label_list
        op1_type = ['(XXxx)']  # then it must be an address
    else:
        op1_type = operand_type(op1)  # get operand type

    if op1 not in table_op1_sublist:

        #op1_type = operand_type(op1)  # get operand type

        if op1_type[0] == 'INVALID':
            error_message = 'Operand 1, "' + op1 +'", is not in a valid format (spaces are not tolerated), or is not valid for mnemonic "'+mnemonic+'"'
            return False, error_message

        if len(op1_type)==1:
            if op1_type[0] not in table_op1_sublist:
                error_message = '"' + op1 + '" is not a valid operand-1 for mnemonic "' + mnemonic +'"'
                return False, error_message

        if len(op1_type)==2:
            if op1_type[0] not in table_op1_sublist and op1_type[1] not in table_op1_sublist:
                error_message = '"'+op1 + '" is not a valid operand-1 for mnemonic "' + mnemonic + '"'
                return False, error_message



    ## if operand 1 is valid for mnemonic, check that operand 2 is valid for mnemonic and op1

    # get indices of op1 in table_op1_sublist
    indices_op1_sublist = [i for i, x in enumerate(table_op1_sublist) if x == op1]
    #print(indices_op1_sublist)
    indices_op1_type_sublist = []

    # get indices of op1_type in table_op1_sublist
    if len(op1_type) == 1:
        indices_op1_type_sublist = [i for i, x in enumerate(table_op1_sublist) if x == op1_type[0]]
    if len(op1_type) == 2:
        indices_op1_type_sublist = [i for i, x in enumerate(table_op1_sublist) if x == op1_type[0]] + [i for i, x in enumerate(table_op1_sublist) if x == op1_type[1]]


    indices_op1_sublist = indices_op1_sublist + indices_op1_type_sublist

    table_mnemonic_sublist = [table_mnemonic_sublist[index] for index in indices_op1_sublist]
    table_op1_sublist = [table_op1_sublist[index] for index in indices_op1_sublist]
    table_op2_sublist = [table_op2_sublist[index] for index in indices_op1_sublist]

    if op2 in label_dict.keys():  # of op2 is in label_list
        op2_type = ['(XXxx)']  # then it must be an address
    else:
        op2_type = operand_type(op2)  # get operand type


    if op2 not in table_op2_sublist:

        #op2_type = operand_type(op2)  # get operand type

        if op2_type[0] == 'INVALID':
            error_message = 'Operand 2, "' + op2 +'", is not in a valid format (spaces are not tolerated), or is not valid for mnemonic "'+mnemonic+ '" and operand 1 "'+op1+'"'
            return False, error_message

        if len(op2_type)==1:
            if op2_type[0] not in table_op2_sublist:
                error_message = '"' + op2 + '" is not a valid operand-2 for mnemonic "' + mnemonic+ '" and operand-1 "' +op1+ '"'
                return False, error_message

        if len(op2_type)==2:
            if op2_type[0] not in table_op2_sublist and op2_type[1] not in table_op2_sublist:
                error_message = '"' + op2 + '" is not a valid operand-2 for mnemonic "' + mnemonic + '" and operand-1 "' +op1+ '"'
                return False, error_message




    return True, error_message



# add a decimal number to a hex number
def hex_add(Hex, dec):
    Hex = int(Hex, 16)  # convert to decimal
    Hex = Hex + dec
    Hex = hex(Hex)
    Hex = Hex[2:]  # remove '0x' prefix
    Hex = Hex.upper()
    return Hex

def inc_address(address):

    # check that address is in form (XXxx)
    if operand_type(address) != ['(XXxx)']:
        print('Error while incrementing address. Address not in form (XXxx)')
        return

    address = address[1:-1]  # remove brackets
    address = hex_add(address, 1)  # increment hex by 1

    length = len(address)

    if length > 4:
        print('Error while incrementing address. Address is greater than 16 bit')
        return

    address = ('0'*(4-length)) + address  # add correct number of leading zeroes

    address = '(' + address + ')'

    return address



# give mnemonic and operands, return list of machine codes
def get_machine_codes(mnemonic,
                      op1,
                      op2,
                      table_mnemonic,
                      table_op1,
                      table_op2,
                      table_byte1,
                      table_byte2,
                      table_byte3,
                      table_byte4,
                      label_dict,
                      label_occurrence_dict):

    #print('getting machine codes')
    bytes = ['','','','']

    # first check if op1 or op2 are references to labels that have already been added to the label_occurrence_dict.
    # If so, simply convert to label_occurrence_dict value
    if op1 in label_occurrence_dict.keys():
        op1 = label_occurrence_dict[op1]
    if op2 in label_occurrence_dict.keys():
        op2 = label_occurrence_dict[op2]


    if op1 in table_op1:
        op1_type = [op1]
    elif op1 in label_dict.keys():  # if op1 is in label_list
        op1_type = ['(XXxx)']  # then it must be an address
    else:
        op1_type = operand_type(op1)  # get operand type


    if op2 in table_op2:
        op2_type = [op2]
    elif op2 in label_dict.keys():  # if op2 is in label_list
        op2_type = ['(XXxx)']  # then it must be an address
    else:
        op2_type = operand_type(op2)  # get operand type

    mnemonic_indices = [i for i, x in enumerate(table_mnemonic) if x == mnemonic]

    if len(op1_type) == 1:
        op1_indices = [i for i, x in enumerate(table_op1) if x == op1_type[0]]
    if len(op1_type) == 2:
        op1_indices = [i for i, x in enumerate(table_op1) if x == op1_type[0]] + [i for i, x in enumerate(table_op1) if x == op1_type[1]]

    if len(op2_type) == 1:
        op2_indices = [i for i, x in enumerate(table_op2) if x == op2_type[0]]
    if len(op2_type) == 2:
        op2_indices = [i for i, x in enumerate(table_op2) if x == op2_type[0]] + [i for i, x in enumerate(table_op2) if x == op2_type[1]]

    ## now need to get index of correct line of table
    index = [x for x in mnemonic_indices if x in op1_indices and x in op2_indices]

    if len(index) != 1:
        print('Error: no ambiguous machine codes identified for instruction "' + mnemonic + ' ' + op1 + ', ' + op2 + '"')

    index = index[0]
    bytes_type = [table_byte1[index], table_byte2[index], table_byte3[index], table_byte4[index]]
    #print('generic bytes: '+str(bytes_type))




    ## now need to put together the actual bytes

    for i in range(0, 4):

        # if bytes is unused
        if bytes_type[i] == '':
            bytes[i] = ''

        # if byte is always same value
        elif is_hex(bytes_type[i], 1) == True:
            bytes[i] = bytes_type[i]

        else: # byte_type must be xx, XX, zz, nn
            # need to search for 'xx', 'XX', 'zz', or 'nn' in op1_type and op2_type to get indices of appearance,
            # and then set byte to op1[indices] or op2[indices]

            # if op1 is a label that has not yet had address assigned to it, give temp byte
            if op1 in label_dict.keys():
                #print('op1 is unassigned label')
                if bytes_type[i] == 'xx':
                    bytes[i] = op1 + ' xx'
                elif bytes_type[i] == 'XX':
                    bytes[i] = op1 + ' XX'

            # if op2 is a label that has not yet had address assigned to it, give temp byte
            elif op2 in label_dict.keys():
                print('op2 is unassigned label')
                if bytes_type[i] == ' xx':
                    bytes[i] = op2 + ' xx'
                elif bytes_type[i] == ' XX':
                    bytes[i] = op2 + ' XX'

            else:

                # check that bytes_type[i] is not in both op1_type and op2_type
                check = 0
                for element in op1_type:
                    if bytes_type[i] in element:
                        check += 1
                for element in op2_type:
                    if bytes_type[i] in element:
                        check += 1
                if check >=2:
                    print('Error getting machine code. Byte type found in both op1 and op2')
                    return



                # check if bytes_type[i] in op1_type
                if len(op1_type) == 1:
                    if bytes_type[i] in op1_type[0]:
                        # get index/position of byte_type in op1
                        bytes[i] = op1[op1_type[0].find(bytes_type[i]) : op1_type[0].find(bytes_type[i]) + len(bytes_type[i])]

                elif len(op1_type) == 2:
                    if bytes_type[i] in op1_type[0]:
                        # get index/position of byte_type in op1
                        bytes[i] = op1[op1_type[0].find(bytes_type[i]): op1_type[0].find(bytes_type[i]) + len(bytes_type[i])]
                    elif bytes_type[i] in op1_type[1]:
                        # get index/position of byte_type in op1
                        bytes[i] = op1[op1_type[1].find(bytes_type[i]): op1_type[1].find(bytes_type[i]) + len(bytes_type[i])]



                # check if bytes_type[i] in op2_type
                if len(op2_type) == 1:
                    if bytes_type[i] in op2_type[0]:
                        # get index/position of byte_type in op1
                        bytes[i] = op2[op2_type[0].find(bytes_type[i]): op2_type[0].find(bytes_type[i]) + len(
                            bytes_type[i])]

                elif len(op2_type) == 2:
                    if bytes_type[i] in op2_type[0]:
                        # get index/position of byte_type in op1
                        bytes[i] = op2[op2_type[0].find(bytes_type[i]): op2_type[0].find(bytes_type[i]) + len(
                            bytes_type[i])]
                    elif bytes_type[i] in op2_type[1]:
                        # get index/position of byte_type in op1
                        bytes[i] = op2[op2_type[1].find(bytes_type[i]): op2_type[1].find(bytes_type[i]) + len(
                            bytes_type[i])]

    #print('actual bytes: '+str(bytes))

    return bytes

