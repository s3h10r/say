#!/usr/bin/env python3
"""
"""
import sys
from say import say

class _Getch:
    """Gets a single character from standard input. Does not echo to the screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()


if __name__ == '__main__':
    msg = 'Do you want to play a game?'
    if len(sys.argv) > 1:
        msg = sys.argv[1]
    else:
        uinp = input("what should i ask (default={}): ".format(msg))
        if uinp:
            msg = uinp
    say(msg=msg,engine='espeak') #TODO better using a Thread here
    uinp = getch()
    print("answer was : {}".format(uinp))
    if uinp in ['y','Y','j','J']:
        sys.exit(0)
    else:
        sys.exit(1)

