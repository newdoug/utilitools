"""Loading configs and other file formats"""

import json
import os
from typing import Union

import yaml


def load_yaml_file(filename: str) -> Union[dict, list]:
    """Load and parse a YAML config file"""
    with open(filename, "r", encoding="UTF-8") as handle:
        return yaml.load(handle, Loader=yaml.SafeLoader)


def load_json_file(filename: str) -> Union[dict, list]:
    """Load and parse a JSON config file"""
    with open(filename, "r", encoding="UTF-8") as handle:
        return json.load(handle)


def get_all_filenames(directory: str) -> list[str]:
    """Return a list of all filenames (recursively) beneath `directory`.
    All returned paths are relative to `directory`. If `directory` is absolute, then the returned filenames are also
    absolute
    """
    filenames = []
    for walk in os.walk(directory):
        for filename in walk[2]:
            filenames.append(os.path.join(walk[0], filename))
    return filenames
