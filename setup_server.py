import os
import re
import shutil
import subprocess

import requests

import settings


def write_file(file_path, content):
    """
    It writes the content to the file at the given file path

    :param file_path: The path to the file you want to write to
    :param content: The content to write to the file
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def get_element(elements: list[list], key_to_find):
    """
    It loops through the elements list, and for each element in the list, it loops through the element
    and checks if the element has a key property and if the key property is equal to the key_to_find. If
    it is, it returns the element

    :param elements: list[list]
    :type elements: list[list]
    :param key_to_find: the key you want to find
    :return: The element with the key that matches the key_to_find.
    """
    for element in elements:
        for ele in element:
            # check if ele has a key property
            if hasattr(ele, "key") and ele.key==key_to_find:
                return ele


def make_folder(dest_folder: str):
    """
    It creates a folder if it doesn't exist, and if it does exist, it deletes it and creates a new one

    :param dest_folder: The path to the folder where the server will be
    :type folder_path: str
    """
    # erase the folder name if it already exists
    try:
        if os.path.exists(dest_folder):
            shutil.rmtree(dest_folder)
        os.mkdir(dest_folder)
    except PermissionError as e:
        window.write_event_value("--POPUP-ERROR--", {"title": "Error", "text": f"Error creating folder: {e}"})


def download(url: str, dest_folder: str):
    """
    It downloads a file from a URL and saves it to a folder

    :param url: The URL of the file you want to download
    :type url: str
    :param dest_folder: The folder where the file will be downloaded to
    :type dest_folder: str
    """
    filename = url.split("/")[-1].replace(" ", "_") # cleaning filename
    file_path = os.path.join(dest_folder, filename)
    settings.add("filename", filename)

    r = requests.get(url, stream=True)
    if r.status_code != 200:
        window.write_event_value("--POPUP-ERROR--", {"title": "Error", "text": f"Error downloading {filename}"})
    with open(file_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 8):
            if chunk:
                f.write(chunk)
                f.flush()
                os.fsync(f.fileno())


def check_java(minecraft_version: str, custom_java: str) -> bool:
    """
    It checks if the user has Java installed and if it's version is at least 17

    :param minecraft_version: The version of Minecraft you want to run
    :type minecraft_version: str
    :param custom_java: The path to the java executable. If you don't know what this is, leave it blank
    :type custom_java: str
    :return: a boolean value.
    """
    if subprocess.run(f"{custom_java} -version" if custom_java else "java -version").returncode: # os.system(f"{custom_java} -version" if custom_java else "java -version")
        window.write_event_value("--POPUP-ERROR--", {"title": "Error", "text": "Java is not installed"})
    try:
        minecraft_version = float(minecraft_version)
    except Exception:
        minecraft_version = float(f"{minecraft_version.split('.')[0]}.{minecraft_version.split('.')[1]}")
    if minecraft_version < 1.18:
        return True
    output = subprocess.run([f"{custom_java}" if custom_java else "java", "-version"], capture_output=True, text=True)
    string = output.stdout.split("\n")[0] if output.stdout else output.stderr.split("\n")[0]
    result = re.search("\"(.*)\"", string)
    if int(result[1].split(".", maxsplit=1)[0])>=17:
        return True
    window.write_event_value("--POPUP-ERROR--", {"title": "Error", "text": f"Java version is {result[1]} but it needs to be at least 17"})
    return False


def setup_start_file(dest_folder: str):
    """
    It creates a start.bat file in the folder of the server.

    :param dest_folder: The path to the directory where the start.bat file will be created
    """
    dict_start = {
    "--ENABLE-GUI--": "--nogui",
    "--BONUS-CHEST--": "--bonusChest",
    "--ERASE-CACHE--": "--eraseCache",
    "--FORCE-UPGRADE--": "--forceUpgrade",
    "--SAFE-MODE--": "--safeMode",
    "--DEMO-MODE--": "--demo",
    "--ONLINE-AUTHENTICATION--": "--online-mode true",
    }
    _, values = window.read(timeout=0)
    if not check_java(settings.get("minecraft_version"), values["--CUSTOM-JAVA--"]):
        return
    paper_args = ""
    for key, value in dict_start.items():
        if key=="--ENABLE-GUI--" and values[key]:
            continue
        elif values[key]:
            paper_args += f" {value}"
    start_content = """{auto_restart_1}{java_runtime} -Xms{xms}M -Xmx{xmx}M -jar {paper_jar}{paper_args}
{auto_restart_2}
{pause}""".format(auto_restart_1=":start\n" if values["--AUTO-RESTART--"] else "", java_runtime="java" if values["--CUSTOM-JAVA--"]=="" else values["--CUSTOM-JAVA--"], xms=int(values["--XMS--"]), xmx=int(values["--XMX--"]), paper_jar=settings.get("filename"), paper_args=paper_args, auto_restart_2="goto :start\n" if values["--AUTO-RESTART--"] else "", pause="PAUSE" if values["--PAUSE--"] else "")
    write_file(os.path.join(dest_folder, "start.bat"), start_content)


def setup_server(url):
    """
    It downloads a file from a url, writes a file to the server folder, writes a server.properties
    file to the server folder, and creates a start.bat file in the server folder.

    :param url: The url of the server file
    """
    global window
    window, folder_path, folder_name = settings.get("window"), settings.get("folder_path"), settings.get("folder_name")
    dest_folder = os.path.join(folder_path, folder_name)
    make_folder(dest_folder)
    # download file with url to server folder
    download(url, dest_folder)
    # write file to server folder
    write_file(os.path.join(dest_folder, "eula.txt"), "eula=true")
    # write server.properties file
    write_file(os.path.join(dest_folder, "server.properties"), settings.get("server_properties"))

    setup_start_file(dest_folder)
    window.write_event_value("--FINISHED--", "")
