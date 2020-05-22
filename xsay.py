#!/usr/bin/env python3
"""
a graphical retro-style version of `say`. because we can. :D

**experimental**
"""
import logging
import os
import subprocess
import sys
import threading
import time
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1' # no "Hello from the pygame community..." on stdout.
try:
    import pygame
    import pygame.freetype
    from pygame.locals import *
except ImportError:
    print("whuuups. no pygame import possible?")
    sys.exit(1)
from say import say

_DEBUG = False
__version__ = '0.1.0'

# --- configure logging
log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)
#log.setLevel(logging.INFO)

WINDOW_SIZE = (1200, 800)
FULLSCREEN=True # if set, the previously defined WINDOW_SIZE is ignored
#FULLSCREEN=False # if set, the previously defined WINDOW_SIZE is ignored
FONT_ZOOM=0.75
MARGIN = [0,0,0,0] # top, left, right, bottom
VT100 = (80,24) # https://de.wikipedia.org/wiki/VT100
#PAGE_SIZE=VT100
PAGE_SIZE=(20,6)

# === THEME / COLOR SCHEME
# --- day
#BACKGROUND_COLOR = (255,255,255)
#TEXT_COLOR = (0,0,0)
#CURSOR_COLOR=GRAY
# --- night
BACKGROUND_COLOR = (0,0,0)
TEXT_COLOR = (255,255,255)
CURSOR_COLOR= (0,128,0) # https://docs.oracle.com/cd/E19728-01/820-2550/term_em_colormaps.html
# === THEME / COLOR SCHEME


class ThreadWithReturnValue(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        threading.Thread.join(self, *args)
        return self._return


def _init_screen(fullscreen=FULLSCREEN):
    global MARGIN
    global WINDOW_SIZE
    log.info("_init_screen(fullscreen={})".format(fullscreen))
    pygame.init()
    pygame.mouse.set_visible(0)
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    infoObj = pygame.display.Info()
    w, h = infoObj.current_w, infoObj.current_h
    log.debug("w=%s h=%s" % (w,h))
    MARGIN = [WINDOW_SIZE[1] / 40, WINDOW_SIZE[0] / 20, WINDOW_SIZE[0] / 20, WINDOW_SIZE[1] / 40] # top, left, right, bottom
    if fullscreen:
        surface = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        WINDOW_SIZE = (w,h)
    else:
        surface = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption('xsay')
    return surface


def get_font_for_page(surface=None, page_size = (80,24), font = "FreeMono, Monospace", margin=(0,0,0,0), monospace=True):
    """
    calculates the (monospace) fontsize for page_size (<columns_char_N>,<rows_char_N>)

    returns FontInstance
    """
    assert(isinstance(font,str))
    font_name = font
    FONT_SIZE_MIN = 1
    width, height = surface.get_size()
    width -= MARGIN[1] + MARGIN[2]  # left + right
    height -= MARGIN[0] + MARGIN[3] # top + bottom
    font_size = 101
    ref_char = ' '
    assert(FONT_SIZE_MIN > 0)
    ref_size_x = None
    ref_size_y = None
    font = None
    running = True
    while running:
        if font_size > (FONT_SIZE_MIN + 1):
            font_size -= 1
        else:
            raise Exception("Ouch! Fontsize required for page_size={} < {} :-/".format(page_size,FONT_SIZE_MIN))
        font = pygame.freetype.SysFont(font_name, font_size)
        font.origin = True
        #ref_size_x = font.get_rect(ref_char).width
        ref_size_x = font.get_rect(ref_char).width + 1 # WORKAROUND: add one pixel per char to be safe ?
        ref_size_y = font.get_sized_height() + 2
        if (ref_size_x * page_size[0] > width) or (ref_size_y * page_size[1] > height):
            log.debug("fontsize={} : ref_char's size_x={} size_y={}".format(font_size, ref_size_x,ref_size_y))
            continue
        else: # got fitting fontsize
            running = False
            log.info("found fontsize={} (font={}) suiting for page_size={} # ref_char's ('{}') size_x={} size_y={}".format(font_size, font_name, page_size, ref_char, ref_size_x,ref_size_y))
    return font


def word_wrap(surf = None, text = None, stop_pos = None, font = None, color=(0, 0, 0), render=True):
    """
    throws text onto screen/surface (if render=True).

    if render is set to False only the positioning is calculated - handy
    for calculating the position of a cursor onto content already drawn
    by an earlier call (return values can be used for setting the cursor to a specific
    position (stop_pos) of the text)

    :args:

       text         a "page" as string which should be printed on durface
       stop_pos     the position in text where printing to surface shoud stop
                    (default == None == len(text)
       render       nothing is printed onto surface. but the positioning
                    calculations are done (see retunrn values)

    returns x,y # position of the last processed character of the text
                # (the x-position is the position where the pixelrepresentation of the char ends)

    **TODO: `color=random_color()` option**
    """
    assert(isinstance(render,bool))
    assert(isinstance(stop_pos,int) or stop_pos == None)
    if not(isinstance(stop_pos,int)):
        stop_pos = len(text) - 1
    pos = 0
    font.origin = True
    words = text.split(' ')
    width, height = surf.get_size()
    width -= MARGIN[1] + MARGIN[2]  # left + right
    height -= MARGIN[0] + MARGIN[3] # top + bottom
    line_spacing = font.get_sized_height() + 2
    x, y = MARGIN[1], line_spacing + MARGIN[0]
    space = font.get_rect(' ')
    #if stop_pos == 0:
    #    return x,y

    i_pos = -1 # position in text-stream
    linebreaks = 0 # nr. of linebreaks in text-stream
    lines = text.split('\n')
    trimmed = False # if stop_pos is reached we set this to true and end the loop
    for i, line in enumerate(lines):
        log.debug("line {} : '{}'".format(i, line))
        if len(line) > 0: # cause ''.split(' ') => ['']
            words = line.split(' ')
        else:
            words = []
        log.debug("words of line {}: {}".format(line, words))
        for i2, word in enumerate(words):
            log.debug("word_wrap-func line nr. {} word nr. {}".format(i,i2))
            if i2 < len(words) - 1:
                if set(words[i2+1:]) != set(['']): # FIX-20011822-01: don't append whitespace if last word in line only followed by whitespaces
                    word += ' '
            if stop_pos != None and (i_pos + len(word) >= stop_pos):
                log.debug("trimming word '{}' to pos length {} @ i_pos {}".format(word,stop_pos,i_pos))
                # trim word to pos length
                too_long = (i_pos + len(word)-1) - stop_pos
                tmpi = len(word) - too_long
                word = word[:tmpi]
                log.debug("trimmed to '{}' @ i_pos {}".format(word,i_pos))
                trimmed=True
            if word=='' and not trimmed:
                word = ' '
                log.debug("word == ' ' @ i_pos: {}".format(i_pos))
            i_pos += len(word)
            bounds = font.get_rect(word)
            log.debug("assume: {} <= {}".format(bounds.width,space.width * len(word)))
            if not (bounds.width <= (space.width * len(word))):
                log.debug("WARNING ASSERTION WRONG. MAYBE WE CAN USE A TRESHOLD IN WHICH IT IS OKAY?")
            log.debug('{}'.format(word))
            if x + bounds.width > width:
                x, y = MARGIN[1], y + line_spacing
            if x + bounds.width > width:
                raise ValueError("word {} px to wide (x) for the surface".format(width - (x + bounds.width)))
            else:
                log.debug("word width (x) fits into surface. {}px left".format(width - (x + bounds.width)))
            if y + bounds.height - bounds.y > height:
                log.critical("FIXME: text to long (y) for the surface")
                raise ValueError("text to long (y) for the surface")
            if render:
                log.debug("render word '{}' on pos {},{}".format(word, x,y))
                font.render_to(surf, (x, y), None, color)
            x += bounds.width
            if trimmed:
                break
        if trimmed:
            break
        # add linebreak
        if i < len(lines) - 1:
            x = MARGIN[1]; y += line_spacing
            i_pos += 1 # the '\n' of the .split()
            linebreaks += 1
    log.info("word_wrap: i_pos {} lines {} linebreaks done {}".format(i_pos,len(lines),linebreaks))
    log.info("word_wrap: i_pos={} stop_pos={} (should be same)".format(i_pos,stop_pos))
    if stop_pos < len(text):
        #assert(i_pos == stop_pos)
        assert(abs(i_pos - stop_pos) < 2)
        if abs(i_pos - stop_pos) >= 2:
            log.warning("word_wrap : abs(i_pos - stop_pos) is {} (but should be zero)".format(abs(i_pos - stop_pos)))
    return x, y


def show_message(surf=None, page="Do you want to play a game?", page_from_pos=0, show_cursor=True, wait_for_keypress=True):
    """
    shows message (question) char by char (full-)screen

    returns

        key pressed by user # e.g "y", "n"
    """
    SHOW_CURSOR=show_cursor
    font = get_font_for_page(surface=surf, page_size = PAGE_SIZE, margin=MARGIN)
    # **
    page_in_transition = True
    page_transition_pos = page_from_pos
    page_transition_state = ""
    # **
    running = True
    user_pressed_key = None
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            # === event handler ===
            #if event.type == pygame.QUIT:
            #    running = False
            #    break
            if event.type == KEYDOWN:
                if (event.key == K_ESCAPE):
                    events = pygame.event.get()
                    user_pressed_key = event
                    running = False
                    break;
                else:
                    user_pressed_key = event.unicode
                    running = False
                    break;
        # === show content
        surf.fill(BACKGROUND_COLOR)
        if page_in_transition:
            page_transition_state = page[0:page_transition_pos + 1]
            x,y = word_wrap(surf, page_transition_state, None, font, TEXT_COLOR)
            if page_transition_pos == len(page): # transition finished
                page_in_transition = False
            #if time.time() % 1 > 0.2: # speed of transition progress
            #    page_transition_pos += 1
            page_transition_pos += 1
        else:
            x,y = word_wrap(surf, page, None, font, TEXT_COLOR)
            if not wait_for_keypress:
                running = False
        cursor_pos = page_transition_pos + 1
        # === cursor positioning
        font.origin = True
        line_spacing = font.get_sized_height() + 2
        space = font.get_rect(' ')
        cursor_width = space.width
        cursor_height_percentage = 100
        cursor_height = (line_spacing / 100) * 80
        if SHOW_CURSOR:
            if page_in_transition:
                x,y = word_wrap(surf=surf, text=page_transition_state, stop_pos=cursor_pos, font = font, color=TEXT_COLOR, render=False)
            else:
                x,y = word_wrap(surf=surf, text=page, stop_pos=cursor_pos, font = font, color=TEXT_COLOR, render=False)
            if x > MARGIN[1]:
                cursor = Rect((x, y - cursor_height), (cursor_width, cursor_height)) # left, top, width, height
            else:
                cursor = Rect((x,y - cursor_height), (cursor_width, cursor_height)) # left, top, width, height
            if time.time() % 1 > 0.5: # blinking
                pygame.draw.rect(surf, CURSOR_COLOR, cursor)
                # --- TODO save a gif-animation for docs
                if not page_in_transition:
                    pygame.image.save(surf,'/tmp/screenshot_xsay.png') # save screenshot
                # ---
        clock.tick(30)
        pygame.display.update()
    return user_pressed_key


def main():
    msg = 'Do you want to play a game?'
    if len(sys.argv) > 1:
        msg = sys.argv[1]
    else:
        uinp = input("what should i say (default={}): ".format(msg))
        if uinp:
            msg = uinp
    page = msg
    surf = _init_screen(fullscreen=FULLSCREEN)
    t1 = ThreadWithReturnValue(target=show_message,args=(surf,msg,))
    t2 = threading.Thread(target=say,args=(msg,'espeak'))
    t1.start()
    #time.sleep(0.5)
    t2.start()
    res = t1.join()
    t2.join()
    if res in ['y','Y','j','J']:
        reply='splendid! let us play dude!'
        page_from_pos = len(msg)
        msg += res + "\n" + reply
        t1 = ThreadWithReturnValue(target=show_message,args=(surf,msg,page_from_pos,True,False))
        t2 = threading.Thread(target=say,args=(reply,'espeak'))
        t1.start()
        t2.start()
        res = t1.join()
        t2.join()
        pygame.quit()
        subprocess.run(['./run_mt_bt.sh'])
    else:
        reply = "okidoki, maybe another time?"
        page_from_pos = len(msg)
        msg += res + "\n" + reply[:-1] + "."
        t1 = ThreadWithReturnValue(target=show_message,args=(surf,msg,page_from_pos,True,False))
        t2 = threading.Thread(target=say,args=(reply,'espeak'))
        t1.start()
        t2.start()
        res = t1.join()
        t2.join()
        pygame.quit()

if __name__ == '__main__':
    s = time.perf_counter()
    main()
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")

