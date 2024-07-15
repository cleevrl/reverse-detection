#!/bin/bash
killall -9 python
killall -9 yolo
source /home/kw/projects/venv/bin/activate
python main.py &
python read.py &
python smr.py
