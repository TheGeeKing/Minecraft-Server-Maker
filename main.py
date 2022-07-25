import os
import sys
import threading
import webbrowser
from os import chdir

import PySimpleGUI as sg

import settings
from get_papermc import get_builds, get_download_url, get_versions
from setup_server import setup_server


def read_file(file_path):
    """
    It opens the file at the given path, reads it, and returns the contents

    :param file_path: The path to the file you want to read
    :return: the contents of the file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(file_path, content):
    """
    It opens a file, writes some content to it, and then closes the file

    :param file_path: The path to the file you want to write to
    :param content: The content to be written to the file
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":

    if getattr(sys, "frozen", False):  # Running as compiled
        chdir(sys._MEIPASS)  # change current working directory to sys._MEIPASS

    sg.theme("DarkAmber")

    settings.init()

    settings.add("folder_path", os.path.join(os.path.join(os.environ["USERPROFILE"]), "Desktop\\"))

    tab1_layout =  [
        [
            sg.Text("Select a location:"),
            sg.Input(settings.get("folder_path"), key="--FOLDER-PATH--"),
            sg.FolderBrowse(button_text="Browse", key="folder_path", initial_folder=settings.get("folder_path"))
        ],
        [
            sg.Text("Name:"),
            sg.Input(key="--NAME--", size=15, tooltip="The name of the directory where the server will be."),
        ],
        [
            sg.Text("Version:"),
            sg.DropDown(get_versions()[::-1], key="--DROPDOWN-VERSIONS--", tooltip="The version of Minecraft that the server will be.", readonly=True, enable_events=True)
        ],
        [
            sg.Text("Build:"),
            sg.DropDown([""], key="--DROPDOWN-BUILDS--", tooltip="The build version of Paper that the server will be.", size=(10, 30), readonly=True)
        ],
        [sg.Checkbox("Accept EULA", key="--ACCEPT-EULA--", default=True)]
        ]

    server_properties_template = read_file("template/server.properties")

    column = [
        [
            sg.Text(line.split("=")[0] + "="),
            sg.Input("" if len(line.split("=")) == 1 else line.split("=")[1], size=((5,1) if line.split("=")[0] in ["true", "false"] else (20,1)))
        ] for line in server_properties_template.split("\n") if len(line) != 0
        ]


    tab2_layout = [
        [
            sg.Column(column, scrollable=True,  vertical_scroll_only=True, expand_x=True, size_subsample_height=6)
        ]
        ]

    column2 = [
        [
            sg.Slider(range=(1024,10240), resolution=512, default_value=2048, orientation="horizontal", key="--XMS--", enable_events=True),
            sg.Slider(range=(1024,10240), resolution=512, default_value=2048, orientation="horizontal", key="--XMX--"),
            sg.Checkbox("", key="--ENABLE-SYNC-RAM--", default=True, enable_events=True)
        ]
        ]

    tab3_layout = [
        [
            sg.Text("Custom Java path:"),
            sg.Input(key="--CUSTOM-JAVA--", tooltip="The path to the Java executable.\nLeave blank to use the default Java path.\ne.g. C:\Program Files (x86)\Common Files\Oracle\Java\javapath\java.exe"),
            sg.FileBrowse(button_text="Browse", tooltip="Select your Java executable.")],
        [
            sg.Slider(range=(1024,10240), resolution=512, default_value=2048, orientation="horizontal", key="--XMS--", enable_events=True),
            sg.Slider(range=(1024,10240), resolution=512, default_value=2048, orientation="horizontal", key="--XMX--", enable_events=True)
        ],
        [sg.Checkbox("Sync RAM (recommended)", key="--ENABLE-SYNC-RAM--", default=True, enable_events=True)],
        [sg.Text("Warning: Some versions may not accept some of these options!")],
        [
            sg.Checkbox("Server GUI", key="--ENABLE-GUI--", default=True, tooltip="Doesn\"t open the GUI when launching the server.\nYou will still be able to interact with your server, but you must use the cmd or Terminal if enabled."),
            sg.Checkbox("Pause output when server is stopped", default=True, key="--PAUSE--", tooltip="Pauses the output when the server is stopped.\nUseful if the server crashes."),
        ],
        [
            sg.Checkbox("Bonus Chest", key="--BONUS-CHEST--", default=False, tooltip="If a bonus chest should be generated, when the world is first generated."),
            sg.Checkbox("Erase Cache", key="--ERASE-CACHE--", default=False, tooltip="Erases the lighting caches, etc.\nSame option as when optimizing single player worlds."),
            sg.Checkbox("Force Upgrade", key="--FORCE-UPGRADE--", default=False, tooltip="Forces upgrade on all the chunks, such that the data version of all chunks matches the current server version (same as with sp worlds).\nThis option significantly increases the time needed to start the server."),
            sg.Checkbox("Safe Mode", key="--SAFE-MODE--", default=False, tooltip="Loads level with vanilla datapack only.")
        ],
        [
            sg.Checkbox("Demo Mode", key="--DEMO-MODE--", default=False, tooltip="If the server is in demo mode. (Shows the players a demo pop-up, and players cannot break or place blocks or eat if the demo time has expired).\nEquivalent to playing Minecraft without an account, you have about 5 in-game days before your trial ends."),
            sg.Checkbox("Online Authentication", key="--ONLINE-AUTHENTICATION--", default=False, tooltip="To tell the server to run in online mode so only authenticated users can join.\nNo cracked accounts are allowed to join."),
            sg.Checkbox("Auto Restart", key="--AUTO-RESTART--", default=False, tooltip="If the server should automatically restart when it crashes."),
        ],
        [
            sg.Text("Other arguments:"),
            sg.Input(key="--OTHER-ARGUMENTS--")
        ],
        [sg.Text("For more info click me!", enable_events=True, key="--MORE-INFO--")]
        ]

    layout = [
        [sg.TabGroup([[sg.Tab("General", tab1_layout), sg.Tab("Server Properties", tab2_layout), sg.Tab("Start settings", tab3_layout)]], expand_x=True)],
        [sg.Button("Create server")]
        ]

    window = sg.Window("Minecraft Server Maker", layout, resizable=True, icon="MMA.ico", finalize=True)

    settings.add("window", window)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            window.close()
            os._exit(0)
        elif event == "--POPUP--":
            sg.popup(values[event]["text"], title=values[event]["title"], icon="MMA.ico")
        elif event == "--POPUP-ERROR--":
            sg.popup_error(values[event]["text"], title=values[event]["title"], icon="MMA.ico")
        elif event == "--DROPDOWN-VERSIONS--":
            window["--DROPDOWN-BUILDS--"].update(values=sorted(get_builds(values["--DROPDOWN-VERSIONS--"]), reverse=True))
        elif event == "Create server" and "" in [values["--NAME--"], values["--DROPDOWN-VERSIONS--"], values["--DROPDOWN-BUILDS--"]]:
            sg.popup("Please fill in all fields", icon="MMA.ico")
            continue
        elif event == "Create server":
            if not values["--ACCEPT-EULA--"]:
                sg.popup_ok("You must accept the EULA to continue. You can read it there: https://account.mojang.com/documents/minecraft_eula", icon="MMA.ico")
                continue
            if os.path.exists(os.path.join(values["--FOLDER-PATH--"],values["--NAME--"])):
                answer = sg.popup_yes_no("A folder already exists with this name. It will erase it!\nDo you want to continue?", title="Do you want to continue?", icon="MMA.ico")
                if answer == "No":
                    continue
            server_properties = "".join(element[0].get() + element[1].get() + "\n" for element in column)
            settings.add("server_properties", server_properties)
            server_properties = settings.get("server_properties")
            settings.add("folder_name", values["--NAME--"])
            settings.add("minecraft_version", values["--DROPDOWN-VERSIONS--"])
            settings.add("folder_path", window["--FOLDER-PATH--"].get()+"\\")
            threading.Thread(target=setup_server, args=(get_download_url(values["--DROPDOWN-VERSIONS--"], values["--DROPDOWN-BUILDS--"]),)).start()
            layout_loading = [
                [sg.Image(sg.DEFAULT_BASE64_LOADING_GIF, key="--LOADING-IMAGE--")],
                [sg.Text("Creating server...", key="--LOADING-TEXT--")]
            ]
            loading_window = sg.Window("", layout_loading, modal=True, finalize=True, icon="MMA.ico", element_justification="center", disable_close=True)
            while True:
                loading_window.read(timeout=50)
                loading_window["--LOADING-IMAGE--"].update_animation(sg.DEFAULT_BASE64_LOADING_GIF, time_between_frames=100)
                event, values = window.read(timeout=50)
                if event == "--FINISHED--":
                    loading_window.close()
                    answer = sg.popup_ok("Server created!", icon="MMA.ico")
                    if answer == "OK":
                        # open the folder in the explorer
                        os.startfile(os.path.join(values["--FOLDER-PATH--"],values["--NAME--"]))
                    break
                elif event == "--POPUP-ERROR--":
                    sg.popup_error(values[event]["text"], title=values[event]["title"], icon="MMA.ico")
                    if values[event]["text"].startswith("Java is not installed!") or values[event]["text"].startswith("Java version is"):
                        if values[event]["text"].startswith("Java is not installed!"):
                            answer = sg.popup_yes_no("Java is not installed!\nDo you want to download it?", title="Java is not installed!", icon="MMA.ico")
                        else:
                            answer = sg.popup_yes_no("The version of Java is outdated!\nDo you want to download the latest version?", title="Your version of Java is outdated!", icon="MMA.ico")
                        if answer == "Yes":
                            webbrowser.open("https://adoptium.net")
                elif event == "--UPDATE--":
                    loading_window["--LOADING-TEXT--"].update("Creating server...\n" + values[event])
        elif (event == "--ENABLE-SYNC-RAM--" and values["--ENABLE-SYNC-RAM--"]) or (event == "--XMS--" and values["--ENABLE-SYNC-RAM--"]):
            window["--XMX--"].update(value=values["--XMS--"])
        elif event == "--XMX--" and values["--XMX--"] < values["--XMS--"]:
            window["--XMX--"].update(value=values["--XMS--"])
            sg.popup("XMX must be greater than XMS", icon="MMA.ico")
        elif event == "--XMS--" and values["--XMS--"] > values["--XMX--"]:
            window["--XMS--"].update(value=values["--XMX--"])
            sg.popup("XMS must be less than XMX", icon="MMA.ico")
        elif event == "--MORE-INFO--":
            webbrowser.open("https://minecraft.fandom.com/wiki/Tutorials/Setting_up_a_server#Java_options")
