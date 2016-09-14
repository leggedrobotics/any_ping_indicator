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
import os
import signal
import subprocess
import threading
import time

from collections import namedtuple

from gi.repository import Gtk as gtk
from gi.repository import GObject

from . import resource
from . import theme

RESULT_OK = 0
RESULT_FAILED = 1
RESULT_NO_RESPONSE = 2

PingStruct = namedtuple("PingStruct", "result min max avg loss")


class PingObject(GObject.GObject):
    """Ping class.
    """
    def __init__(self, id, address, update_rate, number_of_pings,
                 show_indicator, is_activated=None):
        """Initialize.
        :param id:
        :param address:
        :param update_rate:
        :param number_of_pings:
        :param show_indicator:
        :param is_activated:
        """
        # init gobject
        GObject.GObject.__init__(self)
        GObject.type_register(PingObject)
        GObject.threads_init()
        # ping object properties
        self.id = id
        self.address = address
        self.update_rate = update_rate
        self.number_of_pings = number_of_pings
        self.show_indicator = show_indicator
        if is_activated is None:
            self.is_activated = True
        else:
            self.is_activated = is_activated
        self.icon = "icon_red"
        if not self.is_activated:
            self.icon = "icon_grey"
        self.ping_warning = 50.0
        # indicator menu item
        self.menu_item = gtk.ImageMenuItem("Ping: " + address)
        # result
        self.result = PingStruct(RESULT_NO_RESPONSE, 0.0, 0.0, 0.0, 0.0)
        # gtk image for menu item
        self.image = gtk.Image()
        self.image.set_from_file(resource.image_path("icon_gray", theme.THEME))
        # ping state
        self.state = "Ping: " + self.address + " initializing."
        # store subprocess
        self.process = None
        # mutex
        self.mutex = threading.Lock()
        # thread
        self.thread = None
        self.is_running = False
        # interruptable sleep function
        self.stop_event = threading.Event()
        # current time
        self.time_last = time.time()

    # signal definition returns (id, address, icon name, show_indicator)
    __gsignals__ = {
        'update': (GObject.SIGNAL_RUN_FIRST, None, (int, str, str, bool, ))
    }

    def set_ping_warning(self, ping_warning):
        """
        Set new ping warning value.
        :param ping_warning:
        :return:
        """
        self.ping_warning = ping_warning

    def loop(self):
        """Ping loop that runs in a thread.
        :return:
        """
        while self.is_running:
            if not self.is_activated:
                self.rate_sleep(self.update_rate)
                continue
            self.update()
            self.rate_sleep(self.update_rate)

    def rate_sleep(self, rate):
        """Sleep the rest of the time.
        :param rate:
        :return:
        """
        elapsed = time.time() - self.time_last
        time_sleep = rate - elapsed
        if time_sleep > 0.0:
            # interruptable sleeping function
            self.stop_event.wait(time_sleep)
        self.time_last = time.time()

    def stop(self):
        """Join the thread. Kill the running subprocess and interrupt the sleeping.
        :return:
        """
        self.is_running = False
        if self.thread is not None:
            # kill subprocess
            if self.process is not None:
                print("kill process")
                try:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                except ProcessLookupError as e:
                    print(e)
            # interrupt sleeping
            self.stop_event.set()
            self.stop_event = None
            self.thread.join()
            self.thread = None

    def start(self):
        """Start the thread (loop).
        :return:
        """
        if self.thread is None:
            if self.stop_event is None:
                self.stop_event = threading.Event()
            self.is_running = True
            self.thread = threading.Thread(target=self.loop)
            self.thread.setDaemon(True)
            self.thread.start()

    def update(self):
        """Ping the address. Update the menu item. Emit a signal to update the
        indicator icon.
        :return:
        """
        # ping by using subprocess
        self.process = subprocess.Popen(['ping', '-c',
                                         str(self.number_of_pings),
                                         self.address],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        preexec_fn=os.setsid)
        # wait for the result
        output = self.process.communicate()
        result = self.process.wait()
        self.process = None
        # create result
        if result == 0:
            output = output[0].decode("utf-8")
            output = output.split('\n')
            xmit_stats = output[len(output) - 3].split(",")
            timing_stats = output[len(output) - 2].split("=")[1].split("/")
            loss = float(xmit_stats[2].split("%")[0])
            min = float(timing_stats[0])
            avg = float(timing_stats[1])
            max = float(timing_stats[2])

            self.result = PingStruct(RESULT_OK, min, max, avg, loss)
        elif result == 2:
            self.result = PingStruct(RESULT_NO_RESPONSE, 0.0, 0.0, 0.0, 0.0)
        else:
            self.result = PingStruct(RESULT_FAILED, 0.0, 0.0, 0.0, 0.0)
        # update menu item properties (image and state)
        self.image = gtk.Image()
        if self.is_activated:
            if self.result.result == RESULT_OK:
                if self.result.avg > self.ping_warning:
                    self.icon = "icon_orange"
                    img_str = resource.image_path(self.icon, theme.THEME)
                else:
                    self.icon = "icon_green"
                    img_str = resource.image_path(self.icon, theme.THEME)
                self.image.set_from_file(img_str)
                self.state = " min: " + \
                             "{:.2f}".format(self.result.min) + "," + \
                             " avg: " + \
                             "{:.2f}".format(self.result.avg) + "," + \
                             " max: " + \
                             "{:.2f}".format(self.result.max) + "," + \
                             " package loss: " + \
                             "{:.1f}".format(self.result.loss)
            elif self.result.result == RESULT_FAILED:
                self.icon = "icon_red"
                img_str = resource.image_path(self.icon, theme.THEME)
                self.image.set_from_file(img_str)
                self.state = " failed."
            elif self.result.result == RESULT_NO_RESPONSE:
                self.icon = "icon_red"
                img_str = resource.image_path(self.icon, theme.THEME)
                self.image.set_from_file(img_str)
                self.state = " no response."
        else:
            self.icon = "icon_grey"
            img_str = resource.image_path(self.icon, theme.THEME)
            self.image.set_from_file(img_str)
            self.state = " inactive."
        # emit signal to update indicator icon
        self.emit('update', copy.copy(self.id),
                  copy.copy(self.address),
                  copy.copy(self.icon),
                  copy.copy(self.show_indicator))
        # update menu item
        self.update_menu_item()

    def update_menu_item(self):
        """Update the menu item.
        :return:
        """
        GObject.idle_add(
            self.menu_item.set_label,
            "Ping: " + self.address + self.state,
            priority=GObject.PRIORITY_HIGH
        )
        GObject.idle_add(
            self.menu_item.set_image,
            self.image,
            priority=GObject.PRIORITY_HIGH
        )
        GObject.idle_add(
            self.menu_item.show,
            priority=GObject.PRIORITY_HIGH
        )

    def on_show_indicator(self, item):
        """Emit signal to update indicator icon.
        :param item:
        :return:
        """
        self.show_indicator = item.get_active()
        self.emit('update', copy.copy(self.id),
                  copy.copy(self.address),
                  copy.copy(self.icon),
                  copy.copy(self.show_indicator))

    def on_activate(self, item):
        """Update menu item and emit signal to update indicator icon.
        :param item:
        :return:
        """
        self.is_activated = item.get_active()
        if self.is_activated:
            self.icon = "icon_red"
            img_str = resource.image_path(self.icon, theme.THEME)
            self.image.set_from_file(img_str)
            self.state = " waiting..."
        else:
            self.stop()
            self.icon = "icon_grey"
            img_str = resource.image_path(self.icon, theme.THEME)
            self.image.set_from_file(img_str)
            self.state = " inactive."

        self.update_menu_item()

        self.emit('update', copy.copy(self.id),
                  copy.copy(self.address),
                  copy.copy(self.icon),
                  copy.copy(self.show_indicator))

        if self.is_activated:
            self.start()
