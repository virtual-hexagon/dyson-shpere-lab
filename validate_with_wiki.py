# imports
import os      # tools to interact with the operating system
import pathlib # handle paths in a non os specific way
import json
from urllib.request import urlopen  # For opening URLs
from bs4 import BeautifulSoup  # For HTML parsing
import ssl 
import urllib.request, urllib.parse, urllib.error  # For handling web pages like a file
import re  # Regular Expressions

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

#---------------- Start of Validate with Wiki ----------------------

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Get the JSON file and the wiki page to compare it against
item_name = input('Enter the JSON format name of the item:')
item_name_wiki = input('Enter the Wiki format name of the item:')
url = input('Enter respective URL:')

#***********REPEATED CODE START*********
# Make a list of all the names
names_list = []
for path, item_dict in data:
    names_list.append(item_dict['name'])

# Check if entered name is in the list
if item_name in names_list:
    end_prod_dict = data[names_list.index(item_name)][1]  # Use the index in the name list to get the dictionary for the end product
else:  # If name is not in the list, print closest names alphabetically as suggestions and quit
    names_list.append(item_name)
    names_list.sort()
    idx = names_list.index(item_name)
    print('The item', item_name, 'was not found. Maybe you meant', names_list[idx-1], 'or', names_list[idx+1], '?')
    quit()

# Check that the item is not tier zero
if end_prod_dict['tier'] == '0':
    print('Just mine it!')
    quit()
#***********REPEATED CODE END***********

# Initialize Variables
wiki_item_dict = dict()
wiki_item_dict['needs'] = dict()
arrow_value = 0.0

# fhand = urllib.request.urlopen(url)  # Open the url like a file handle
html = urllib.request.urlopen(url).read()
soup = BeautifulSoup(html, 'html.parser')

# Retrieve and loop through all of the div tags
tags = soup('div')
for tag in tags:
    if tag.get('class', None) is not None and tag.get('class', None)[0] == 'recipe-extended':  # if tag is not Null and class is 'recipe-extended'
        #print('TAG:', tag)  # Ouputs entire HTML section
        #print('Class:', tag.get('class', None))  # Ouputs list of classes, like: ['recipe-extended']
        #print('Contents:', tag.contents)  # Ouputs a list of the sub-components of this block of HTML, like: ['Gear']
        #print('Attrs:', tag.attrs)  # Outputs a dictionary of the HTML attributes, like: {'class': ['recipe-extended']}
        for section in tag.contents:  # Look through the HTML within the 'recipe-extended section
            if section.get('class', None) is not None:  # if tag is not Null
                # Get the Recipe Name
                if section.get('class', None)[0] == 'recipe-name':  # If class is 'recipe-name'
                    #print('Contents:', section.contents[0])
                    if section.contents[0] != item_name_wiki:  # If not the recipe we want, exit for loop
                        break
                    wiki_item_dict['name'] = section.contents[0]
                # Get what it is Made In
                if section.get('class', None)[0] == 'recipe-extended-table':
                    section_tags = section('a')  # Gets all the anchor tags in section
                    for anchor_tag in section_tags:
                        if anchor_tag.get('title', None) is not None:
                            wiki_item_dict['made_in'] = anchor_tag.get('title', None)
                # Get the recipe inputs and outputs
                if section.get('class', None)[0] == 'recipe-container':
                    div_tags = section('div')
                    for div_tag in div_tags:
                        # Find recipe items
                        if div_tag.get('class', None) is not None and div_tag.get('class', None)[0] == 'recipe-item':
                            sub_anchor_tags = div_tag('a')
                            sub_div_tags = div_tag('div')
                            for sub_anchor_tag in sub_anchor_tags:
                                # Find output amount
                                if sub_anchor_tag.get('title', None) is not None and sub_anchor_tag.get('title', None) == item_name_wiki:  # Why did this get return a string instead of a list?!?!?
                                    for sub_div_tag in sub_div_tags:
                                        if sub_div_tag.get('class', None) is not None and sub_div_tag.get('class', None)[0] == 'recipe-item-value':
                                            wiki_item_dict['output_num'] = sub_div_tag.contents[0]
                                # Find input items and amounts
                                else:
                                    for sub_div_tag in sub_div_tags:
                                        if sub_div_tag.get('class', None) is not None and sub_div_tag.get('class', None)[0] == 'recipe-item-value':
                                            wiki_item_dict['needs'][sub_anchor_tag.get('title', None)] = int(sub_div_tag.contents[0])  # {'needs': {'Iron Ingot': '1'}...}
                        # Find number on the arrow to calculate the rate
                        elif div_tag.get('class', None) is not None and div_tag.get('class', None)[0] == 'recipe-arrow-value':
                            arrow_str_raw = div_tag.contents[0]
                            arrow_value = float(arrow_str_raw[:len(arrow_str_raw)-1])  # Removes the 's' at the end
        
wiki_item_dict['rate'] = arrow_value / float(wiki_item_dict['output_num'])  # rate is in units of seconds/item

print('Wiki dict:', wiki_item_dict)
print('JSON dict:', end_prod_dict)

# Compare the two dictionaries and print inconsistencies
if wiki_item_dict['name'].lower() != end_prod_dict['name']:
    print('Mismatch: Wiki name is:', wiki_item_dict['name'].lower(), 'and JSON name is', end_prod_dict['name'])
if wiki_item_dict['made_in'].lower() != end_prod_dict['made_in']:
    print('Mismatch: Wiki made-in is:', wiki_item_dict['made_in'].lower(), 'and JSON made-in is', end_prod_dict['made_in'])
if wiki_item_dict['rate'] != end_prod_dict['rate']:
    print('Mismatch: Wiki rate is:', wiki_item_dict['rate'], 'and JSON rate is', end_prod_dict['rate'])



