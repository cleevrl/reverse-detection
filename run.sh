#!/bin/bash

export PATH_REV="$PWD"
export PATH_VOICE="$PWD/voice"

#!/bin/bash
killall -9 python
killall -9 yolo
source venv/bin/activate

cd kw
python main.py &
python read.py &

cd ..
python reverse_app.py