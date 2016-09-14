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
from gi.repository import Gdk as gdk

from . import resource
from .ping_object import PingObject
from .ping_edit_dialog import PingEditDialog


class PreferencesWindow(gtk.Window):
    """Preferences class.
    """
    def __init__(self, icon_path, preferences, autostart, ping_warning):
        """Initialize.
        :param icon_path:
        :param preferences:
        """
        # init gtk window
        gtk.Window.__init__(self, title="Any Ping - Preferences")
        self.set_icon_from_file(icon_path)
        self.set_border_width(10)
        self.set_default_size(500, 400)
        self.set_position(gtk.WindowPosition.CENTER)
        self.connect("delete-event", self.on_close)
        #
        self.icon_path = icon_path
        self.preferences = preferences
        self.autostart = autostart
        self.ping_warning = ping_warning
        # generate the list
        list_ping_objects = []
        for item in preferences:
            t = (item.address, item.update_rate, item.number_of_pings,
                 item.show_indicator, item.is_activated)
            list_ping_objects.append(t)
        # initialize the list store
        self.store = gtk.ListStore(str, float, int, bool, bool)
        for ref in list_ping_objects:
            self.store.append(list(ref))
        # initialize the tree view
        self.tree_view = gtk.TreeView.new_with_model(self.store)
        for i, column_title in enumerate(
                ["Address", "Update Rate", "Number of Pings", "Show Indicator",
                 "Activate"]):
            renderer = gtk.CellRendererText()
            column = gtk.TreeViewColumn(column_title, renderer, text=i)
            self.tree_view.append_column(column)
        # gui
        builder = gtk.Builder()
        file_path = os.path.dirname(os.path.abspath(__file__))
        builder.add_from_file(resource.ui_path("preferences_window"))
        # get main box
        self.box1 = builder.get_object('box1')
        # add main box to window
        self.add(self.box1)
        # get second box for the tree
        self.box2 = builder.get_object('box2')
        self.box2.pack_start(self.tree_view, True, True, 0)
        # get elements
        self.button_add = builder.get_object("button_add")
        self.button_remove = builder.get_object("button_remove")
        self.button_edit = builder.get_object("button_edit")
        self.button_up = builder.get_object("button_up")
        self.button_down = builder.get_object("button_down")
        self.checkbutton_autostart = builder.get_object("checkbutton_autostart")
        self.spinbutton_ping_warning = \
            builder.get_object("spinbutton_ping_warning")
        # set values
        self.checkbutton_autostart.set_active(self.autostart)
        self.spinbutton_ping_warning.set_value(self.ping_warning)
        # connect signal to slots
        handlers = {
            "on_button_add_clicked": self.on_button_add_clicked,
            "on_button_remove_clicked": self.on_button_remove_clicked,
            "on_button_edit_clicked": self.on_button_edit_clicked,
            "on_button_up_clicked": self.on_button_up_clicked,
            "on_button_down_clicked": self.on_button_down_clicked,
            "on_button_close_clicked": self.on_button_close_clicked
        }
        builder.connect_signals(handlers)
        # handle list selection
        self.selection = None
        select = self.tree_view.get_selection()
        select.connect("changed", self.on_tree_selection_changed)
        # show gui
        self.show_all()

    def on_close(self, _0, _1):
        """Called when the windows is closed. Generate a new list of ping
        objects.
        :param _0:
        :param _1:
        :return:
        """
        self.autostart = self.checkbutton_autostart.get_active()
        self.ping_warning = self.spinbutton_ping_warning.get_value()
        # generate new ping objects
        for item in self.preferences:
            item.stop()
        self.preferences = []
        count = 0
        for item in self.store:
            self.preferences.append(PingObject(count, item[0], item[1], item[2],
                                               item[3], item[4]))
            self.preferences[count].set_ping_warning(self.ping_warning)
            count += 1

    def on_button_add_clicked(self, _):
        """Called on add button clicked. Add a new item to the list.
        :param _:
        :return:
        """
        self.add_edit_ping(("", 1.0, 1, True, True), True)

    def on_button_remove_clicked(self, _):
        """Called on remove button clicked. Remove the selected item from the
        list.
        :param _:
        :return:
        """
        if self.selection is None or len(self.store) == 1:
            return
        model, tree_iter = self.selection.get_selected()
        self.store.remove(tree_iter)

    def on_button_edit_clicked(self, _):
        """Called on edit button clicked. Edit the selected item.
        :param _:
        :return:
        """
        if self.selection is None:
            return
        model, tree_iter = self.selection.get_selected()
        t = (model[tree_iter][0], model[tree_iter][1], model[tree_iter][2],
             model[tree_iter][3], model[tree_iter][4])
        self.add_edit_ping(t, False)

    def on_button_up_clicked(self, _):
        """Called on up button clicked. Move the selected item one position up.
        :param _:
        :return:
        """
        model, tree_iter = self.selection.get_selected()
        tree_iter_2 = model.get_iter(
            gtk.TreePath(str(int(model.get_path(tree_iter).to_string()) - 1)))
        model.swap(tree_iter, tree_iter_2)

        self.check_button_sensitive()

    def on_button_down_clicked(self, _):
        """Called on down button clicked. Move the selected item on position
        down.
        :param _:
        :return:
        """
        model, tree_iter = self.selection.get_selected()
        tree_iter_2 = model.get_iter(
            gtk.TreePath(str(int(model.get_path(tree_iter).to_string()) + 1)))
        model.swap(tree_iter, tree_iter_2)

        self.check_button_sensitive()

    def on_button_close_clicked(self, _):
        """Called on close button clicked. Emit close signal.
        :param _:
        :return:
        """
        self.emit("delete-event", gdk.Event(gdk.EventType.DELETE))

    def on_tree_selection_changed(self, selection):
        """Called when a list item is selected.
        :param selection:
        :return:
        """
        self.selection = selection

        self.check_button_sensitive()

    def check_button_sensitive(self):
        """Check the up, down and remove buttons and disable or enable them.
        Depending on the selected item.
        :return:
        """
        if self.selection is None:
            return

        model, tree_iter = self.selection.get_selected()

        self.button_up.set_sensitive(True)
        self.button_down.set_sensitive(True)
        self.button_remove.set_sensitive(True)

        if model.get_path(tree_iter) == gtk.TreePath("0"):
            self.button_up.set_sensitive(False)
        if model.get_path(tree_iter) == gtk.TreePath(str(len(model) - 1)):
            self.button_down.set_sensitive(False)
        if len(model) == 1:
            self.button_remove.set_sensitive(False)

    def add_edit_ping(self, preference, is_adding):
        """Open the add/edit dialog window.
        :param preference:
        :param is_adding:
        :return:
        """
        dialog = PingEditDialog(self, preference)
        response = dialog.run()

        if response == gtk.ResponseType.OK:
            address = dialog.entry_address.get_text()
            update_rate = dialog.spinbutton_update_rate.get_value()
            number_of_pins = dialog.spinbutton_number_of_pings.get_value()
            show_indicator = dialog.radiobutton_yes.get_active()
            is_activated = dialog.radiobutton_activate_yes.get_active()
            if is_adding:
                if address is not "":
                    t = (address, update_rate, number_of_pins, show_indicator,
                         is_activated)
                    self.store.append(t)
            else:
                model, tree_iter = self.selection.get_selected()
                model[tree_iter][0] = dialog.entry_address.get_text()
                model[tree_iter][1] = \
                    dialog.spinbutton_update_rate.get_value()
                model[tree_iter][2] = \
                    dialog.spinbutton_number_of_pings.get_value()
                model[tree_iter][3] = dialog.radiobutton_yes.get_active()
                model[tree_iter][4] = \
                    dialog.radiobutton_activate_yes.get_active()
        elif response == gtk.ResponseType.CANCEL:
            print("cancel")

        self.check_button_sensitive()

        dialog.destroy()
