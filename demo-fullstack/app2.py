from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from random import randint

from backend.utils.utils import *
from backend.utils.json_utils import *
from backend.utils.frontend_utils import *
from backend.utils.generate_actions_utils import *
from backend.utils.generate_blocks_utils import *
from backend.utils.generate_locations_utils import *
from backend.utils.generate_characters_utils import *
from backend.utils.generate_items_utils import *
from backend.utils.generate_game_json import *

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Global variable to hold character data
main_character = {
    "name": "Unknown",
    "description": "No character has been created yet."
}
story_cyberpunk = read_file_to_str("data/story-cyberpunk.txt")
story_insidetemple = read_file_to_str("data/story-insidetemple.txt")
story_lake = read_file_to_str("data/story-lake.txt")

location_format = read_json_examples(
    "data/location-empty.json")

stories = [story_cyberpunk, story_insidetemple]
with open("data/few-shot-examples/example-characters.json", 'r') as file:
    example_characters = json.load(file)
character_format = read_file_to_str("data/character-empty.json")

central_loc_lake_obj = read_json_examples(
    "data/few-shot-examples/central-loc-lake.json")
neib_locs_lake_5_list = read_json_examples(
    "data/few-shot-examples/neighb-locs-lake-5.json")
central_loc_insidetemple_obj = read_json_examples(
    "data/few-shot-examples/central-loc-insidetemple.json")
neib_locs_insidetemple_3_list = read_json_examples(
    "data/few-shot-examples/neighb-locs-insidetemple-3.json")

hall_of_goddess_obj = read_json_examples("data/few-shot-examples/hall-of-goddess.json")
royal_tomb_obj = read_json_examples("data/few-shot-examples/royal-tomb.json")

# few-shot for central location format
central_loc_shot_1 = create_new_location_shot(story_insidetemple, central_loc_insidetemple_obj)
central_loc_shot_2 = create_new_location_shot(story_lake, central_loc_lake_obj)
central_loc_shots = central_loc_shot_1 + central_loc_shot_2

# few-shot for neighboring locations
neib_locs_shot_1 = create_neib_locs_shot(
    central_loc_insidetemple_obj, story_insidetemple, 1, neib_locs_insidetemple_3_list[:1])
neib_locs_shot_2 = create_neib_locs_shot(
    central_loc_insidetemple_obj, story_insidetemple, 3, neib_locs_insidetemple_3_list)
neib_locs_shot_3 = create_neib_locs_shot(
    central_loc_lake_obj, story_lake, 5, neib_locs_lake_5_list)
neib_locs_shots = neib_locs_shot_1 + neib_locs_shot_2 + neib_locs_shot_3

# few-shot for connections
hall_tomb_connection = [{"direction": "down",
                            "travel description": "Descending the stairs from the Hall of the Goddess, you move towards the Royal Tomb, the air growing cooler and heavier with the weight of centuries."},
                        {"direction": "up",
                            "travel description": "Ascending the stairs from the depths of the Royal Tomb, you journey back towards the Hall of the Goddess. With each step upwards, the air becomes lighter and warmer, shedding the cool, heavy presence of ancient history. The atmosphere subtly shifts, as if leaving behind the echoes of the past to embrace the divine serenity of the Goddess's hall."}]
connections_shot_1 = create_connections_shot(hall_of_goddess_obj, royal_tomb_obj, hall_tomb_connection)
connections_shots = connections_shot_1

# all_characters = read_json_examples("data/test_generations/all_the_characters.json")
all_characters = []
all_locations = read_json_examples("data/test_generations/all_the_locations.json")

with open(f"data/extracted_items.json", 'r') as file:
    extracted_items = json.load(file)

sample_items_inventory = json.dumps(extracted_items[2:4]+extracted_items[5:6]+extracted_items[11:12]+extracted_items[15:16], indent=4)
sample_items_objects = json.dumps(extracted_items[5:10], indent=4)

locations_to_use = {
    "Fairy King's Throne": "Starting location. A humble abode located in a tucked away crevice of a towering building. This is also where the pigeon returns to eat its precious pizza slice.",
    "Jerry's Cage": "A large open area where the pigeon must avoid branches while in flight. Also the return point after the pizza has been stolen.",
    "Streetlamp Overlook": "An elevated spot where the pigeon lands to scout for food sources.",
    "Busy City Streets": "A bustling area the pigeon must navigate to avoid pedestrians while flying towards Costco.",
    "Costco": "A location full of potential food sources. Here is where the pigeon spots the delectable pizza and attempts to steal a slice.",
    "Costco Eating Area": "A site of human activity where the pigeon must cunningly mimic human actions to steal a slice of pizza, dodge angry customers, and take off."
}

winning_state = "main character steals breakfast from costco"
background_story = ""

already_generated_items = []
all_selected_items = []

@app.get("/npc-generation")
def start_npcs(request: Request):
    # Redirects to the start inventory with a default location_index of 0
    return RedirectResponse(url="/npc-generation/0", status_code=303)

@app.get("/npc-generation/{location_index}")
async def display_npcs(request: Request, location_index: int):
    # Start with the first character and reset the global variables
    global already_generated_items, all_selected_items, generated_in_round
    location = all_locations[location_index]
    loc_name = location["name"]
    generated_in_round = []
    purpose = locations_to_use[loc_name]
    items = generate_npcs_round(loc_name, location["description"], purpose, background_story,
                                            main_character, already_generated_items)
    already_generated_items.extend(items)
    generated_in_round.extend(items)
    context = {"request": request, "items": items, "location_index": location_index, "loc_name": loc_name}
    return templates.TemplateResponse("npcs_selection.html", context)


@app.post("/npc-generation/{location_index}/select")
async def select_npcs(request: Request, location_index: int, selected_items: list = Form(...)):
    global all_selected_items, generated_in_round
    selected_items_json = []
    for _, num in enumerate(selected_items):
        selected = generated_in_round[int(num.strip())]
        print("selected: ", selected)
        selected_items_json.append(selected)
    all_selected_items.extend(selected_items_json)
    generated_in_round = []
    return await display_npcs(request, location_index)


@app.get("/npc-generation/{location_index}/regenerate")
async def regenerate_npcs(request: Request, location_index: int, ):
    return await display_npcs(request, location_index)


@app.get("/npc-generation/{location_index}/final_selection")
async def final_selection_npcs(request: Request, location_index: int):
    global all_selected_items, already_generated_items, all_locations
    next_location_id = location_index+1
    items_dict = {}
    for ind, item in enumerate(all_selected_items):
        key = item["name"]
        items_dict[key] = item

    all_selected_items = []
    already_generated_items = []
    all_locations[location_index]["characters"] = items_dict
    all_items = list(items_dict.values())
    dict_to_json_file(all_locations, "data/test_generations/all_the_locations.json")
    if location_index == len(all_locations) - 1:
        location_index = -1
        context = {"request": request, "locations": all_locations, "location_index": location_index }
        return templates.TemplateResponse("npcs_completion.html", context)
    return await display_npcs(request, next_location_id)


@app.get("/object-generation")
def start_objects(request: Request):
    # Redirects to the start inventory with a default location_index of 0
    return RedirectResponse(url="/object-generation/0", status_code=303)

@app.get("/object-generation/{location_index}")
async def display_items_objects(request: Request, location_index: int):
    # Start with the first character and reset the global variables
    global already_generated_items, all_selected_items, generated_in_round
    print("selected2: ", all_selected_items)
    generated_in_round = []
    location = all_locations[location_index]
    location_name = location["name"]
    items = populate_objects_in_location_round(location, locations_to_use, 
                                            sample_items_objects, already_generated_items)
    already_generated_items.extend(items)
    generated_in_round.extend(items)
    context = {"request": request, "items": items, "location_index": location_index, "loc_name": location_name}
    return templates.TemplateResponse("objects_item_selection.html", context)


@app.post("/object-generation/{location_index}/select")
async def select_items_objects(request: Request, location_index: int, selected_items: list = Form(...)):
    global all_selected_items, generated_in_round
    selected_items_json = []
    for _, num in enumerate(selected_items):
        selected = generated_in_round[int(num.strip())]
        selected_items_json.append(selected)
    all_selected_items.extend(selected_items_json)
    print("selected1: ", all_selected_items)
    generated_in_round = []
    return await display_items_objects(request, location_index)


@app.get("/object-generation/{location_index}/regenerate")
async def regenerate_items_objects(request: Request, location_index: int, ):
    return await display_items_objects(request, location_index)


@app.get("/object-generation/{location_index}/final_selection")
async def final_selection_obejcts(request: Request, location_index: int):
    global all_selected_items, already_generated_items, all_locations
    print("all selected items: ", all_selected_items)
    next_location_id = location_index+1
    items_dict = {}
    for ind, item in enumerate(all_selected_items):
        key = item["name"]
        items_dict[key] = item

    all_locations[location_index]["items"] = items_dict
    all_items = list(items_dict.values())
    dict_to_json_file(all_locations, "data/test_generations/all_the_locations.json")
    all_selected_items = []
    already_generated_items = []
    if location_index == len(all_locations) - 1:
        location_index = -1
        context = {"request": request, "locations": all_locations, "location_index": location_index}
        return templates.TemplateResponse("objects_completion.html", context)
    return await display_items_objects(request, next_location_id)


@app.get("/inventory-generation")
def start_inventory(request: Request):
    # Redirects to the start inventory with a default location_index of 0
    return RedirectResponse(url="/inventory-generation/0", status_code=303)

@app.get("/inventory-generation/{location_index}")
async def start_location_inventory(request: Request, location_index: int):
    # Start with the first character and reset the global variables
    global already_generated_items, all_selected_items
    already_generated_items = []
    all_selected_items = []
    return await display_items_inventory(request, location_index, 0)

@app.get("/inventory-generation/{location_index}/{character_id}")
async def display_items_inventory(request: Request, location_index: int, character_id: int):
    global already_generated_items, locations_to_use, winning_state, sample_items_inventory, all_locations, all_characters_in_loc, generated_in_round
    generated_in_round = []
    all_characters_in_loc_dict = all_locations[location_index]["characters"]
    all_characters_in_loc = list(all_characters_in_loc_dict.values())
    if (len(all_characters_in_loc) == 0):
        return RedirectResponse(url=f"/inventory-generation/{location_index+1}", status_code=303)

    character = all_characters_in_loc[character_id] # json object
    location = all_locations[location_index]

    location_name = location["name"]
    location_actions = locations_to_use.get(location_name, "No specific actions described.")
    location_items_names = [item for item in location["items"].keys()]
    location_items = json.dumps(location_items_names, indent=4)
    items = generate_inventory_items(character, main_character, winning_state, location_name, location_actions, 
                                     location_items, sample_items_inventory, already_generated_items)
    already_generated_items.extend(items)
    generated_in_round.extend(items)

    context = {"request": request, "items": items, "character_id": character_id, "location_index": location_index,
               "loc_name": location_name, "char_name": character["name"]}

    return templates.TemplateResponse("inventory_item_selection.html", context)


@app.post("/inventory-generation/{location_index}/{character_id}/select")
async def select_items_inventory(request: Request, location_index: int, character_id: int, selected_items: list = Form(...)):
    global all_selected_items, generated_in_round
    selected_items_json = []
    for _, num in enumerate(selected_items):
        selected = generated_in_round[int(num.strip())]
        print("selected: ", selected)
        selected_items_json.append(selected)
    all_selected_items.extend(selected_items_json)
    generated_in_round = []
    return await display_items_inventory(request, location_index, character_id)


@app.get("/inventory-generation/{location_index}/{character_id}/regenerate")
async def regenerate_items_inventory(request: Request, location_index: int, character_id: int):
    return await display_items_inventory(request, location_index, character_id)


@app.get("/inventory-generation/{location_index}/{character_id}/final_selection")
async def final_selection_inventory(request: Request, location_index: int, character_id: int):
    global all_selected_items, already_generated_items, all_characters
    next_character_id = character_id + 1
    character_name = all_characters_in_loc[character_id]["name"]
    all_characters_in_loc[character_id]["inventory"] = all_selected_items
    all_selected_items = []
    already_generated_items = []
    if next_character_id >= len(all_characters_in_loc):
        # write to all_the_characters.json
        all_characters += all_characters_in_loc
        dict_to_json_file(all_characters, "data/test_generations/all_the_characters.json")
        # write to all_the_locations.json
        items_dict = {}
        for ind, ch in enumerate(all_characters_in_loc):
            key = ch["name"]
            items_dict[key] = ch

        all_locations[location_index]["characters"] = items_dict
        dict_to_json_file(all_locations, "data/test_generations/all_the_locations.json")
        if location_index == len(all_locations) - 1:
            location_index = -1
        context = {"request": request, "characters": all_characters_in_loc, "location_index": location_index,
                   "loc_name": all_locations[location_index]["name"]}
        return templates.TemplateResponse("inventory_completion.html", context)
    return await display_items_inventory(request, location_index, next_character_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)