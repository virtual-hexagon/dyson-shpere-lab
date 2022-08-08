# imports
import os      # tools to interact with the operating system
import pathlib # handle paths in a non os specific way
import json

# build the path that we are going to load objects from
obj_dir = pathlib.Path.cwd() / 'objects' / 'items'
buildings_dir = pathlib.Path.cwd() / 'objects' / 'buildings'

# lambda to validate that file is a json file
is_json = lambda de: (pathlib.Path(de.path).suffix.lower() == '.json')

# scan the dir to get all the objects. then try to load each json into a list.
# if the file fails to open, close the file handle.
data = []
for entry in filter(is_json, os.scandir(obj_dir)):
    f = open(entry.path,"r")
    try:
        data.append(
            (entry.path, json.load(f))
        )
    except IOError:
        print(f"could not open file: {entry.path}")
    finally:
        f.close()
for entry in filter(is_json, os.scandir(buildings_dir)):  # Duplicated the above code to include buildings
    f = open(entry.path,"r")
    try:
        data.append(
            (entry.path, json.load(f))
        )
    except IOError:
        print(f"could not open file: {entry.path}")
    finally:
        f.close()

# data is in the format (<filename>, <dictionary>)
data.sort()  # Sorts by file name (I think)

# Initialize variables
end_prod_name = input('Enter the name of the item or building you want to make: ')
end_prod_dict = dict()
num_builders_dict = dict()

# Make a list of all the names
names_list = []
for path, item_dict in data:
    names_list.append(item_dict['name'])

# Check if entered name is in the list
if end_prod_name in names_list:
    end_prod_dict = data[names_list.index(end_prod_name)][1]  # Use the index in the name list to get the dictionary for the end product
    print('Item found!')
    print(end_prod_dict)
else:  # If name is not in the list, print closest names alphabetically as suggestions and quit
    names_list.append(end_prod_name)
    names_list.sort()
    idx = names_list.index(end_prod_name)
    print('The item', end_prod_name, 'was not found. Maybe you meant', names_list[idx-1], 'or', names_list[idx+1], '?')
    quit()

# Check that the item is not tier zero
if end_prod_dict['tier'] == '0':
    print('Just mine it!')
    quit()

# Calculate the number of assemblers/smelters needed to reach production rate and add them up in the num_builders_dict dictionary
def calculate_production(item_name, production_rate):  # (string, float)
    print(production_rate, item_name, 'per second')
    item_dict = data[names_list.index(item_name)][1]  # Using the index in the names list to get the dictionary of the item
    if item_dict['tier'] != "0":
        num_builders = int(production_rate * item_dict['rate']) + (production_rate % item_dict['rate'] > 0.0)  # Rounds up to the nearest int. If the second part is True it becomes 1. 
        num_builders_dict[item_name] = num_builders_dict.get(item_name, 0) + num_builders  # Adds number to existing key or creates a new key
        print('Builders:', num_builders)
        for key,value in item_dict['needs'].items():
            calculate_production(key, float(value) * production_rate)
    


end_prod_rate_str = input('How many do you want to make per minute?')
end_prod_rate = float(end_prod_rate_str) / 60.0  # Converted to seconds
calculate_production(end_prod_name, end_prod_rate)
print('You need:')
for k,v in num_builders_dict.items():
    print(v, 'builders for', k)

