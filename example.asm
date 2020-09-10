This is an example asm file for testing the assembler.

Anything before the START assembler-instruction will be ignored.

So this is a good place to put notes.

NOTE: all numbers are in Hex. This is real programming.

indents etc should be reasonably well tolerated.

First line after START must be ORG statement


START
ORG (0000)

EQU PORT1, (01) ; an IO address
EQU STACK, (FFFF) ; The initial value of SP
EQU ARG1, 46 ; a random 1-byte number

;random comment

JP BEGIN
ADD A, A
BEGIN: LD A,24 ; load acc with 24H
LD (IX+FF), B
LD D, ARG1
ADD A, FF ; comment
JP BEGIN
EXX

END
