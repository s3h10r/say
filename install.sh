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

echo "if you can't hear this something is wrong. don't panic!" | ./say

# -- 3. listening to available / supported tts-engines on your system

./say-example.py
