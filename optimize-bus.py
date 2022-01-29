# imports
import os      # tools to interact with the operating system
import pathlib # handle paths in a non os specific way
import json

# build the path that we are going to load objects from
obj_dir = pathlib.Path.cwd() / 'objects'

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

# validate that the file name matches the json item name
def validate_file_name_matches_item_name(tuple):
    (file, obj) = tuple
    return pathlib.Path(file).stem == obj["name"]

# validate that the tier of the item is either 0 if no children or max(tier of children)+1
def validate_tier(obj, dict):
    ## internal data
    max_ingredient_tier = -1
    max_ingredient_name = None         
    recipie = obj["needs"] if obj["needs"] != 'none' else []
    book = list(zip(*dict))[1] # book contains all the recipes
    
    ## iterate through each ingredient in a particular recipie.
    ## only one entry should be found in book for each ingredient since each item is unique
    ## if the ingredient we are inspecting has any ingredients, then recursivly validate those too.
    ## if we can trust that the data for the ingredient under inspection is valid,
    ## then test  it to see if this is the highest tier ingredient in the recipie.
    ## if it is then save its tier and name data.
    for ingredient in recipie:
        maybe_ingredient_data = [ x for x in book if x["name"] == ingredient ]
        if maybe_ingredient_data:
            ingredient_data = maybe_ingredient_data[0]
            if validate_tier(ingredient_data , data):
                max_ingredient_name = ingredient_data["name"] if int(ingredient_data["tier"]) > max_ingredient_tier else max_ingredient_name
                max_ingredient_tier = int(ingredient_data["tier"]) if int(ingredient_data["tier"]) > max_ingredient_tier else max_ingredient_tier 
        else:
            raise ValueError("Error processing recipie for {0}. could not find ingredient '{1}' in recipie book!".format( obj["name"], ingredient))

    ## test the item under inspection to see if it is valid, other wise raise an exception
    if int(obj["tier"]) == 0 and obj["needs"] == 'none':
        return True
    elif int(obj["tier"]) == (max_ingredient_tier + 1):
        return True
    elif int(obj["tier"]) == max_ingredient_tier:
        msg = "item {0}'s tier is equal to the highest tier ingredient detected. the highest tier ingredient detected was {1} wich is tier {2} ".format(
            obj["name"], max_ingredient_name, max_ingredient_tier
        )
        raise ValueError(msg)
    elif int(obj["tier"]) > (max_ingredient_tier + 1):
        msg = "item {0}'s tier is {1}. which is two or more tiers above the highest teir ingredient detected. the highest tier ingredient detected was {2} wich is tier {3}".format(
            obj["name"], obj["tier"], max_ingredient_name, max_ingredient_tier
        )
        raise ValueError(msg)
    elif int(obj["tier"]) < (max_ingredient_tier):
        msg = "item {0}'s tier is {1}. which is lower than the hightest tier detected. the highest tier ingredient detected was {2} which is tier {3}".format(
            obj["name"], obj["tier"], max_ingredient_name, max_ingredient_tier
        )
        raise ValueError(msg)
    else:
        return False    

# lets do some validation of the JSON data
def validate(data):
    print('======= VALIDATION =======')
    # pair, = [p for p in data if p[1]["name"] == 'proliferator_mk1']
    for pair in data:
        (file, obj) = pair
        print(f'validating file: {file}')
        if validate_file_name_matches_item_name(pair):
            print('--- object name valid') 
        else: 
            raise ValueError('JSON object name did not match file name. Object: {0} File: {1}'.format(obj["name"],file))
    
        if validate_tier(obj, data):
            print('--- tier data valid') 
        else: 
            raise ValueError('tier data could not be validated')
    

validate(data)   