import pygame
#import NPCs
NPCs = ['Arthur','Dean','James','Rowan','Lemonie','Olex']

def show_NPC_hitboxes():
    for NPC in NPCs:
        print(f'{NPC}: ({NPC.x},{NPC.y})')