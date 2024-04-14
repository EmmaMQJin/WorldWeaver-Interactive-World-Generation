from generate_locations import *



def generate_all_locations(desc):
    central_loc_desc = input("Do you have any thoughts on what the central location is like?\n")
    







print("Welcome to WorldWeaver!")

desc = input("Please give a description of the type of game you want to build.\n")

choice = input("Would you like to start with generating locations or characters for your game?\n")

if choice.lower() == "location":
    generate_all_locations(desc)