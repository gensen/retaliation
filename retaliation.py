#!/bin/env python

# Borrowed heavily from Retaliation from codedance (http://github.com/codedance/Retaliation)

import sys
import platform
import time
import socket
import urllib
import re
import json

import usb.core
import usb.util

COMMAND_SETS = {
    "yung" : (
        ("zero", 0),
        ("right", 5000),
        ("up", 3000),
        ("fire", 1),
        ("zero", 0),
        ),
    "dan" : (
        ("zero", 0),
        ("right", 4500),
        ("up", 2500),
        ("fire", 1),
        ("zero", 0),
        ),
    "aaron": (
        ("zero", 0),
        ("right", 3000),
        ("up", 2500),
        ("fire", 1),
        ("zero", 0),
        ),
    "jon": (
        ("zero", 0),
        ("right", 2000),
        ("up", 2500),
        ("fire", 1),
        ("zero", 0),
        ),
    "phil": (
        ("zero", 0),
        ("right", 750),
        ("up", 4000),
        ("fire", 1),
        ("zero", 0),
        ),
    "antony": (
        ("zero", 0),
        ("right", 14000),
        ("up", 4000),
        ("fire", 1),
        ("zero", 0),
        )
    }

NOTIFICATION_UDP_PORT = 22222

DEVICE = None

DOWN = 1 << 0
UP = 1 << 1
LEFT = 1 << 2
RIGHT = 1 << 3
FIRE = 1 << 4
STOP = 1 << 5

def usage():
    print "Usage: retaliation.py [command] [value]"
    print ""
    print "   commands:"
    print "     stalk - sit around waiting for a "
    print "             notification, then attack the victim!"
    print ""
    print "     up    - move up <value> milliseconds"
    print "     down  - move down <value> milliseconds"
    print "     right - move right <value> milliseconds"
    print "     left  - move left <value> milliseconds"
    print "     fire  - fire <value> times (between 1-4)"
    print "     zero  - park at zero position (bottom-left)"
    print "     pause - pause <value> milliseconds"
    print ""
    print "     <command_set_name> - run/test a defined COMMAND_SET"
    print "             e.g. run:"
    print "                  retaliation.py 'chris'"
    print "             to test targeting of chris as defined in your command set."
    print ""

def setup_usb():
        global DEVICE
        DEVICE = usb.core.find(idVendor=0x0a81, idProduct=0x0701)

        if DEVICE is None:
                raise ValueError('Missile device not found')

        DEVICE.set_configuration()

def send_cmd(cmd):
        DEVICE.ctrl_transfer(0x21, 0x09, 0, 0, [cmd])

def send_move(cmd, duration_ms):
        send_cmd(cmd)
        time.sleep(duration_ms / 1000.0)
        send_cmd(STOP)

def run_command(command, value):
        command = command.lower()
        if command == "right":
                send_move(RIGHT, value)
        elif command == "left":
                send_move(LEFT, value)
        elif command == "up":
                send_move(UP, value)
        elif command == "down":
                send_move(DOWN, value)
        elif command == "zero" or command == "park" or command == "reset":
                send_move(DOWN, 2000)
                send_move(LEFT, 8000)
        elif command == "pause" or command == "sleep":
                time.sleep(value / 1000.0)
        elif command == "fire" or command == "shoot":
                if value < 1 or value > 4:
                        value = 1
                # stabilize prior to the shot, then allow for reload time after
                time.sleep(0.5)
                for i in range(value):
                        send_cmd(FIRE)
                        time.sleep(4.5)
        else:
                print "Error: unknown command: '%s'" % command

def run_command_set(commands):
        for cmd, value in commands:
                run_command(cmd, value)

def target_user(user):
        # Not efficient but our user list is probably less than 1k.
        # Do a case insenstive search for convenience.
        for key in COMMAND_SETS:
                print "Checking against key %s" % key
                if key.lower() == user.lower():
                        # We have a command set that targets our user so got for it!
                        run_command_set(COMMAND_SETS[key])
                        match = True
                        break
        if not match:
            print "WARNING: No target command set defined for user %s" % user


def wait_for_event():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', NOTIFICATION_UDP_PORT))

        while True:
                data, addr = sock.recvfrom(8 * 1024)
                try:
                        notification_data = json.loads(data)
                        victim = notification_data["victim"]

                        print "Targeting victim: " + victim
                        target_user(victim)
                except:
                        pass

def main(args):
        if len(args) < 2:
                usage()
                sys.exit(1)

        setup_usb()

        if args[1] == "stalk":
                print "Listening and waiting for victims..."
                wait_for_event()
                return

        command = args[1]
        value = 0
        if len(args) > 2:
                value = int(args[2])

        if command in COMMAND_SETS:
                run_command_set(COMMAND_SETS[command])
        else:
                run_command(command, value)

if __name__ == '__main__':
        main(sys.argv)
