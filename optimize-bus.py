# imports
import os      # import os tools
import pathlib # handle paths in a non os specific way
import json

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
    except:
        print(f"could not open file: {entry.path}")
    finally:
        f.close()


## validate that the file name matches the json item name
def file_name_matches_item_name(tuple):
    (file, obj) = tuple
    return pathlib.Path(file).stem == obj["name"]

## validate that the tier of the item is either 0 if no children or max(tier of children)+1
def validate_tier(tuple):
    (file, obj) = tuple

# lets do some validation of the JSON data
print( file_name_matches_item_name(data[1]) )