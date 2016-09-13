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

from gi.repository import Gtk as gtk

from . import resource


class PingEditDialog(gtk.Dialog):
    """Edit/add dialog.
    """
    def __init__(self, parent, preference):
        gtk.Dialog.__init__(self, "Edit ping...", parent, 0,
                            (gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL,
                             gtk.STOCK_OK, gtk.ResponseType.OK))

        self.set_position(gtk.WindowPosition.CENTER)

        # set ui to dialog
        builder = gtk.Builder()
        file_path = os.path.dirname(os.path.abspath(__file__))
        builder.add_from_file(resource.ui_path("ping_edit_dialog"))
        self.box1 = builder.get_object('box1')
        self.box = self.get_content_area()
        self.box.add(self.box1)

        # get ui elements
        self.entry_address = builder.get_object("entry_address")
        self.spinbutton_update_rate = \
            builder.get_object("spinbutton_update_rate")
        self.spinbutton_number_of_pings = \
            builder.get_object("spinbutton_number_of_pings")
        self.radiobutton_yes = builder.get_object("radiobutton_yes")
        self.radiobutton_no = builder.get_object("radiobutton_no")
        self.radiobutton_activate_yes = \
            builder.get_object("radiobutton_activate_yes")
        self.radiobutton_activate_no = \
            builder.get_object("radiobutton_activate_no")

        # set data
        self.entry_address.set_text(preference[0])
        self.spinbutton_update_rate.set_value(preference[1])
        self.spinbutton_number_of_pings.set_value(preference[2])
        if preference[3]:
            self.radiobutton_yes.set_active(True)
        else:
            self.radiobutton_no.set_active(True)
        if preference[4]:
            self.radiobutton_activate_yes.set_active(True)
        else:
            self.radiobutton_activate_no.set_active(True)

        # show dialog
        self.show_all()
