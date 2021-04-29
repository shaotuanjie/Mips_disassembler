#!/usr/bin/python3
#-*- coding: utf-8 -*-
# 
# author: Shao tuanjie

# a MIPS - assembly language disassembler.

# ◼ Input
# ❖ Input file name is given by the first command-line argument
# ❖ You can assume that the maximum length of the input file name is 255

# ◼ Output
# ❖ Read the binary file named <filename> and prints the disassembled instruction
# ❖ Each line prints in the following format
#inst <instruction number>: <32-bit binary code in hex format> <disassembled instruction>


import sys

# Dictionary for the opcodes
# 0 and 1 have special meaning and do not directly define the function
opcodes = {
	0:"rtyp",
	1:"branch",
	2:"j", #
	3:"jal", #

	4:"beq", # I type
	5:"bne", # 
	#6:"blez",
	#7:"bgtz",
	8:"addi", #
	9:"addiu", #
    10:"slti", # slti rt, rs, constant   if (rs < constant) rt = 1; else rt = 0;
	11:"sltiu",#
	12:"andi", #
	13:"ori", #
	14:"xori", #

	15:"lui", #Load upper immediate

	32:"lb", #
	33:"lh", #
	35:"lw", #
	36:"lbu", #
	37:"lhu", #
	40:"sb", #
	41:"sh", #
	43:"sw" #
	}

# if we have a r-type instruction (opcode 0), we need the function codes to decode the functions
fcodes = { 
	0:"sll",  #shift left
	2:"srl",  #shift right
	3:"sra", # Shift right arithmetic – extend the sign bit

	4:"sllv", # Similar to sll/srl, but the shift amount comes from $rs[4:0]
	6:"srlv", # 
	7:"srav",  #

	8:"jr",   # Jump Register
	9:"jalr",  #Jump And Link Register

	12:"syscall", #
	#13:"break",
	16:"mfhi", # Move the multiplication result in the HI register to $d
	17:"mthi", # move to Hi
	18:"mflo", #mflo $d : Move the multiplication result in the LO register to $d
	19:"mtlo", # move to Lo

	24:"mult", #multiply
	25:"multu", #multiply unsigned
	26:"div", #
	27:"divu", #divide unsigned

	32:"add",  #
	33:"addu", #
	34:"sub", #
	35:"subu", #

	36:"and", # bitwise and
	37:"or", # bitwise or
	38:"xor", #bitwwise or
	39:"nor", # bitwise not
	42:"slt", #
	43:"sltu" #
	}

# List of registernumbers 
registers = {
	0:"$0",
	1:"$1",
	2:"$2",
	3:"$3",
	4:"$4",
	5:"$5",
	6:"$6",
	7:"$7",
	8:"$8",
	9:"$9",
	10:"$10",
	11:"$11",
	12:"$12",
	13:"$13",
	14:"$14",
	15:"$15",
	16:"$16",
	17:"$17",
	18:"$18",
	19:"$19",
	20:"$20",
	21:"$21",
	22:"$22",
	23:"$23",
	24:"$24",
	25:"$25",
	26:"$26",
	27:"$27",
	28:"$28",
	29:"$29",
	30:"$30",
	31:"$31"
}



# Masks for getting the different parts out of the machinecode, by and'ing the code with the mask and shifting back
rTypeMasks = {
	"opcode":0b11111100000000000000000000000000,
	"rs"    :0b00000011111000000000000000000000,
	"rt"    :0b00000000000111110000000000000000,
	"rd"    :0b00000000000000001111100000000000,
	"shamd" :0b00000000000000000000011111000000,
	"funct" :0b00000000000000000000000000111111}

iTypeMasks = {
	"opcode":0b11111100000000000000000000000000,
	"rs"    :0b00000011111000000000000000000000,
	"rt"    :0b00000000000111110000000000000000,
	"imm"	:0b00000000000000001111111111111111}
jTypeMasks = {
	"opcode":0b11111100000000000000000000000000,
	"addr"	:0b00000011111111111111111111111111}

# disassemble(32-bit int instruction) -> Instruction (string)

def zk(zahl): # 16 bit immedieates, calculate 2-compliment
	msb = zahl >> 15 # most significant bit, indicates if negative or positive
	if(msb==0):
		return zahl
	else:
		return -2**16 + ((zahl << 1) >> 1)


def disassemble(instruction):
	a = instruction
	opcode = (a & 0b11111100000000000000000000000000) >> (32-6) #get opcode

	if opcode not in opcodes:
		return "unknown instruction"
	elif (opcode == 0): # Rtype instruction
		fcode = a & rTypeMasks["funct"] # get functioncode
		#print("fcode is ", fcode)
		if fcode not in fcodes:
			return "unknown instruction"
		else:
			rs = registers[(a & rTypeMasks["rs"]) >> 21]
			rt = registers[(a & rTypeMasks["rt"]) >> 16]
			rd = registers[(a & rTypeMasks["rd"]) >> 11]
			if(fcode==0 or fcode==2 or fcode==3): # shift instructions
				shamd = (a & rTypeMasks["shamd"]) >> 6
				return fcodes[fcode] + " " + rd + ", " + rt + ", " + str(shamd)
			elif(fcode==4 or fcode==6 or fcode==7):
				return fcodes[fcode] + " " + rd + ", " + rt + ", " + rs
			elif(fcode==8): # jr
				return fcodes[fcode] + " " + rs
			elif(fcode==9):#jalr
				return fcodes[fcode] + " " + rd + ", " + rs
			elif(fcode==12 ):#syscall
				return fcodes[fcode]
			elif(fcode==16 or fcode == 18):
				# mfhi,mflo
				return fcodes[fcode] + " " + rd
			elif(fcode==17 or fcode == 19):
				# mthi, mtlo
				return fcodes[fcode] + " " + rs
			elif(fcode==24 or fcode==25 or fcode==26 or fcode==27): # mult(u) and div(u)
				return fcodes[fcode] + " " + rs + ", " + rt
			else:
				return fcodes[fcode] + " " + rd + ", " + rs + ", " + rt
				

	elif (opcode == 2 or opcode == 3):
		# j/jal j-type instructions
		addr = (a & jTypeMasks["addr"]) 
		return opcodes[opcode] + " " + str(addr)
	elif (opcode == 15): # lui  (load upper immediate)
		rt  = registers[(a & iTypeMasks["rt"]) >> 16]
		imm = (a & iTypeMasks["imm"])
		return opcodes[opcode] + " " + rt + ", " + str(zk(imm))
	elif (opcode == 32 or opcode ==33 or opcode == 35 or opcode==36 or opcode==37 or opcode==41 or opcode == 40 or opcode== 43): # lb lw lh lw  lbu lhu  sb sb sw
		rt = registers[(a & 0b00000000000111110000000000000000) >> 16]
		rs = registers[(a & 0b00000011111000000000000000000000) >> 21]
		imm = (a & iTypeMasks["imm"])
		return opcodes[opcode] + " " + rt + ", " + str(zk(imm)) + "(" + rs + ")"
		# if(imm>=0x8000):
		# 	return  opcodes[opcode] + " " + rt + ", " + str(hex(imm)) + "(" + rs + ")"
		# else:
		# 	return opcodes[opcode] + " " + rt + ", " + str(zk(imm)) + "(" + rs + ")"
	
	else: #I_type
		rs  = registers[(a & iTypeMasks["rs"]) >> 21]
		rt  = registers[(a & iTypeMasks["rt"]) >> 16]
		imm = (a & iTypeMasks["imm"]) 
		if (opcode==4 or opcode==5): #beq/bne rs, rt, L1
			return opcodes[opcode] + " " + rs + ", " + rt + ", " + str(zk(imm))

		return opcodes[opcode] + " " + rt + ", " + rs + ", " + str(zk(imm))


def main():
	with open(sys.argv[1], 'rb') as f:
		content = f.read()
		n_fold = int(len(content) / 4)
		for i in range(n_fold):
			s = (content[0+4*i] << 24) + (content[1+4*i] << 16) + (content[2+4*i]<<8) + content[3+4*i]
			instruc_num = ("%08x" % s)
			print("inst "+str(i)+": " + instruc_num +" "+ disassemble(s))
	
	
		

if __name__=='__main__':
	main()



