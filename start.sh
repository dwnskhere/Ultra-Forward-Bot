#!/usr/bin/env sh
set -eu

# Heroku builds the repository into the image. Never clone a different
# repository/branch at runtime: doing so bypasses the reviewed release.
exec python3 main.py
