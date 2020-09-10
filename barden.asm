Assembly example from Barden

START
ORG (0100)

XOR A
LD B, 0A ; value changed from dec to hex
LOOP: ADD A, B
DEC B
JP NZ, LOOP
HLT

END
