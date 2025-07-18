#!/bin/sh

ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# This will exec the CMD from your Dockerfile, i.e. "python -u ./main.py"
exec "$@"