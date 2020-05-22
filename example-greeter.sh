#!/bin/bash
export PATH=${PATH}:$(dirname $0)
echo "Hi! It's $(date +%A) in week $(date +%U) of year $(date +%Y). I wish you a happy day! Live long and prosper! " | say --engine google
