import json
import time
from typing import Union

import requests
from lxml import html

VERSIONS_URL = "https://api.papermc.io/v2/projects/paper/"

BUILDS_URL = "https://api.papermc.io/v2/projects/paper/versions/{version}/"

DOWNLOAD_URL = "https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{build}/downloads/paper-{version}-{build}.jar"

"""CLASS FOR EXECPTIONS"""


"""CHECKS"""

def check_version(version: Union[float, str]) -> bool:
    versions = get_versions()
    return str(version) in versions

def check_build(version: Union[float, str], build: Union[int, str]) -> bool:
    builds = get_builds(version)
    try:
        return int(build) in builds
    except ValueError:
        raise ValueError("Build must be an integer or an integer in a string format")

"""FUNCTIONS"""

def get_versions() -> list[str]:
    response = requests.get(VERSIONS_URL)
    if response.status_code != 200:
        raise Exception("Error getting versions")
    return json.loads(response.text)["versions"]

def get_builds_raw(version: Union[float, str]) -> list[str]:
    response = requests.get(BUILDS_URL.format(version=str(version)))
    if response.status_code != 200:
        raise Exception("Error getting builds")
    return json.loads(response.text)["builds"]

def get_builds(version: Union[float, str]) -> list[str]:
    if not check_version(version):
        raise Exception("Version not found")
    return get_builds_raw(version)

def get_download_url_raw(version: Union[float, str], build: Union[int, str]) -> str:
    return DOWNLOAD_URL.format(version=str(version), build=str(build))

def get_download_url(version: Union[float, str], build: Union[int, str]) -> str:
    if not check_version(version):
        raise Exception("Version not found")
    if not check_build(version, build):
        raise Exception("Build not found")
    return get_download_url_raw(version, build)

def get_latest_version() -> str:
    response = requests.get(VERSIONS_URL)
    if response.status_code != 200:
        raise Exception(f"Error getting latest version | {response.status_code}")
    return json.loads(response.text)["versions"][-1]

def get_latest_build(version: Union[float, str]) -> int:
    return get_builds(version)[-1]

def get_latest_version_and_build():
    version = get_latest_version()
    return version, get_latest_build(version)
