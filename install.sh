#!/bin/bash
echo "-- 1. installation"
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

echo "-- 2. doing a quick test"
echo "Hi! Nice to meet you. I am the default-tts engine." | ./say

echo "-- 3. playing all available / supported tts-engines on your system"
cat say-example.py
./say-example.py
