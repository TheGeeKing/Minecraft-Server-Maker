import os
import re
import shutil
import subprocess

import pythoncom
import requests
from win32com.client import Dispatch

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


def check_java(minecraft_version: str, custom_java: str|None = None) -> bool:
    """
    It checks if the java version is ok for the minecraft version.

    :param minecraft_version: str
    :type minecraft_version: str
    :param custom_java: str|None = None
    :type custom_java: str|None
    :return: The path to the java.exe file.

    Paper documentation recommendations:
    Paper Version	Recommended Java Version
    1.8 to 1.11	Java 8
    1.12 to 1.16.4	Java 11
    1.16.5	Java 16
    1.17.1-1.18.1+	Java 17

    Test:
    Java 8 can run up to 1.16.5
    1.17 needs at least Java 16
    1.18 needs at least Java 17
    """
    #TODO: check the custom java and return it if it's ok
    where_java = subprocess.run(["where", "java"], capture_output=True, text=True)
    if where_java.returncode:
        window.write_event_value("--POPUP-ERROR--", {"title": "Error", "text": "Java is not installed!\nYou must install Java to run your server."})
        return False
    pythoncom.CoInitialize()
    ver_parser = Dispatch("Scripting.FileSystemObject")
    java_paths = where_java.stdout.split("\n")
    java_paths.remove("")
    dict_java_paths = {}


    for java_path in java_paths:
        info = ver_parser.GetFileVersion(java_path)

        if info == "No Version Information Available":
            continue

        dict_java_paths[java_path] = float(info.split(".")[0] + "." + info.split(".")[1]) if info else None

    max_java_path = max((java_paths), key=lambda x: dict_java_paths[x])
    max_java_version = dict_java_paths[max_java_path]

    # check if the max java version is ok for the minecraft_version
    try:
        minecraft_version = float(minecraft_version)
    except ValueError:
        minecraft_version = float(f"{minecraft_version.split('.')[0]}.{minecraft_version.split('.')[1]}")

    if max_java_version >= 17:
        return max_java_path
    if minecraft_version <= 1.16:
        if max_java_version >= 8:
            return max_java_path
        else:
            window.write_event_value("--POPUP-ERROR--", {"title": "Error", "text": f"Java version is {max_java_version} but it needs to be at least 8"})
            return False
    if minecraft_version == 1.17:
        if max_java_version >= 16:
            return max_java_path
        else:
            window.write_event_value("--POPUP-ERROR--", {"title": "Error", "text": f"Java version is {max_java_version} but it needs to be at least 16"})
            return False
    if minecraft_version == 1.18:
        if max_java_version >= 17:
            return max_java_version
        else:
            window.write_event_value("--POPUP-ERROR--", {"title": "Error", "text": f"Java version is {max_java_version} but it needs to be at least 17"})
            return False
    window.write_event_value("--POPUP-ERROR--", {"title": "Error", "text": "This error is related to your Java version.\nPlease report it on GitHub:\ngithub.com/TheGeeKing/Minecraft-Server-Maker/issues"})
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
    user_java_path = f"\"{values['--CUSTOM-JAVA--']}\"" if values['--CUSTOM-JAVA--'] else None # add quotes around the path
    optimal_java_runtime = check_java(settings.get("minecraft_version"), user_java_path)
    if user_java_path:
        java_runtime = user_java_path
    elif optimal_java_runtime:
        java_runtime = f"\"{optimal_java_runtime}\""
    else:
        java_runtime = "java"

    if java_runtime not in ["java", optimal_java_runtime]: # skip that if java_runtime is from optimal_java_runtime because it is from `where java`
        test_java_runtime_provided: bool = os.system(f"{java_runtime} -version") # if no error occurs, it means that the java runtime provided by the user is correct and it's returncode is 0
        if test_java_runtime_provided: # if java_runtime is incorrect, returncode 1
            window.write_event_value("--POPUP-ERROR--", {"title": "Error", "text": f"Error running your custom java path:\n{user_java_path}\nPlease check if it's correct!\nIt will automatically fallback to the optimal java runtime."})
            java_runtime = optimal_java_runtime
        else:
            pass #TODO: check if the custom java can run the minecraft version, maybe direclty in check_java function
    paper_args = ""
    for key, value in dict_start.items():
        if key=="--ENABLE-GUI--" and values[key]:
            continue
        elif values[key]:
            paper_args += f" {value}"
    start_content = """{auto_restart_1}{java_runtime} -Xms{xms}M -Xmx{xmx}M -jar {paper_jar}{paper_args}
{auto_restart_2}
{pause}""".format(auto_restart_1=":start\n" if values["--AUTO-RESTART--"] else "", java_runtime=java_runtime, xms=int(values["--XMS--"]), xmx=int(values["--XMX--"]), paper_jar=settings.get("filename"), paper_args=paper_args, auto_restart_2="goto :start\n" if values["--AUTO-RESTART--"] else "", pause="PAUSE" if values["--PAUSE--"] else "")
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
    window.write_event_value("--UPDATE--", "Making folder...")
    make_folder(dest_folder)
    # download file with url to server folder
    window.write_event_value("--UPDATE--", "Downloading JAR file...")
    download(url, dest_folder)
    # write file to server folder
    window.write_event_value("--UPDATE--", "Agreeing to EULA...")
    write_file(os.path.join(dest_folder, "eula.txt"), "eula=true")
    # write server.properties file
    window.write_event_value("--UPDATE--", "Writing server.properties...")
    write_file(os.path.join(dest_folder, "server.properties"), settings.get("server_properties"))

    window.write_event_value("--UPDATE--", "Creating start file...")
    setup_start_file(dest_folder)
    window.write_event_value("--FINISHED--", "")
