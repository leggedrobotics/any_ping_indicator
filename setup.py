#!/usr/bin/python3

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
from distutils.core import setup

from any_ping_applet.resource import RESOURCES_DIRECTORY_PATH


def find_resources(resource_dir):
    target_path = os.path.join(RESOURCES_DIRECTORY_PATH, resource_dir)
    resource_names = os.listdir(resource_dir)
    resource_list = [os.path.join(resource_dir, file_name) for file_name in
                     resource_names]
    return target_path, resource_list


setup(name="any_ping_indicator",
      version="0.7",
      description="Any Ping Indicator for Ubuntu",
      url='https://github.com/leggedrobotics/any_ping_indicator',
      author='Samuel Bachmann',
      author_email='samuel.bachmann@gmail.com',
      license='GPL',
      packages=["any_ping_applet"],
      data_files=[
          ('/usr/share/applications', ['any_ping_applet.desktop']),
          find_resources("img"),
          find_resources("ui")],
      scripts=["bin/any_ping_applet"],
      install_requires=[
          'svgutils'
      ]
      )
