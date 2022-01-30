# Data Model Control Document

This document lays out the design and specification of the JSON data objects that represent the in game items and buildings.
objects are classified into two categories based on the replicator menu available to the player through the Icarus mecha.

## Tier Definition

* Tier 0 -- items that are "raw" resources directly mined or gathered from the environment in the game
* Tier 1 -- items that are made from Tier 0 items only.
* Tier 2 -- items that are made from aleast one Tier 1 item

General Rule:

* Tier N -- items that are made from atleast one Tier N-1 item

## JSON Data model

JSON data in this project must adhere to the following rules in order to be considered valid.
A basic item JSON object should have the following mandatory keys and follow the following rules:

Rule 1: all text is lower case
Rule 2: no spaces. all word seperation is done with underscores

* name - The ingame name of the item
  * Spaces are note valid. seperate works with underscores
  * The item name must match the file name

* type - The in game classification of the item based on the Icarus's replicator GUI. Currently the replicator has two tabs denoting two different groups of in game items: items and buildings
  * value must be "item" or "building"

* tier - A number computed by this project based on the definition in the [tier definition](#tier-definition) section of this document. Generally tier is considered a figure of merit for representing the complexity of producing a certain item within the game.

* made_in - A string repesenting which building a particular item can be produced in. note the specific definitions below:
  * vein - Denotes any item which is a natural resouce that can be automatically collected by a miner, pump, ray-reciever, or orbital collector. For this data model a vein is a stand in for any pool of natural resources. it is meant to refer to any of the following ore veins, oceans, oil spots, gas giants, black holes, ect.

  * smelter - This model option does not differentiate or account for differences between the arc smelter and plane smelter

  * assembler - This model option does not diffentiate or account for difference between Mk.I, Mk.II or Mk.III assemblers

  * chemical_plant

  * oil_refinery

  * research_facility

  * particle_collider

  * fractionator
  
* needs - The needs key should contain a dictionary with all ingredients needed to make the item. the dictionary should have entries of the form  <item name> : < # of item >  e.g.  "iron" : 2.  If the item is a natural resource or "Tier 0" in the convention of this data model, then the needs key may be set to the string "none" to indicate that no input items are needed. The "none" value can be specified in place of a dictionary, for example: "needs" : "none"

* alt - alt is an optional key. It is intended to be an array of dictionaries that may or may not exist depending on if an item has an alternate recipie provided by the game. Since some items may have more than one alternate recipie, looking at you hydrogen, the array has no fixed length. If there are no alternate recipie then the "alt" key can be omitted entirely from the JSON object.

## JSON Template

```json
{
  "name": "<item_name_here>",
  "type": "<item | building>",
  "tier": "< tier_num >",
  "made_in": "<building>",
  "needs": {
    "<ingredient_name>": "<num_ingredient>",
    "<ingredient_name>": "<num_ingredient>",
    "<ingredient_name>": "<num_ingredient>",
  },
  "alt":[
    {
      "made_in": "<building>",
      "needs":{
        "<ingredient_name>": "<num_ingredient>",
        "<ingredient_name>": "<num_ingredient>",
      }
    },
    {
      "made_in": "<another_building>",
      "needs": {
        "<ingredient_name>": "<num_ingredient>",
        "<ingredient_name>": "<num_ingredient>",
      }
    },
    {
      "made_in": "vien",
      "needs" : "none"
    }
  ]
}
```
