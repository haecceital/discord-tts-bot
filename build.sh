#!/usr/bin/env bash
set -o errexit

pip install uv && uv pip install -r uv.lock

curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz | tar -xJ --strip-components=1 -C .