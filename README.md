# say - lightweight tts for shell & scripts

`say` makes 

  * 90s retro style (espeak, festival, pico)
  * modern (google speech api)

text-to-speech (tts) accessible to your favorite shell 
and is easy to use from within scripts.


installation
============

To clone the latest code-repository to the current working directory of 
your (debian-/ubuntu-linux-) machine and to run the examples
either copy'n'paste the following into your terminal

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

or do

```console
$ wget -O - https://raw.githubusercontent.com/s3h10r/say/master/install.sh | bash
```


usage 
=====

command line
------------

```console
$ echo "Have fun!" | ./say.py
``` 

```console
$ echo "Hi! It's $(date +%A) in week $(date +%U) of year $(date +%Y)" | ./say.py
``` 

```console
$ ./ask.py "Do you want to play a game?" && echo "splendid! (:"                  
```

```console
$ ./ask.py "do you want to play a game?" --yes="splendid!" --no="okidoki. maybe another time." --engine="google"
```


<!--
```
# -- **TODO** args/docopts

$ echo "Look Dave, I can see you're really upset about this." | ./say --engine=espeak --scrolling=True --fps=25
```
btw. a graphical version (experimental):

```console
$ ./xsay.py "This is because we can. Have fun!""
```
-->

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

```console
$ ./ask --help
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
```

```console
$ pydoc ./say.py

Help on module say:

NAME
    say

FILE
    /home/s3h10r/development/say/say.py

DESCRIPTION
    lightweight tts for shell and scripts
    -------------------------------------
    
    `say` makes
    
      * 90s retro style (espeak, festival, pico)
      * modern (google speech api)
    
    text-to-speech (tts) accessible to your favorite shell
    and is easy to use from within scripts.

FUNCTIONS
    available_engines()
    
    say(msg=None, engine='espeak')
    
    version()

DATA
    AUDIO_PLAYER_BIN = 'mplayer'
    DELETE_AUDIO_FILES = True
    ENABLE_TTS_ONLINE = True
    ENGINE_DEFAULT = 'espeak'
    __version__ = '0.1.2'
    formatter = <logging.Formatter object>
    handler = <logging.StreamHandler object>
    logger = <logging.Logger object>

VERSION
    0.1.2
```

