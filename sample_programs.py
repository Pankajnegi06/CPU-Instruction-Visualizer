"""sample_programs.py - demo programs (Student 4). They load at address 100."""

SAMPLE_PROGRAMS = {
    "1. Add two numbers": """\
LOAD R1, 10     ; R1 = 10
LOAD R2, 5      ; R2 = 5
ADD R1, R2      ; R1 = 15
STORE R1, 200   ; RAM[200] = 15
HLT
""",
    "2. SUB, MUL, DIV": """\
LOAD R1, 20
LOAD R2, 4
SUB R1, R2      ; 16
MUL R1, 3       ; 48
DIV R1, R2      ; 12
HLT
""",
    "3. AND, OR, NOT": """\
LOAD R1, 12     ; binary 1100
LOAD R2, 10     ; binary 1010
AND R1, R2      ; 1000 = 8
OR R1, 1        ; 1001 = 9
NOT R2          ; flips every bit
HLT
""",
    "4. STORE then LOAD": """\
LOAD R1, 42
STORE R1, 150
LOAD R2, [150]  ; read it back from RAM
HLT
""",
    "5. Compare": """\
LOAD R1, 7
LOAD R2, 9
CMP R1, R2      ; 7 < 9, so ACC = -1
HLT
""",
    "6. JMP skips an instruction": """\
LOAD R1, 1
JMP 103
LOAD R1, 99     ; skipped
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
LOAD R1, 5
STORE R1, 999
HLT
""",
}
DEFAULT_SAMPLE = "1. Add two numbers"
