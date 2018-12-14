#!/bin/bash

# Get's us uwsgi :P 
source ./venv/bin/activate

# uswsgi also sources the env
uwsgi --ini ./uwsgi-dev.ini $@