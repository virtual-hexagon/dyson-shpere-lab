# imports
import os      # tools to interact with the operating system
import pathlib # handle paths in a non os specific way
import json

# build the path that we are going to load objects from
obj_dir = pathlib.Path.cwd() / 'objects' / 'items'

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
    
# Main Program
validate(data)

# now that data is valid lets strip the file paths from the data set
# book contains all of the recipies in the game
book = list(zip(*data))[1] 

# if we are on windows import the distributed graphviz lib
# else if we are on any other platform we will assume graphviz is on the path already
import platform
if platform.system() == 'Windows':
    graphviz_lib = pathlib.Path.cwd() / 'lib' / 'graphviz-2.50.0-win32' / 'bin'
    os.environ["PATH"] += os.pathsep + str(graphviz_lib)

import pydot as pd
import networkx as nx

get_all_in_tier = lambda n: [ item for item in book if int(item["tier"]) == n ]
get_max_tier = lambda: int(max([ item["tier"] for item in book]))
graph = pd.Dot("item_tree", graph_type="digraph")

# Add nodes
for n in range(0,):
    [ graph.add_node(pd.Node(item["name"])) for item in get_all_in_tier(n) ]

# Add edges
for recipie in book:
    [ graph.add_edge(pd.Edge( item, recipie["name"])) for item in recipie["needs"] if recipie["needs"] != "none"]
        
graph.write_png("pre_sort.png")

nxgraph = nx.nx_pydot.from_pydot(graph)
nodes = nx.algorithms.dag.lexicographical_topological_sort(nxgraph)
nxgraph.update(edges=None,nodes=nodes)
graph = nx.nx_pydot.to_pydot(nxgraph)
graph.write_png("post_sort.png")

# import networkx as nx
# graph = nx.DiGraph()

# get_all_in_tier = lambda n: [ item for item in book if int(item["tier"]) == n ]
# get_max_tier = lambda: int(max([ item["tier"] for item in book]))

# for item in get_all_in_tier(0):
#     graph.add_node(item["name"])

# pd_graph = nx.nx_pydot.to_pydot(graph)
# pd_graph.write_png("output.png")





# # The digraph is defined under graphviz which we will use for creating graphs object, nodes, and edges.
# from graphviz import Digraph

# outd = pathlib.Path.cwd() / 'output'

# # setup graph
# graph = Digraph()

# graph.node('a', 'Machine Learning Errors')
# graph.node('b', 'RMSE')
# graph.node('c', 'MAE')

# graph.edges(['ab', 'ac'])

# graph.render()
# graph.view()

#graph.write_png(outd + "tree.png")


# from flexx import flx

# class Example(flx.Widget):
#     def init(self):
#         flx.Label(text='hello world')

# # app = flx.App(Example)
# # app.export('example.html', link=0)  # Export to single file
# app = flx.App(Example)
# #app.launch('app')  # to run as a desktop app
# app.launch('browser')  # to open in the browser
# #flx.run()  # mainloop will exit when the app is closed