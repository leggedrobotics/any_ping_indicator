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

from gi.repository import Gtk as gtk
from gi.repository import GdkPixbuf


class AboutDialog(gtk.AboutDialog):
    def __init__(self, icon_path):
        gtk.Window.__init__(self, title="Any Ping - About")
        self.set_icon_from_file(icon_path)
        # b = GdkPixbuf.Pixbuf.new_from_file(icon_path)
        b = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 100, 100, True)
        self.set_logo(b)
        self.set_license_type(gtk.License.BSD)
        self.set_copyright("@ ETH RSL 2016")
        self.set_authors(["Samuel Bachmann <samuel.bachmann@gmail.com>"])
        self.set_program_name("Any Ping")
        self.set_version("v0.7")
        self.set_website("http://www.rsl.ethz.ch")
        self.set_website_label("http://www.rsl.ethz.ch")
