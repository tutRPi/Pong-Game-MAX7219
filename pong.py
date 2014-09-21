#!/usr/bin/python
# ----------------------------------------
# 
# 
# You can find an introduction (german) here:
# 
# ----------------------------------------
# It is important to set MATRIX_WIDTH and 
# MATRIX_HEIGHT in the multilineMAX7219.py
# file. You can get it here:
# https://github.com/tutRPi/multilineMAX7219
# ----------------------------------------
# How to connect Joystick
# ----------------------------------------
# RaspberryPi 	MCP3008
# Pin 1 (3.3V) 	Pin 16 (VDD)
# Pin 1 (3.3V) 	Pin 15 (VREF)
# Pin 6 (GND) 	Pin 14 (AGND)
# Pin 23 (SCLK)	Pin 13 (CLK)
# Pin 21 (MISO)	Pin 12 (DOUT)
# Pin 19 (MOSI)	Pin 11 (DIN)
# Pin 26 (CE1) 	Pin 10 (CS/SHDN)
# Pin 6 (GND) 	Pin 9 (DGND)
#
# 	RPi/MCP3008 			Joystick
# Raspberry Pin 6 (GND) 	GND
# Raspberry Pin 1 (3.3V) 	+5V
# MCP3008 Pin 3 (CH2) 		VRy
#
# ----------------------------------------
# How to connect MAX7219 Matrices
# ----------------------------------------
# RaspberryPi 			MAX7219 LED Matrix
# Pin 2 (5V0)			VCC
# Pin 6 (GND)			GND
# Pin 19 (GPIO10/MOSI)	DIN
# Pin 24 (GPIO8/ CS0)	CS
# Pin 23 (GPIO11/SCLK)	CLK

import spidev
import time
import sys
from math import floor, ceil
import multilineMAX7219 as LEDMatrix # from https://github.com/tutRPi/multilineMAX7219
from multilineMAX7219 import GFX_ON, GFX_OFF
from random import uniform, random, choice

# Define board width (in dots)
board_height = 4

# Define Channels (channel 1,2 and 3-7 are free)
vry_channel = 2

# Computer's speed (the lower it is, the easier to win)
# between 0 and 1 (1 will make it impossible to win)
cpu_speed = 0.8

delay_time = 0.04
dot = [0,0] # x,y
dot_dir = [choice([-2/3.0, -3/4.0, -4/5.0, -1.0]), uniform(0.85, 1) * choice([0.5, -0.5])]

points = [0,0]
LEDNumbers = [[],[],[],[],[],[],[],[],[],[]]
LEDNumbers[0] = [[0,1,1,1,1,1,0],[1,0,0,0,0,0,1],[1,0,0,0,0,0,1],[0,1,1,1,1,1,0],[0,0,0,0,0,0,0]]
LEDNumbers[1] = [[1,0,0,0,0,1,0],[1,1,1,1,1,1,1],[1,0,0,0,0,0],[0,0,0,0,0,0,0]]
LEDNumbers[2] = [[1,1,0,0,0,1,0],[1,0,1,0,0,0,1],[1,0,0,1,0,0,1],[1,0,0,0,1,1,0],[0,0,0,0,0,0,0]]
LEDNumbers[3] = [[0,1,0,0,0,1,0],[1,0,0,1,0,0,1],[1,0,0,1,0,0,1],[0,1,1,1,1,1,0],[0,0,0,0,0,0,0]]
LEDNumbers[4] = [[0,0,0,1,1,1,1],[0,0,0,1,0,0,0],[0,0,0,1,0,0,0],[1,1,1,1,1,1,1],[0,0,0,0,0,0,0]]
LEDNumbers[5] = [[0,1,0,0,1,1,1],[1,0,0,1,0,0,1],[1,0,0,1,0,0,1],[0,1,1,0,0,0,1],[0,0,0,0,0,0,0]]
LEDNumbers[6] = [[0,1,1,1,1,1,0],[1,0,0,1,0,0,1],[1,0,0,1,0,0,1],[0,1,1,0,0,0,1],[0,0,0,0,0,0,0]]
LEDNumbers[7] = [[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[1,1,1,1,0,0,1],[0,0,0,0,1,1,1],[0,0,0,0,0,0,0]]
LEDNumbers[8] = [[0,1,1,0,1,1,0],[1,0,0,1,0,0,1],[1,0,0,1,0,0,1],[0,1,1,0,1,1,0],[0,0,0,0,0,0,0]]
LEDNumbers[9] = [[0,0,0,0,1,1,0],[1,0,0,1,0,0,1],[1,0,0,1,0,0,1],[0,1,1,1,1,1,0],[0,0,0,0,0,0,0]]
LED_colon = [[0,0,1,0,1,0,0],[0,0,0,0,0,0,0]]

spiMax7219 = spidev.SpiDev()
spiMax7219.open(0,0)
spiJoystick = spidev.SpiDev()
spiJoystick.open(0,1)

board_position_bottom = round( 8*LEDMatrix.MATRIX_HEIGHT/2 - board_height / 2 )
cpu_position_bottom = board_position_bottom # computer


def readCH(ch):
	val = spiJoystick.xfer2([1,(8+ch)<<4,0])
	data = ((val[1]&3) << 8) + val[2]
	return data
  
def move():
	global board_position_bottom
	mv_y = readCH(vry_channel)
	mv = 0
	# to avoid small variances
	if mv_y > 530 or mv_y < 500:
		mv = ((mv_y+1) - 512) / -float(512)
	board_position_bottom = min( max(0, board_position_bottom + mv ), 8*LEDMatrix.MATRIX_HEIGHT - board_height )
	LEDMatrix.gfx_line( 8*LEDMatrix.MATRIX_WIDTH-1, int(round(board_position_bottom)), 8*LEDMatrix.MATRIX_WIDTH-1, int(round(board_position_bottom)) + board_height-1 , GFX_ON)
	
def moveCPU():
	global cpu_position_bottom
	# towards player
	if dot_dir[0] > 0:
		cpu_position_bottom = min(max(0, cpu_position_bottom + dot_dir[1]*0.5), 8*LEDMatrix.MATRIX_HEIGHT - board_height)
	# towards cpu
	else:
		if dot[1] > (cpu_position_bottom + board_height):
			cpu_position_bottom = min(max(0, cpu_position_bottom + cpu_speed), 8*LEDMatrix.MATRIX_HEIGHT - board_height)
		elif dot[1] < (cpu_position_bottom):
			cpu_position_bottom = min(max(0, cpu_position_bottom - cpu_speed), 8*LEDMatrix.MATRIX_HEIGHT - board_height)
	LEDMatrix.gfx_line( 0, int(round(cpu_position_bottom)), 0, int(round(cpu_position_bottom)) + board_height-1 , GFX_ON)

def movePong():
	global delay_time, dot_dir
	# top / bottom
	if dot[1] + dot_dir[1] > 8*LEDMatrix.MATRIX_WIDTH-1 or dot[1] + dot_dir[1] < 0:
		dot_dir[1] = - dot_dir[1]
	# cpu side
	if dot[0] + dot_dir[0] < 1:
		if round(dot[1] + dot_dir[1]) >= round(cpu_position_bottom) and round(dot[1] + dot_dir[1]) <= round(cpu_position_bottom) + board_height:
			dot_dir[0] = - dot_dir[0]
			dot_dir[1] = choice([uniform(0.3, 0.55), uniform(-0.55, -0.3)])
			delay_time = max(0.03, delay_time - 0.01)
		else:
			dot[0] = 1
			dot[1] = int(round(8*LEDMatrix.MATRIX_HEIGHT/2))
			dot_dir = [choice([2/3.0, 3/4.0, 4/5.0, 1.0]), uniform(0.85, 1) * choice([0.5, -0.5])]
			points[1] += 1
			setPoints()
			return
	# user side
	elif dot[0] + dot_dir[0] > 8*LEDMatrix.MATRIX_WIDTH - 2:
		if round(dot[1] + dot_dir[1]) >= round(board_position_bottom) and round(dot[1] + dot_dir[1]) <= round(board_position_bottom) + board_height:
			dot_dir[0] = - dot_dir[0]
			dot_dir[1] = choice([uniform(0.3, 0.55), uniform(-0.55, -0.3)])
			delay_time = max(0.03, delay_time - 0.01)
		else:
			dot[0] = 8*LEDMatrix.MATRIX_WIDTH-2
			dot[1] = int(round(8*LEDMatrix.MATRIX_HEIGHT/2))
			dot_dir = [choice([-2/3.0, -3/4.0, -4/5.0, -1.0]), uniform(0.85, 1) * choice([0.5, -0.5])]
			points[0] += 1
			setPoints()
			return
	dot[0] = dot[0] + dot_dir[0]
	dot[1] = dot[1] + dot_dir[1]
	LEDMatrix.gfx_set_px(int(round(dot[0])), int(round(dot[1])), GFX_ON)
	
def setPoints():
	global board_position_bottom, cpu_position_bottom
	if (points[0] < 10 and points[1] < 10):
		board_position_bottom = round( 8*LEDMatrix.MATRIX_HEIGHT/2 - board_height / 2 )
		cpu_position_bottom = board_position_bottom
		LEDMatrix.gfx_set_all(GFX_OFF)
		display = LEDNumbers[points[0]] + LED_colon + LEDNumbers[points[1]]
		LEDMatrix.gfx_sprite_array(display, int((LEDMatrix.MATRIX_WIDTH*8 - len(display))/2), int( LEDMatrix.MATRIX_HEIGHT*4 - 4 ) )
		LEDMatrix.gfx_render()
		time.sleep(1)
	else:
		print "Game over: %d - %d" % (points[0], points[1])
		LEDMatrix.gfx_set_all(GFX_OFF)
		if points[0] >= 10:
			sign = [[1,1,1,1,1,1,1],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,1,1,1,1,1,0],[1,0,0,0,0,0,1],[1,0,0,0,0,0,1],[0,1,1,1,1,1,0],[0,0,0,0,0,0,0],[1,0,0,1,1,1,1],[1,0,0,1,0,0,1],[1,1,1,1,0,0,1],[0,0,0,0,0,0,0],[0,0,0,0,0,0,1],[1,1,1,1,1,1,1],[0,0,0,0,0,0,1]]
			LEDMatrix.gfx_sprite_array(sign, int((LEDMatrix.MATRIX_WIDTH*8 - len(sign))/2), int( LEDMatrix.MATRIX_HEIGHT*4 - 4 ) )
		else:
			sign = [[0,1,1,1,1,1],[1,0,0,0,0,0],[0,1,1,1,0,0],[1,0,0,0,0,0],[0,1,1,1,1,1],[0,0,0,0,0,0],[1,1,1,1,1,1],[0,0,0,0,0,0],[1,1,1,1,1,1],[0,0,0,1,1,0],[0,0,1,0,0,0],[1,1,0,0,0,0],[1,1,1,1,1,1],[0,0,0,0,0,0],[1,0,1,1,1,1]]
			LEDMatrix.gfx_sprite_array(sign, int((LEDMatrix.MATRIX_WIDTH*8 - len(sign))/2), int( LEDMatrix.MATRIX_HEIGHT*4 - 3 ) )
		LEDMatrix.gfx_render()
		sys.exit(0)
		
if __name__ == "__main__":
	board_height = min(max(2, board_height), 8*LEDMatrix.MATRIX_HEIGHT -2)
	dot[0] = 8*LEDMatrix.MATRIX_WIDTH-2
	dot[1] = int(round(8*LEDMatrix.MATRIX_HEIGHT/2))
	#time.sleep(delay_time)
	while True:
		LEDMatrix.gfx_set_all(GFX_OFF)
		move()
		moveCPU()
		movePong()
		
		LEDMatrix.gfx_render()
		time.sleep(delay_time)
		
	