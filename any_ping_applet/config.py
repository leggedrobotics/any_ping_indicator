################################################################################
# Copyright (C) 2015 by Samuel Bachmann                                        #
# samuel.bachmann@gmail.com                                                    #
#                                                                              #
# This program is free software; you can redistribute it and/or modify         #
# it under the terms of the Lesser GNU General Public License as published by  #
# the Free Software Foundation; either version 3 of the License, or            #
# (at your option) any later version.                                          #
#                                                                              #
# This program is distributed in the hope that it will be useful,              #
# but WITHOUT ANY WARRANTY; without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 #
# Lesser GNU General Public License for more details.                          #
#                                                                              #
# You should have received a copy of the Lesser GNU General Public License     #
# along with this program. If not, see <http://www.gnu.org/licenses/>.         #
################################################################################

import os
import json

from .ping_containers import PingObjectTuple

__CONFIG_FILE_PATH = os.path.expanduser("~/.any_ping_applet")
__AUTOSTART_FILE_PATH = os.path.expanduser("~/.config/autostart/")
__AUTOSTART_FILE_NAME = "any_ping_applet.desktop"

autostart_file_path = __AUTOSTART_FILE_PATH
autostart_file_name = __AUTOSTART_FILE_NAME
ping_object_tuples = []
check_for_updates = True
autostart = True
ping_warning = 50.0


def __load():
    """Load the config (json format) from file.
    :return:
    """
    global ping_object_tuples
    global check_for_updates
    global autostart
    global ping_warning

    if not os.path.isfile(__CONFIG_FILE_PATH):
        print("no such config file")
        ping_object_tuple = PingObjectTuple("", "8.8.8.8", 1.0, 1, True, True,
                                            True)
        ping_object_tuples.append(ping_object_tuple)
        return

    with open(__CONFIG_FILE_PATH, 'r') as config_file:
        config_dict = json.load(config_file)

    counter = 0
    while config_dict.get(str(counter)) is not None:
        # print(config_dict.get(str(counter))["address"])
        # print(type(config_dict.get(str(counter))))
        config = config_dict.get(str(counter))
        name = ""
        if "name" in config:
            name = config["name"]
        address = "8.8.8.8"
        if "address" in config:
            address = config["address"]
        update_rate = 1.0
        if "update_rate" in config:
            update_rate = config["update_rate"]
        number_of_pings = 1
        if "number_of_pings" in config:
            number_of_pings = config["number_of_pings"]
        show_indicator = True
        if "show_indicator" in config:
            show_indicator = config["show_indicator"]
        is_activated = True
        if "is_activated" in config:
            is_activated = config["is_activated"]
        show_text = True
        if "show_text" in config:
            show_text = config["show_text"]
        ping_object_tuple = PingObjectTuple(name,
                                            address,
                                            update_rate,
                                            number_of_pings,
                                            show_indicator,
                                            is_activated,
                                            show_text)
        ping_object_tuples.append(ping_object_tuple)
        counter += 1

    check_for_updates = config_dict.get("check_for_updates", True)

    autostart = config_dict.get("autostart", True)

    ping_warning = config_dict.get("ping_warning", 50.0)

    # global objects
    # global check_for_updates
    #
    # with open(__CONFIG_FILE_PATH, 'r') as config_file:
    #     config= yaml.load(config_file)
    #
    # for item in config["objects"]:
    #     ping_object = PingObject(item["address"],
    #                              item["show_indicator"],
    #                              item["number_of_pings"])
    #     objects.append(ping_object)


def persist():
    """Write the config (json format) to file.
    :return:
    """
    b = []
    for i in range(0, len(ping_object_tuples)):
        a = [i, {"name": ping_object_tuples[i].name,
                 "address": ping_object_tuples[i].address,
                 "update_rate": ping_object_tuples[i].update_rate,
                 "number_of_pings": ping_object_tuples[i].number_of_pings,
                 "show_indicator": ping_object_tuples[i].show_indicator,
                 "is_activated": ping_object_tuples[i].is_activated,
                 "show_text": ping_object_tuples[i].show_text}]
        b.append(a)
    b.append(["check_for_updates", check_for_updates])
    b.append(["autostart", autostart])
    b.append(["ping_warning", ping_warning])
    # print(b)
    with open(__CONFIG_FILE_PATH, 'w') as config_file:
        json.dump(dict(b), config_file)


__load()
