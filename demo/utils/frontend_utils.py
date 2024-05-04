from random import sample, randint

def render_items_choices(items):
    print("CHOICES")
    for i, item in enumerate(items):
        print("Choice ", i)
        print(item)

def render_selected_items(items):
    print("SELECTED ITEMS")
    for i, item in enumerate(items):
        print(item)

def get_selected_items(items):
    num_chosen = randint(1, 3)
    chosen = sample(items, num_chosen)
    return chosen

def user_submit():
    user_inp = input("Submit? (y/n)\n")
    result = True if user_inp == "y" else False
    return result