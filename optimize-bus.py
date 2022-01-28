# imports
import os      # tools to interact with the operating system
import pathlib # handle paths in a non os specific way
import json

from sqlalchemy import false    # handle loading and interacting with json data

## build the path that we are going to load objects from
obj_dir = pathlib.Path.cwd() / 'objects'

## lambda to validate that file is a json file
is_json = lambda de: (pathlib.Path(de.path).suffix.lower() == '.json')

## scan the dir to get all the objects. then try to load each json into a list.
## if the file fails to open, close the file handle.
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

## validate that the file name matches the json item name
def file_name_matches_item_name(tuple):
    (file, obj) = tuple
    return pathlib.Path(file).stem == obj["name"]

## validate that the tier of the item is either 0 if no children or max(tier of children)+1
def validate_tier(obj, dict):
    print('======= DEBUG =======')
    print(f'obj: {obj}')
    #### internal data
    max_child_tier = 0         
    recipie = obj["needs"] if obj["needs"] is not None else None
    book = list(zip(*dict))[1] # book contains all the recipes
    
    #### internal util function
    find_max_tier = lambda x: int(x) if int(x) > max_child_tier else max_child_tier

    ### iterate through each item in a particular recipie.
    ### only one entry should be found in book for each item since each item is unique
   
    for item in recipie:
        maybe_item_data = [ x for x in book if x["name"] == item ]
        if maybe_item_data:
            item_data = maybe_item_data[0]
            print(f'item_data: {item_data}')
            if validate_tier(item_data , data):
                max_child_tier = int(item_data["tier"]) if int(item_data["tier"]) > max_child_tier else max_child_tier
        else:
            continue

    ### test each item to see if it is the child with the highest child tier
    print(f'name: {obj["name"]}')
    print(f'max_child_tier: {max_child_tier}')
    print(f'obj_tier: {obj["tier"]}')
    print(f'first test: {int(obj["tier"]) == (max_child_tier + 1)}')
    print(f'second test: {int(obj["tier"]) == 0}')
    if int(obj["tier"]) == 0:
        return True
    elif int(obj["tier"]) == (max_child_tier + 1):
        return True
    elif int(obj["tier"]) == max_child_tier:
        msg = "item {0}'s tier is equal to the highest tier ingredient detected. the highest ingredient tier detected was {1} ".format(
            obj["name"], max_child_tier
        )
        raise ValueError(msg)
    elif int(obj["tier"]) > (max_child_tier + 1):
        msg = "item {0}'s tier is {1}. which is two or more levels higher than the highest teir ingredient detected. the highest ingredient tier detected was {2}".format(
            obj["name"], obj["tier"], max_child_tier
        )
        raise ValueError(msg)
    elif int(obj["tier"]) < (max_child_tier):
        msg = "item {0}'s tier is {1}. which is lower than the highest teir ingredient detected. the highest ingredient tier detected was {2}".format(
            obj["name"], obj["tier"], max_child_tier
        )
        raise ValueError(msg)
    else:
        return False    

# lets do some validation of the JSON data
(file, obj) = data[2]
print('======= RAW ========')
print(f'object: {obj}')
print('======= INFO =======')
print(f'validating file: {file}')
print(f'name: {obj["name"]}')
print(f'needs: {obj["needs"]}')
print('====================')
print( validate_tier(obj, data) )


# print(f'needs: {obj["needs"]}')