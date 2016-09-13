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

from os.path import join, dirname, isfile

RESOURCES_DIRECTORY_PATH = "/usr/share/any_ping_applet"

# when running any_ping_applet directly from sources
# use resources from source code
__RELATIVE_RESOURCE_PATH = join(dirname(dirname(__file__)))
__CURRENT_RESOURCES_PATH = \
    __RELATIVE_RESOURCE_PATH \
    if isfile(join(__RELATIVE_RESOURCE_PATH, "bin", "any_ping_applet")) else \
    RESOURCES_DIRECTORY_PATH


def image_path(name, theme):
    """Returns path to the image file by its name, in given theme library"""
    return join(__CURRENT_RESOURCES_PATH, "img", theme, "%s.svg" % name)


def image_path_type(name, theme):
    """Returns path to the image file by its name, in given theme library"""
    return join(__CURRENT_RESOURCES_PATH, "img", theme, "%s" % name)


def ui_path(name):
    """Returns path to the ui (glade) file by its name."""
    return join(__CURRENT_RESOURCES_PATH, "ui", "%s.glade" % name)
