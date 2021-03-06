#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
converts given text/phrase to speech (tts). supports different tts-engines.

Usage:
say [<msg>] [--engine=<tts-engine>]

Options:
    --engine=<str> TTS-engine to use {'google', 'espeak', 'festival'}
                   [default: espeak]
    -h, --help     Print this
    --version      Print version

Examples:
    $ say "Hello world!" --engine espeak
    $ say "Look Dave, I can see you're really upset about this." --engine espeak
    $ say "This tts-engine sounds more human but requires to be online." --engine google
"""
import logging
import os
import sys
import subprocess
import tempfile
from docopt import docopt

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()  # console-handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

__version__ = (0,1,25)
_VERBOSITY  = 0
_ENGINES    = ['festival', 'espeak', 'dummy']
ENGINE_DEFAULT=_ENGINES[1]
ENABLE_TTS_ONLINE=True # because we can ;)
if ENABLE_TTS_ONLINE:
    try:
        from gtts import gTTS
        _gTTS = True
    except ImportError:
        _gTTS = False
    if _gTTS:
        _ENGINES.append('google')
        ENGINE_DEFAULT='google'
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1' # no "Hello from the pygame community..." on stdout.
    try:
        import pygame
    except ImportError:
        pygame=False
AUDIO_PLAYER_BIN='ffplay -nodisp -autoexit'
DELETE_AUDIO_FILES=True

def _check_engines(engines, ignore=['google']):
    """
    checks environment for available tts-binaries.
    returns the available ones for being able to adjusts _ENGINES suiting
    to that.
    """
    for e in engines:
        if e in ignore:
            continue
        rc = os.system('which {} 2>&1 > /dev/null'.format(e))
        if rc != 0:
            logger.debug("tts-engine '{}' not available. removing from candidates.".format(e))
            engines.remove(e)
    return engines
_ENGINES = _check_engines(_ENGINES)

def _check_requirements():
    crit = 0
    warn = 0
    info = 0
    if not len(_ENGINES) > 0:
        logger.critical('no tts-engines available. please install at leat one. (under debian you can use `sudo apt-get install espeak` for example')
        crit += 1
    logger.debug('available engines: {}'.format(_ENGINES))
    rc = os.system('which {} 2>&1 > /dev/null'.format(AUDIO_PLAYER_BIN.split()[0]))
    if rc != 0:
        logger.warning("AUDIO_PLAYER_BIN='{}' not available. it may be not possible to use TTS-APIs!".format(AUDIO_PLAYER_BIN))
        warn += 1
    if not pygame:
        logger.info('pygame not available. it may be not possible to use TTS-APIs!')
        info += 1
    if crit > 0:
        return False
    return True
_check_requirements()


def available_engines():
    return _ENGINES


def version():
    """
    """
    return __version__


def _play_audio(file, audio_player=AUDIO_PLAYER_BIN):
    assert(isinstance(file,str))
    assert(isinstance(audio_player,str) and len(audio_player.strip()) > 0)
    if audio_player:
        logger.debug("_play_audio '{}' with {}".format(file, audio_player))
        cmd = '{} {}'.format(audio_player,file)
        #subprocess.call(['{}'.format(cmd)], shell=True)
        proc = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = proc.communicate()
        rc = proc.wait()
        if rc == 0:
            return True
        else:
            logger.critical("playing audio file '{}' failed.".format(file))
            return False
    elif pygame:
        logger.debug("_play_audio '{}' with pygame".format(file))
        pygame.mixer.init()
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        return True
    else:
        logger.critical("no audio player available.")
        return False


def say(msg, engine=ENGINE_DEFAULT):
    """
    """
    assert(isinstance(msg,str))
    fn_audio, tts_cmd = None, None
    if engine not in _ENGINES:
        raise Exception("sorry, engine '{}' not available.".format(engine))
    if engine == 'festival':
        tts_cmd = 'echo "{}" | festival --tts'.format(msg)
    elif engine == 'espeak':
        tts_cmd = 'espeak "{}"'.format(msg)
    elif engine == 'google' or engine == 'google_online':
        tts = gTTS(msg, lang='en')
        suf = '.mp3'
        fn_audio = os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names()) + suf)
        logger.debug("...saving tts-result into '{}'".format(fn_audio))
        tts.save(fn_audio)
    if not fn_audio:
        if tts_cmd:
            subprocess.call(['{}'.format(tts_cmd)], shell=True)
        else:
            raise Exception("whooops. Sry, no tts_cmd for engine='{}'".format(engine))
    else:
        _play_audio(fn_audio)
        if DELETE_AUDIO_FILES: os.remove(fn_audio)

if __name__ == '__main__':
    if not _check_requirements():
        logger.critical('_check_requirements() failed.')
        sys.exit(-1)
    kwargs = docopt(__doc__, version=str('.'.join([str(el) for el in __version__])))
    logger.debug("kwargs={}".format(kwargs))
    if '<msg>' in kwargs:
        msg = kwargs['<msg>']
    engine = kwargs['--engine']
    if not engine in available_engines():
        logger.info("requested --engine='{}' not available. using engine '{}' instead".format(engine,ENGINE_DEFAULT))
        engine=ENGINE_DEFAULT
    if not msg:
        if _VERBOSITY > 0:
            msg = input("what should i say? : ")
        else:
            msg = input()
    say(msg,engine)
