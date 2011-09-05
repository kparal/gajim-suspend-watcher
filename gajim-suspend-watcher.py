#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gajim does not intercept suspend signals correctly and stays online even when
computer is suspending. That leaves the user hanging 'online' for many minutes
but all incoming messages are lost. This script watches for suspend events and
changes Gajim's status to offline in that case. On system resume it changes
Gajim's previous status back. Have this script auto-started in your session.

License: GNU AGPL 3+
@author: Kamil Páral <kamil.paral _at_ gmail.com>
"""

import dbus
from dbus.mainloop.glib import DBusGMainLoop
import gobject
import time
import optparse
import sys

parser = optparse.OptionParser(description="Change Gajim's status to offline "
    "before system suspend and back to previous status on system resume. "
    "Have this auto-started with your system session.")
parser.add_option('-s', '--resume-status', help='Use this status after resume '\
                  'instead of last used status [valid values: online, chat, ' \
                  'away, xa, dnd, invisible, offline]', default=None,
                  metavar='STATUS')
(options, args) = parser.parse_args()

gajim_service = 'org.gajim.dbus'
gajim_obj = '/org/gajim/dbus/RemoteObject'
gajim_int = 'org.gajim.dbus.RemoteInterface'

upower_service = 'org.freedesktop.UPower'
upower_obj = '/org/freedesktop/UPower'
upower_int = 'org.freedesktop.UPower'

nm_service = 'org.freedesktop.NetworkManager'
nm_obj = '/org/freedesktop/NetworkManager'
nm_int = 'org.freedesktop.NetworkManager'
NM_STATE_CONNECTED_GLOBAL = 70 # NM 0.9
NM_STATE_CONNECTED = 3 # NM 0.8

DBusGMainLoop(set_as_default=True)

session_bus = dbus.SessionBus()
system_bus = dbus.SystemBus()

nm = system_bus.get_object(nm_service, nm_obj)
inm = dbus.Interface(nm, dbus_interface=nm_int)

last_status = 'offline'
should_connect = False

def get_igajim():
    try:
        gajim = session_bus.get_object(gajim_service, gajim_obj)
        igajim = dbus.Interface(gajim, dbus_interface=gajim_int)
        return igajim
    except dbus.exceptions.DBusException, ex:
        print >> sys.stderr, ex
        return None

def on_suspend(*args, **kwargs):
    igajim = get_igajim()
    if igajim is None:
        print '%s: Suspending, but Gajim not running' % time.asctime()
        return

    global last_status, should_connect
    if not should_connect:
        last_status = igajim.get_status('')
    igajim.change_status('offline', '', '')
    print '%s: Suspending, changing Gajim status to offline' % time.asctime()

def on_resume(*args, **kwargs):
    global should_connect
    print '%s: Resuming, now waiting for network to come up' % time.asctime()
    if not connect():
        should_connect = True

def connect(*args, **kwargs):
    global should_connect, last_status, options

    if not should_connect:
        return False

    if inm.state() != NM_STATE_CONNECTED_GLOBAL and inm.state() != NM_STATE_CONNECTED:
        print '%s: Network not connected, not changing Gajim status yet' % time.asctime()
        return False
    else:
        igajim = get_igajim()
        if igajim is None:
            print '%s: Network connected, but Gajim not running' % time.asctime()
        else:
            if options.resume_status:
                last_status = options.resume_status
            print '%s: Network connected, changing Gajim status to %s' % (time.asctime(), last_status)
            igajim.change_status(last_status, '', '')
        should_connect = False
        return True

system_bus.add_signal_receiver(signal_name='Sleeping', dbus_interface=upower_int,
                               handler_function=on_suspend)

system_bus.add_signal_receiver(signal_name='Resuming', dbus_interface=upower_int,
                               handler_function=on_resume)

system_bus.add_signal_receiver(signal_name='StateChanged', dbus_interface=nm_int,
                               handler_function=connect)

print 'Suspend monitoring started...'

loop = gobject.MainLoop()
loop.run()
