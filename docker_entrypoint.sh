#!/bin/bash
set -e

# Migrate DB
./src/manage.py migrate

uwsgi --ini=uwsgi.ini