"""Module for printing a block of text overwriting previous text."""

import sys
from threading import RLock


class Printer:
    """Reprints messages wiping unneeded lines. Supports multiple threads."""

    __rlock = RLock()

    def __init__(self, line_length=70):
        """Initialize object."""
        self.__msgs = {}
        self.__line_length = line_length

    def add_msg(self, key, msg):
        """Add a new message and print it on last line."""
        with self.__rlock:
            self.__msgs[key] = msg
            print(self.__msgs[key].ljust(self.__line_length, " "))

    def print_msg(self, msg):
        """Print a single message."""
        print(msg.ljust(self.__line_length, " "))

    def purge_msg(self, key, last_msg):
        """Print the last message on top active line and move lower."""
        with self.__rlock:
            self.__move_up()
            if key in self.__msgs:
                del self.__msgs[key]
            print(last_msg.ljust(self.__line_length, " "))
            self.__print_active(move_up=False)

    def __print_active(self, move_up=False):
        """Print all active messages overwriting console."""
        # Clear previous text by overwritig non-spaces with spaces
        if move_up:
            self.__move_up()
        for key in self.__msgs.keys():
            print(self.__msgs[key].ljust(self.__line_length, " "))

    def __move_up(self):
        """Move cursor to the top active line."""
        for _ in range(len(self.__msgs)):
            sys.stdout.write("\033[A")
