#!/bin/bash

export PATH_REV="$PWD"
export PATH_VOICE="$PWD/voice"

source venv/bin/activate

cd kw
python main.py &
python read.py &

cd ..
python reverse_app.py

exit