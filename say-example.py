#!/usr/bin/env python3
import random
from string import Template
from say import available_engines, say

msg = 'Look Dave, I can see you\'re really upset about this.'
msg_tpl = Template("Hi! I am tts-engine $engine, \
                    nice to meet you. Have fun!")
for engine in available_engines():
    print("using engine: '{}'".format(engine))
    say(msg_tpl.substitute({'engine': engine}), engine)
    say(msg, engine)

engines = available_engines()
if 'google' in engines:
    engines.remove('google')
for word in (msg_tpl.substitute({'engine': 'crazy'}) + " " + msg).split():
    print(word)
    say(word, engines[random.randint(0, len(engines)-1)])
