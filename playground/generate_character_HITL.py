from generate_characters import *
import json
import os
import subprocess

def read_file_to_str(filepath):
    to_return = ""
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        file.close()
    to_return = ''.join(lines)
    return to_return.strip()


def read_json_examples(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        example_jsons = json.load(file)
    return example_jsons


def dict_to_json_file(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)


def list_to_json_file(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)


def extract_keys_from_list(list_json_objs, key):
    to_return = []
    for json_obj in list_json_objs:
        to_return.append(json_obj[key])
    return to_return

def edit_character_in_vim(character_data):
    """Opens Vim to allow the user to edit the character JSON data."""
    filename = 'temp_character.json'
    with open(filename, 'w') as file:
        json.dump(character_data, file, indent=4)

    subprocess.run(['vim', filename])

    with open(filename, 'r') as file:
        edited_character = json.load(file)

    os.remove(filename) 
    return edited_character

def human_in_loop_interaction(story, directory):
    approved_characters = []
    while True:
        new_character = promptGPT(story, directory)
        
        # Open the new character in Vim for editing
        edited_character = edit_character_in_vim(new_character)
        
        # Show the edited character and ask for approval
        print(json.dumps(edited_character, indent=4))
        user_input = input("Do you approve this character? (yes/no/stop): ").lower().strip()
        approved_characters=[]
        if user_input == "yes":
            approved_characters.append(edited_character)
            # Save immediately if approved
            with open(directory+"data/approved_characters.json", "w" if os.path.exists(directory+"data/approved_characters.json") else "w") as file:
                json.dump(approved_characters, file, indent=4)
                file.write('\n')  # Ensure newline for JSON arrays on subsequent entries
            print("Character approved and added.")
        elif user_input == "stop":
            print("Process stopped by user.")
            break
        
        new_npcs = generate_npc(story, directory)
        edited_npc_character = edit_character_in_vim(new_npcs)
        approved_npc_characters = []
        user_input = input("Do you approve these NPC characters? (yes/no/stop): ").lower().strip()

        if user_input == "yes":
            approved_npc_characters.append(edited_npc_character)
            # Save immediately if approved
            with open(directory+"data/approved_NPC_characters.json", "a" if os.path.exists(directory+"data/approved_NPC_characters.json") else "w") as file:
                json.dump(approved_npc_characters, file, indent=4)
                file.write('\n')  # Ensure newline for JSON arrays on subsequent entries
            print("NPC Character approved and added.")
        elif user_input == "stop":
            print("Process stopped by user.")
            break


# Usage
directory = ''  # 
stories = []
stories.append(read_file_to_str(directory+"data/story-rapunzel.txt"))
stories.append(read_file_to_str(directory+"data/story-cyberpunk.txt"))
stories.append(read_file_to_str(directory+"data/story-insidetemple.txt"))
human_in_loop_interaction(stories, directory)
