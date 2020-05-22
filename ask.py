#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage:
ask [<msg>] [--yes=<reply_yes>] [--no=<reply_no>] [--engine=<tts-engine>]

Options:
    --engine=<str> TTS-engine to use {'google', 'espeak', 'festival'}
                   [default: espeak]
    --no=<str>     Message for negative answer
    --yes=<str>    Message for positive answer
    -h, --help     Print this
    --version      Print version

Examples:
    $ ask.py "Do you want to play a game?" && echo "Splendid! :)"
    $ ask.py "Do you want to play a game?" --yes="Splendid, let's play!" --no="Okidoki. Maybe another time."
"""
import logging
import sys
from docopt import docopt
from say import available_engines, ENGINE_DEFAULT, __version__, say

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler() # console-handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


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
    kwargs = docopt(__doc__, version=str('.'.join([str(el) for el in __version__])))
    logger.debug("kwargs={}".format(kwargs))
    if '<msg>' in kwargs:
        msg = kwargs['<msg>']
    reply_y = kwargs['--yes']
    reply_n = kwargs['--no']
    engine = kwargs['--engine']
    if not engine in available_engines():
        engine=ENGINE_DEFAULT
    if not msg:
        msg = input("what should i ask? : ".format(msg))
    say(msg,engine) #TODO better using a Thread here
    uinp = getch()
    logger.debug("answer was : {}".format(uinp))
    if uinp in ['y','Y','j','J']:
        if reply_y:
            say(reply_y,engine)
        sys.exit(0)
    else:
        if reply_n:
            say(reply_n,engine)
        sys.exit(1)

