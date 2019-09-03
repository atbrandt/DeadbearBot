import yaml
from pathlib import Path


# Setting platform-independent path to config file
CONFIGFILE = Path(__file__).parent / "config.yml"


# Set a reference of default options that must exist in config
CFGDEFAULT = {
'Global': {'Prefix': '-'},
'AutoRole': None,
'Greetings': {'ChannelID': None, 'Message': None},
'Farewells': {'ChannelID': None, 'Message': None}
}


# Function for writing to the config file
def write_cfg(data):
    with Path.open(CONFIGFILE, 'w', encoding='utf-8') as config:
        yaml.safe_dump(data,
                       config,
                       indent=4,
                       default_flow_style=False,
                       allow_unicode=True)


# Function for reading the config file
def read_cfg():
    with Path.open(CONFIGFILE, 'r', encoding='utf-8') as config:
        cfg = yaml.safe_load(config)
    return cfg


# Initialize the config
try:
    currentCFG = read_cfg()
except:
    write_cfg(CFGDEFAULT)

