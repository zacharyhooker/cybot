#!/bin/bash
_now=$(date +"%m_%d_%Y")
_file="$_now-fullmovies.out"
nohup python -u working.config.py >$_file &
