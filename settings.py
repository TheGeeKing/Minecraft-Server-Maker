"""
Usage:
Should be init() at the top of the main file, then add("name", data)
and get("name") in other files when needed
"""

def init():
    """
    It creates a global variable called settings and sets it to an empty dictionary.
    """
    global settings
    settings = {}

def add(name, data):
    """
    It takes a name and data as arguments, adds the name and data to the global settings dictionary, and
    returns the data

    :param name: The name of the setting
    :param data: The data to be stored in the settings
    :return: The data that was added to the settings dictionary.
    """
    global settings
    settings[name] = data
    return settings[name]

def remove(name):
    """
    It deletes the key-value pair from the settings dictionary whose key is the value of the name
    parameter

    :param name: The name of the setting to remove
    """
    global settings
    del settings[name]

def get(name):
    """
    It returns the value of the key in the settings dictionary that matches the name parameter

    :param name: The name of the setting to get
    :return: The value of the key 'name' in the dictionary 'settings'
    """
    global settings
    return settings[name]
