
"""sample_programs.py - demo programs (Student 4).
All programs load at address 100.
Supported registers: R1, R2, ACC
"""

SAMPLE_PROGRAMS = {

    "1. Add two numbers": """\
LOAD R1, 10
LOAD R2, 5
ADD R1, R2
STORE R1, 200
HLT
""",

    "2. SUB, MUL, DIV": """\
LOAD R1, 20
LOAD R2, 4
SUB R1, R2
MUL R1, 3
DIV R1, R2
HLT
""",

    "3. AND, OR, NOT": """\
LOAD R1, 12
LOAD R2, 10
AND R1, R2
OR R1, 1
NOT R2
HLT
""",

    "4. STORE then LOAD": """\
LOAD R1, 42
STORE R1, 150
LOAD R2, [150]
HLT
""",

    "5. Compare": """\
LOAD R1, 7
LOAD R2, 9
CMP R1, R2
HLT
""",

    "6. JMP skips an instruction": """\
LOAD R1, 1
JMP 103
LOAD R1, 99
ADD R1, 1
HLT
""",

    "7. Error: divide by zero": """\
LOAD R1, 8
LOAD R2, 0
DIV R1, R2
HLT
""",

    "8. Error: bad memory address": """\
LOAD R1, 10
LOAD R2, 20
ADD R1, R2
STORE R1, 200

LOAD R1, 15
LOAD R2, 25
ADD R1, R2
STORE R1, 201

LOAD R1, 8
LOAD R2, 4
MUL R1, R2
STORE R1, 202

LOAD R1, 50
LOAD R2, 30
SUB R1, R2
STORE R1, 203

LOAD R1, [200]
LOAD R2, [201]
ADD R1, R2
STORE R1, 204

LOAD R1, [202]
LOAD R2, [203]
ADD R1, R2
STORE R1, 205

LOAD R1, [204]
LOAD R2, [205]
ADD R1, R2
STORE R1, 206

LOAD R1, [206]
ADD R1, 10
STORE R1, 207

LOAD R1, [207]
SUB R1, 20
STORE R1, 208

LOAD R1, [208]
ADD R1, 5
STORE R1, 209

LOAD R1, [209]
MUL R1, 2
STORE R1, 210

LOAD R1, [210]
SUB R1, 10
STORE R1, 211

LOAD R1, 100
STORE R1, 999

HLT
""",

}

DEFAULT_SAMPLE = "8. Error: bad memory address"
