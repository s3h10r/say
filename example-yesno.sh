#!/bin/bash
export PATH=${PATH}:$(dirname $0)

xask "Do you want to play a game?" --yes="Splendid, let's play!" --no="Okidoki. Maybe another time." --engine espeak
if [ $? -eq 0 ]
then
  echo "we got a YES"
else
  echo "we got a NOPE"
fi

#xask "Do you want to play a game?" --yes="Splendid, let's play!" --yes-exec='wall "we got a YES"'--no="Okidoki. Maybe another time." --no-exec='wall "we got a Nope"'
