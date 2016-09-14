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

import copy
import errno
import json
import os
import shutil
import signal
import threading

try:
    # For Python 3.0 and later
    from urllib.request import Request, urlopen, URLError
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import Request, urlopen, URLError

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify
from gi.repository import GObject

import svgutils.transform as sg

from . import config
from . import resource
from . import theme
from .about_dialog import AboutDialog
from .ping_object import PingObject
from .ping_containers import PingObjectTuple, IconTuple
from .preferences_window import PreferencesWindow

APPINDICATOR_ID = 'any_ping_applet'


class AnyPingIndicator(GObject.GObject):
    """Indicator class.
    """
    def __init__(self):
        """Initialize the indicator.
        """
        # initialize gobject
        GObject.GObject.__init__(self)
        GObject.type_register(AnyPingIndicator)
        GObject.threads_init()
        # initialize mutex
        self.mutex = threading.Lock()
        # icon counter to get different icon names
        self.icon_count = 0
        # list of icon tuples
        self.list_of_icon_tuple = []
        # get ping objects from config
        self.ping_objects_tuple = config.ping_object_tuples
        self.ping_objects = []
        count = 0
        for item in self.ping_objects_tuple:
            self.ping_objects.append(PingObject(count,
                                                item.address,
                                                item.update_rate,
                                                item.number_of_pings,
                                                item.show_indicator,
                                                item.show_text,
                                                item.is_activated))
            self.ping_objects[count].set_ping_warning(config.ping_warning)
            count += 1
        # update list of icon tuples
        self.update_list_of_icon_tuples()
        # init windows variables
        self.preferences_window = None
        self.about_dialog = None
        # check autostart
        self.check_autostart()
        # initialize notification
        notify.init(APPINDICATOR_ID)
        # initialize and build indicator menu
        self.menu = gtk.Menu()
        self.build_menu()
        # initialize indicator
        self.indicator = appindicator.Indicator.new(APPINDICATOR_ID,
                resource.image_path("icon_red", theme.THEME),
                appindicator.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.menu)
        # update indicator icon
        self.update_indicator_icon()
        # start ping objects
        self.start_ping_objects()

    def start_ping_objects(self):
        """Start all ping objects.
        :return:
        """
        for item in self.ping_objects:
            item.connect("update", self.update_indicator_icon_slot)
            if item.is_activated:
                item.start()

    def stop_ping_objects(self):
        """Stop all ping objects.
        :return:
        """
        for item in self.ping_objects:
            item.disconnect_by_func(self.update_indicator_icon_slot)
            item.stop()

    def update_list_of_icon_tuples(self):
        """Update list of icon tuples.
        :return:
        """
        self.list_of_icon_tuple = []
        for item in self.ping_objects:
            t = IconTuple(item.id, item.address, "icon_grey",
                          item.show_indicator, item.show_text)
            self.list_of_icon_tuple.append(t)

    def update_indicator_icon(self):
        """Update the indicator icon depending on the list of icon tuples.
        :return:
        """
        # count how many ping status go into the icon
        # count how many characters are required
        count = 0
        char_count = 0
        for i in range(0, len(self.list_of_icon_tuple)):
            if self.list_of_icon_tuple[i].show_indicator:
                count += 1
                if self.list_of_icon_tuple[i].show_text:
                    char_count += len(self.list_of_icon_tuple[i].address)
        if count == 0:
            # update indicator icon
            GObject.idle_add(
                self.indicator.set_icon,
                resource.image_path_type("icon.png", theme.THEME),
                priority=GObject.PRIORITY_DEFAULT
            )
            return
        # create new SVG figure
        character_width = 55
        disk_width = 135
        width = count * disk_width + char_count * character_width
        fig = sg.SVGFigure(str(width) + "px", "128px")
        # generate the plots and texts
        plots = []
        texts = []
        txt_position = 0
        disk_position = 0
        for i in range(0, len(self.list_of_icon_tuple)):
            if self.list_of_icon_tuple[i].show_indicator:
                # get the address length
                txt_length = 0
                if self.list_of_icon_tuple[i].show_text:
                    txt_length = len(self.list_of_icon_tuple[i].address) * \
                                 character_width
                # load the figure from file
                fig_1 = sg.fromfile(
                    resource.image_path(self.list_of_icon_tuple[i].icon,
                                        theme.THEME))
                # get the plot
                plot_1 = fig_1.getroot()
                plot_1.moveto(disk_position, 0, scale=1.0)
                # add the plot to the list
                plots.append(plot_1)
                # update next disk position
                disk_position += disk_width + txt_length
                # update text position
                txt_position += disk_width
                # generate text element
                if self.list_of_icon_tuple[i].show_text:
                    txt = sg.TextElement(txt_position, 100,
                                         self.list_of_icon_tuple[i].address,
                                         size=90, weight="regular", font="Courier",
                                         color="white")
                    # add the text to the list
                    texts.append(txt)
                # update text position
                txt_position += txt_length

        # append plots and labels to figure
        fig.append(plots)
        fig.append(texts)
        # print(fig.to_str().decode("utf-8"))
        # save generated SVG files
        fig.save("/tmp/any_ping_indicator" + str(self.icon_count) + ".svg")
        # update indicator icon
        GObject.idle_add(
            self.indicator.set_icon,
            "/tmp/any_ping_indicator" + str(self.icon_count) + ".svg",
            priority=GObject.PRIORITY_DEFAULT
        )
        # update icon count
        self.icon_count += 1
        self.icon_count %= 5

    def update_indicator_icon_slot(self, ping_object, id, address, icon,
                                   show_indicator, show_text):
        """Function to update the indicator icon with new ping object status.
        :param ping_object: Unused, but provided by the signal call. It is not
        thread save to use this object.
        :param id: ID of the ping object.
        :param address: Address of the ping object.
        :param icon: Icon string of the ping object.
        :param show_indicator: Boolean to add/not add the status to the icon.
        :param show_text:
        :return: None.
        """
        # acquire mutex
        self.mutex.acquire()
        # copy the icon tuple list
        list_of_icon_tuple = copy.copy(self.list_of_icon_tuple)
        # update the list entry that is matching the id
        for i in range(0, len(list_of_icon_tuple)):
            if list_of_icon_tuple[i].id == id:
                list_of_icon_tuple[i] = IconTuple(id, address, icon,
                                                  show_indicator, show_text)
                break
        # check if list is different,
        # if not, no update required, release mutex and return
        if list_of_icon_tuple == self.list_of_icon_tuple:
            self.mutex.release()
            return
        # assign updated list
        self.list_of_icon_tuple = list_of_icon_tuple
        # update indicator icon
        self.update_indicator_icon()
        # release mutex
        self.mutex.release()

    def run(self):
        """Run the GTK main loop.
        :return:
        """
        gtk.main()

    def build_menu(self):
        """Build the indicator menu.
        :return:
        """
        # new menu
        self.menu = gtk.Menu()
        # joke
        item_joke = gtk.MenuItem('Joke')
        item_joke.connect('activate', self.joke)
        self.menu.append(item_joke)
        # separator
        self.menu.append(gtk.SeparatorMenuItem("Pings"))
        # ping states
        i = 0
        for item in self.ping_objects:
            img_name = "icon_red"
            state = " no response."
            if not item.is_activated:
                img_name = "icon_grey"
                state = " inactive."
            img = gtk.Image()
            img.set_from_file(resource.image_path(img_name, theme.THEME))
            item.menu_item.set_label("Ping: " + item.address + state)
            item.menu_item.set_image(img)
            item.menu_item.set_always_show_image(True)
            self.menu.append(item.menu_item)
            # generate submenu
            submenu = gtk.Menu()
            # submenu entry to hide ping status from indicator icon
            submenu_item_show_indicator = \
                gtk.CheckMenuItem("Show indicator",
                                  active=
                                  self.ping_objects[i].show_indicator)
            submenu_item_show_indicator.connect("activate",
                    self.ping_objects[i].on_show_indicator)
            submenu.append(submenu_item_show_indicator)
            # submenu entry to hide address text from indicator icon
            submenu_item_show_text = \
                gtk.CheckMenuItem("Show text",
                                  active=
                                  self.ping_objects[i].show_text)
            submenu_item_show_text.connect("activate",
                                           self.ping_objects[i].on_show_text)
            submenu.append(submenu_item_show_text)
            # submenu to activate/deactivate the ping
            submenu_item_activate = \
                gtk.CheckMenuItem("Activate",
                                  active=
                                  self.ping_objects[i].is_activated)
            submenu_item_activate.connect("activate",
                                          self.ping_objects[i].on_activate)
            submenu.append(submenu_item_activate)
            # add submenu to ping entry
            item.menu_item.set_submenu(submenu)
            # increment i
            i += 1
        # separator
        self.menu.append(gtk.SeparatorMenuItem("Options"))
        # preferences
        item_pref = gtk.MenuItem('Preferences')
        item_pref.connect('activate', self.open_preferences)
        self.menu.append(item_pref)
        # about
        item_about = gtk.MenuItem('About')
        item_about.connect('activate', self.open_about)
        self.menu.append(item_about)
        # quit
        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', self.quit)
        self.menu.append(item_quit)
        # show menu
        self.menu.show_all()

    def check_autostart(self):
        """
        Check if autostart is enabled/disabled.
        :return:
        """
        if config.autostart:
            if not os.path.isfile(os.path.join(config.autostart_file_path,
                                               config.autostart_file_name)):
                try:
                    os.makedirs(config.autostart_file_path)
                except OSError as exception:
                    if exception.errno != errno.EEXIST:
                        raise
                shutil.copy(
                    resource.autostart_desktop_file_path("any_ping_applet"),
                    config.autostart_file_path)
        else:
            if os.path.isfile(os.path.join(config.autostart_file_path,
                                           config.autostart_file_name)):
                os.remove(os.path.join(config.autostart_file_path,
                                       config.autostart_file_name))

    def open_preferences(self, _):
        """Open the preferences window.
        :param _:
        :return:
        """
        if self.preferences_window is not None:
            return
        self.preferences_window = PreferencesWindow(
            resource.image_path_type("icon.png", theme.THEME),
            self.ping_objects, config.autostart, config.ping_warning)
        self.preferences_window.connect("delete-event", self.close_preferences)
        self.preferences_window.show_all()

    def open_about(self, _):
        """Open the about window.
        :param _:
        :return:
        """
        if self.about_dialog is not None:
            return
        self.about_dialog = AboutDialog(
            resource.image_path_type("icon.png", theme.THEME))
        self.about_dialog.connect('response', self.close_about)
        self.about_dialog.run()

    def close_preferences(self, preference_window, event):
        """Called when the preference window is closed. Destroy (close) the
        window. Update the menu and restart the ping threads. Store the
        configuration.
        :param preference_window:
        :param event:
        :return:
        """
        # update config
        self.ping_objects = preference_window.preferences
        config.autostart = preference_window.autostart
        config.ping_warning = preference_window.ping_warning
        # close preference window
        self.preferences_window.destroy()
        self.preferences_window = None
        # refresh indicator
        self.mutex.acquire()
        # update list of icon tuples
        self.update_list_of_icon_tuples()
        # update indicator icon
        self.update_indicator_icon()
        # build indicator menu
        self.build_menu()
        # set indicator menu
        self.indicator.set_menu(self.menu)
        self.mutex.release()
        # start ping threads
        self.start_ping_objects()
        # check autostart
        self.check_autostart()
        # store config
        self.store_config()

    def close_about(self, _0, _1):
        """Called when the about window is closed. Destroy (close) the window.
        :param _0:
        :param _1:
        :return:
        """
        self.about_dialog.destroy()
        self.about_dialog = None

    def fetch_joke(self):
        """Get a joke from icndb.com
        :return:
        """
        request = Request('http://api.icndb.com/jokes/random?limitTo=[nerdy]'
                          '&firstName=&lastName=Remo')
        response = urlopen(request)
        raw_response = response.read()
        joke = json.loads(raw_response.decode())['value']['joke']
        return joke

    def joke(self, _):
        """Display a joke notification.
        :param _:
        :return:
        """
        notify.Notification.new("<b>Joke</b>", self.fetch_joke(),
                                resource.image_path_type("chuck_norris_2.jpg",
                                                         theme.THEME)).show()

    def store_config(self):
        """Store the current configuration.
        :return:
        """
        # create a new list from the ping object list
        ping_object_tuples = []
        for item in self.ping_objects:
            t = PingObjectTuple(item.address,
                                item.update_rate,
                                item.number_of_pings,
                                item.show_indicator,
                                item.is_activated,
                                item.show_text)
            ping_object_tuples.append(t)
        # assign the list to config and store to file
        config.ping_object_tuples = []
        config.ping_object_tuples = ping_object_tuples
        config.persist()

    def quit(self, source):
        """Exit the indicator. Stop all the ping objects. Store the current
        configuration.
        :param source:
        :return:
        """
        # stop all ping objects
        for item in self.ping_objects:
            item.stop()
        #
        notify.uninit()
        # store config
        self.store_config()
        # exit
        gtk.main_quit()


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    AnyPingIndicator().run()


if __name__ == "__main__":
    main()
