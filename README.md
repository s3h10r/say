say - lightweight tts for shell & scripts
=========================================

`say` makes text-to-speech (tts) accessible to your favorite shell 
and is easy to use from within scripts. 
it provides commands which can be used in shellscripts and exports
functions wich are usable in python.

the tts-engines are:

  * 90s retro style (espeak, festival, pico)
  * modern (google speech api)

`say` works fine on RaspberryPis (Raspbian-/Debian-/Linux).


installation
============

To install the latest version into the current working directory of 
your (debian-/linux) machine do:

```console
$ wget -O - https://raw.githubusercontent.com/s3h10r/say/master/install.sh | bash
```
Assuming you have `git` and `wget` already installed
this clones the code-repository, installs the dependencies and runs
some basic examples.

Otherwise if you prefer doing things manually or want to be on the safe side
you can also copy'n'paste the following into your terminal:

```bash
#!/bin/bash

# -- 1. installation 

git clone https://github.com/s3h10r/say
if [ "$EUID" -eq 0 ] 
then
    grep -vE '^#' requirements.apt | xargs sudo apt install -y
else
  echo "no root-privileges - skipping apt-package-installation."
fi

cd say 
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# -- 2. doing a quick test 

echo "don't panic!" | ./say

# -- 3. listening to available / supported tts-engines on your system 

./say-example.py
```

usage 
=====

command line
------------

```console
$ echo "Have fun!" | ./say.py
``` 

```console
$ echo "Hi! It's $(date +%A) in week $(date +%U) of year $(date +%Y)" | ./say.py --engine google
``` 

```console
$ ./ask.py "Do you want to play a game?" && echo "splendid! (:"
```

```console
$ ./ask.py "do you want to play a game?" --yes="splendid!" --no="okidoki. maybe another time." --engine="google"
```

```console
# -- **experimental** a graphical version (xask)

$ ./example-yesno.sh
```


python
------

```
#!/usr/bin/env python3
import random
from string import Template
from say import available_engines, say

print(available_engines())
msg_tpl = Template("Hi! I am tts-engine $engine, \
                    nice to meet you. Have fun!")

for engine in available_engines():
    say(msg_tpl.substitute({'engine': engine}), engine=engine)

engines = available_engines()
for word in msg_tpl.substitute({'engine': 'crazy'}).split():
    say(word, engines[random.randint(0, len(engines)-1)])
```


help
====

```
$ pydoc3 say.py

Help on module say:

NAME
    say - converts given text/phrase to speech (tts). supports different tts-engines.

DESCRIPTION
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

FUNCTIONS
    available_engines()
    
    say(msg, engine='espeak')
    
    version()

DATA
    AUDIO_PLAYER_BIN = 'ffplay -nodisp -autoexit'
    DELETE_AUDIO_FILES = True
    ENABLE_TTS_ONLINE = True
    ENGINE_DEFAULT = 'espeak'
    formatter = <logging.Formatter object>
    handler = <StreamHandler <stderr> (NOTSET)>
    logger = <Logger say (INFO)>

VERSION
    (0, 1, 24)

FILE
    /home/s3h10r/development/say/say.py
```


```console
$ say --help

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
```

```console
$ ask --help

asks a yes/no question via audio (text-to-speech).
returncode reflects answer in common unix-style (0 == yes/ok, 1 == nope)

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
    $ ask "Do you want to play a game?" && echo "Splendid! :)"
    $ ask "Do you want to play a game?" --yes="Splendid, let's play!" --no="Okidoki. Maybe another time."
```

```console
$ xask --help

**experimental** a graphical retro-style version of `ask` - because we can. :D

asks a yes/no question via audio (text-to-speech).
returncode reflects answer in common unix-style (0 == yes/ok, 1 == nope)

Usage:
xask [<msg>] [--yes=<reply_yes>] [--no=<reply_no>] [--engine=<tts-engine>]
     [--yes-exec=<yes-exec>] [--no-exec=<no-exec>]

Options:
    --engine=<str>   TTS-engine to use {'google', 'espeak', 'festival'}
                     [default: espeak]
    --no=<str>       Message for negative answer
    --no-exec=<str>  execute given command by negative answer
    --yes=<str>      Message for positive answer
    --yes-exec=<str> execute given command by positive answer

    -h, --help       Print this
    --version        Print version

Examples:
    $ xask "Do you want to play a game?" && echo "Splendid! :)"
    $ xask "Do you want to play a game?" --yes="Splendid, let's play!" --no="Okidoki. Maybe another time."
    $ xask "Reboot universe?" --yes="rebooting now." --yes-exec "init 6" --no="Ok. Maybe another time."
```

