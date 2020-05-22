#!/bin/bash
export PATH=${PATH}:$(dirname $0)
msg=$(haiku.py | tr -s '\n' ' ')
echo $msg
echo $msg | say --engine google
