#!/usr/bin/env python3

import os
import sys
import dbus
import signal
import platform
import dbus.service
import dbus.mainloop.glib

from gi.repository import GLib
from dbus.exceptions import DBusException
# from dbus.service import method
from typing import Dict, List, Union
from keyszer.lib.logger import debug, error, warn, info, log

# Add paths to avoid errors like ModuleNotFoundError or ImportError
home_dir = os.path.expanduser("~")
# local_site_packages_dir = os.path.join(home_dir, f".local/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages")
parent_folder_path  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
current_folder_path = os.path.abspath(os.path.dirname(__file__))

sys.path.insert(0, current_folder_path)
sys.path.insert(0, parent_folder_path)

existing_path = os.environ.get('PYTHONPATH', '')
os.environ['PYTHONPATH'] = f'{parent_folder_path}:{current_folder_path}:{existing_path}'

# local imports
# from ..lib.env import get_env_info
import lib.env as env

# Independent module/script to create a D-Bus window context
# service in a KDE Plasma environment, which will be notified
# of window focus changes by KWin

if os.name == 'posix' and os.geteuid() == 0:
    error("This app should not be run as root/superuser.")
    sys.exit(1)

def signal_handler(sig, frame):
    """handle signals like Ctrl+C"""
    if sig in (signal.SIGINT, signal.SIGQUIT):
        # Perform any cleanup code here before exiting
        # traceback.print_stack(frame)
        debug(f'\nSIGINT or SIGQUIT received. Exiting.\n')
        sys.exit(0)

if platform.system() != 'Windows':
    signal.signal(signal.SIGINT,    signal_handler)
    signal.signal(signal.SIGQUIT,   signal_handler)
else:
    error(f'This is only meant to run on Linux. Exiting...')
    sys.exit(1)


# leave all of this alone!
DISTRO_NAME     = None
DISTRO_VER      = None
SESSION_TYPE    = None
DESKTOP_ENV     = None

env_info: Dict[str, str] = env.get_env_info()   # Returns a dict

DISTRO_NAME     = env_info.get('DISTRO_NAME')
DISTRO_VER      = env_info.get('DISTRO_VER')
SESSION_TYPE    = env_info.get('SESSION_TYPE')
DESKTOP_ENV     = env_info.get('DESKTOP_ENV')

debug("")
debug(  f'Toshy KDE D-Bus service script sees this environment:'
        f'\n\t{DISTRO_NAME      = }'
        f'\n\t{DISTRO_VER       = }'
        f'\n\t{SESSION_TYPE     = }'
        f'\n\t{DESKTOP_ENV      = }\n', ctx="CG")


TOSHY_KDE_DBUS_SVC_PATH         = '/org/toshy/Toshy'
TOSHY_KDE_DBUS_SVC_IFACE        = 'org.toshy.Toshy'


class DBUS_Object(dbus.service.Object):
    """Class to handle D-Bus interactions"""
    def __init__(self, session_bus, object_path, interface_name):
        super().__init__(session_bus, object_path)
        self.interface_name     = interface_name
        self.dbus_svc_bus_name  = dbus.service.BusName(interface_name, bus=session_bus)
        self.caption            = "NO_DATA"
        self.resource_class     = "NO_DATA"
        self.resource_name      = "NO_DATA"

    @dbus.service.method(TOSHY_KDE_DBUS_SVC_IFACE, in_signature='sss')
    def NotifyActiveWindow(self, caption, resource_class, resource_name):
        print(f'DBUS_SVC: NotifyActiveWindow() called...')
        self.caption            = str(caption)
        self.resource_class     = str(resource_class)
        self.resource_name      = str(resource_name)
        print(f'DBUS_SVC: Active window attributes:'
                f"\n\t'{caption = }'"
                f"\n\t'{resource_class = }'"
                f"\n\t'{resource_name = }'"
        )

    @dbus.service.method(TOSHY_KDE_DBUS_SVC_IFACE, out_signature='a{sv}')
    def GetActiveWindow(self):
        print(f'DBUS_SVC: GetActiveWindow() called...')
        return {    'caption':          self.caption,
                    'resource_class':   self.resource_class,
                    'resource_name':    self.resource_name }


def main():
    # Initialize the D-Bus main loop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    # Connect to the session bus
    session_bus = dbus.SessionBus()

    # Create the DBUS_Object
    try:
        DBUS_Object(session_bus, TOSHY_KDE_DBUS_SVC_PATH, TOSHY_KDE_DBUS_SVC_IFACE)
    except DBusException as dbus_error:
        print(f"DBUS_SVC: Error occurred while creating D-Bus service object:\n\t{dbus_error}")
        sys.exit(1)

    # Run the main loop
    # dbus.mainloop.glib.DBusGMainLoop().run()
    GLib.MainLoop().run()


if __name__ == "__main__":
    main()
