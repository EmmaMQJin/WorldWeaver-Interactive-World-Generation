import json
import os
import tempfile
import subprocess

def open_vim_with_string(text):
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as temp_file:
        temp_file.write(text)
    subprocess.run(['vim', temp_file.name])

    with open(temp_file.name, 'r') as edited_file:
        edited_text = edited_file.read()
    os.unlink(temp_file.name)

    return edited_text

def open_vim_with_json(json_data):
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
        json.dump(json_data, temp_file, indent=4)
        temp_file.flush()
    subprocess.run(['vim', temp_file.name])
    with open(temp_file.name, 'r') as edited_file:
        try:
            edited_json = json.load(edited_file)
        except json.JSONDecodeError:
            print("Edited data is not valid JSON.")
            return None
    os.unlink(temp_file.name)
    return edited_json

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
    for i, obj in enumerate(data):
        temp_path = f"data/test_generations/obj{i}.json"
        with open(temp_path, 'w') as tempfile:
            json.dump(obj, tempfile, indent=4)

    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)


def extract_keys_from_list(list_json_objs, key):
    to_return = []
    for json_obj in list_json_objs:
        to_return.append(json_obj[key])
    return to_return