# dyson-sphere-lab

A place to study the game Dyson Sphere Program.

## Installation

### Python Environment Setup

Create a python virtual environment for your copy of the code. This is done to prevent you from polluting your local python installation & tool chain.
Required python packages for this project can be installed via a pip requirements file:

See official python docs for more information: [creating-a-virtual-environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment)

```python
# create the venv folder to hold the virtual environment
python3 -m venv <path/to/your/dir>/venv
```

### Activate the Virtual Environment

The newly installed environment can be activated by running the activate script in the virtual environment.
See the official python docs for more information: [activating-a-virtual-environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#activating-a-virtual-environment)

```bash
# Unix
source <path/to/you/dir>/venv/bin/activate
```

```powershell
# Windows
<path\to\your\dir>\venv\Scripts\activate
```

### Install Required Packages

Before installing the required python packages be sure to [activate your virtual environment](#activate-the--virtual-environment)

```python
# activate your venv first
# install the required packages 
(venv) python3 -m pip install -r requirements.txt
```

## Data Model Control Document

This document lays out the design and specification of the JSON data objects that represent the in game items and buildings.
objects are classified into two categories based on the replicator menu available to the player through the Icarus mecha.

see the [data model](objects/data_model.md) document for more information
