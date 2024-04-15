from generate_locations import *
import tempfile
import subprocess

def open_vim_with_string(text):
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as temp_file:
        # Write the string to the temporary file
        temp_file.write(text)

    # Open the temporary file in Vim
    subprocess.run(['vim', temp_file.name])

    # Read the edited string from the temporary file
    with open(temp_file.name, 'r') as edited_file:
        edited_text = edited_file.read()

    # Delete the temporary file
    # Remove the temporary file
    import os
    os.unlink(temp_file.name)

    return edited_text


def generate_all_locations(desc, examples):
    # generate central location with user input
    central_loc_desc = input("Do you have any thoughts on what the central location is like?\n")
    all_descs = desc
    if central_loc_desc:
        all_descs += "\nAbout the central location of the game: " + central_loc_desc
    loc_center = generate_new_location(all_descs, examples)
    
    # get feedback from user about central location
    print("OK, here is the generated central location:")
    # print("Name: ", loc_center["name"])
    # print("Description: ", loc_center["description"])
    new_name = open_vim_with_string(loc_center["name"])
    print("Edited name: ", new_name)
    new_desc = open_vim_with_string(loc_center["description"])
    print("Edited description: ", new_desc)
    loc_center["name"] = new_name
    loc_center["description"] = new_desc

    dict_to_json_file(loc_center, "test_generations/init_location.json")







story_desc = read_file_to_str("data/story-cyberpunk.txt")
location_init_examples = read_json_examples("data/locations-name-desc-4.json")
location_init_story_insidetemple = read_file_to_str("data/story-insidetemple.txt")
location_init_story_lake = read_file_to_str("data/story-lake.txt")
location_neib_prompt_example = read_json_examples("data/location-name-desc-1.json")
location_neibs_example_lake = read_json_examples("data/locations.name-desc-lake.json")

print("Welcome to WorldWeaver!")

# desc = input("Please give a description of the type of game you want to build.\n")

choice = input("Would you like to start with generating locations or characters for your game?\n")

if choice.lower() == "location":
    generate_all_locations(story_desc, location_init_examples)