import binascii
import re
import struct
import os
import codecs
import sys
import time

configs = []
f = open("C:\Games\Downloads\ec_patch_2038-2041.cup.decoded\element\data\elements.data", 'rb')
cfg = open("C:\Games\pwTools\pwtools-svn-bin\sELedit\configs\PW_1.5.5_v156.cfg", 'r')

num_group = int(cfg.readline())
raw_tree = int(cfg.readline())

cur_group = 0
configs = []
line = cfg.readline()
while line and cur_group < num_group:
	if len(line.strip()) == 0:
		line = cfg.readline()
		continue
	config = []
	config.append(line.strip())
	config.append(cfg.readline().strip())
	config.append(cfg.readline().strip())
	config.append(cfg.readline().strip())

	configs.append(config)
	line = cfg.readline()
	cur_group += 1

fieldOperators = {
	'int32' : lambda f, x: struct.unpack('<i', f.read(4))[0],
	'float' : lambda f, x: struct.unpack('<f', f.read(4))[0],
	'wstring' : lambda f, x: struct.unpack(str(x)+'s', f.read(x))[0].decode('utf16').split('\0',1)[0],
	'string' : lambda f, x: struct.unpack(str(x)+'s', f.read(x))[0].split('\0',1)[0],#.decode('GB18030'),
	'byte' : lambda f, x: f.read(x),
}


f.seek(8, os.SEEK_CUR)

def scanTalk(f, talk_count):
	dialogs = []
	for i in xrange(talk_count):
		dialog = [0, '', []]
		dialog[0] = struct.unpack('<i', f.read(4))[0] #id
		dialog[1] = struct.unpack('128s', f.read(128))[0].decode('utf16').split('\0',1)[0] #name
		question_count = struct.unpack('<i', f.read(4))[0]
		for j in range(question_count):
			question = [0, 0, '', []]
			question[0] = struct.unpack('<i', f.read(4))[0] #ID
			question[1] = struct.unpack('<i', f.read(4))[0] #Control
			text_len = struct.unpack('<i', f.read(4))[0]
			question[2] = struct.unpack(str(text_len*2)+'s', f.read(text_len*2))[0].decode('utf16').split('\0',1)[0]
			choice_count = struct.unpack('<i', f.read(4))[0]
			for k in range(choice_count):
				choice = [0, '']
				choice[0] = struct.unpack('<i', f.read(4))[0] #Control
				choice[1] = struct.unpack('132s', f.read(132))[0].decode('utf16').split('\0',1)[0]
				question[3].append(choice)
			dialog[2].append(question)
		dialogs.append(dialog)
	return ('', dialogs)
		

cur_auto = 0
entries = {}
for config in configs:
	if config[1] == "AUTO":
			while True:
				count = struct.unpack('<i', f.read(4))[0]
				idx = struct.unpack('<i', f.read(4))[0]
				if (count & 0xFFFF0000) or (idx & 0xFFFF0000):
					f.seek(-7, 1)
				else:
					f.seek(-8, 1)
					break
	elementCount = struct.unpack('<i', f.read(4))[0]
	print "Scanning", config[0], elementCount
	elements = []
	if config[2] == "RAW":
		entries['NPC TALK'] = scanTalk(f, elementCount)
	else:	
		names = config[2].split(';')
		fields = config[3].split(';')
		for i in xrange(elementCount):
			element = []
			for field in fields:
				arg = ''
				if ':' in field:
					field, arg = field.split(":")
					arg = int(arg)
				element.append(fieldOperators[field](f, arg))		
			elements.append(element)
		entries[config[0]] = (names, elements)
		
output = open("output.txt", "w")

icons = []
for config in entries:
	names, elements = entries[config]
	if 'file_icon' in names:
		icons.extend([(x[names.index('ID')], x[names.index('file_icon')].split('\\')[-1]) for x in elements if len(x[names.index('file_icon')]) > 0])
		
output.write('\n'.join([str(x[0])+','+x[1] for x in icons]))

import pygame
START_FROM = 51023
for sex in ['f', 'm']:
	icon_sheet = pygame.image.load('C:\Games\Downloads\ec_patch_2038-2041.cup.decoded\element\surfaces\iconset\iconlist_ivtr'+sex+'.bmp')
	current_icon_index = 0
	icon_map = {}
	icon_sheet_index = open('C:\Games\Downloads\ec_patch_2038-2041.cup.decoded\element\surfaces\iconset\iconlist_ivtr'+sex+'.txt')
	icon_height = int(icon_sheet_index.readline())
	icon_width = int(icon_sheet_index.readline())
	icon_sheet_height = int(icon_sheet_index.readline())
	icon_sheet_width = int(icon_sheet_index.readline())
	line = icon_sheet_index.readline()
	while line:
		icon_map[line.strip()] = current_icon_index
		current_icon_index += 1
		line = icon_sheet_index.readline()
		
	for icon in icons:
		if icon[0] < START_FROM:
			continue
		if icon[1] not in icon_map:
			continue
		location = icon_map[icon[1]]
		if location > -1:
			y,x = divmod(location, icon_sheet_width)
			icon_surface = pygame.Surface((icon_width,icon_height))
			icon_surface.blit(icon_sheet, (x*-icon_width, y*-icon_height))
			pygame.image.save(icon_surface, sex+"\\"+str(icon[0])+".bmp")