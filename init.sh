#!/bin/bash

echo "dongbuict0" | sudo -S apt-get update
sudo apt-get install -y python3-pip python.3.10-venv
sudo apt-get install -y cuda-toolkit-12-2
sudo apt-get install -y python3-libnvinfer*
sudo apt-get install -y pavucontrol
sudo apt-get install -y libxcb-cursor-dev

sudo -H pip install -U jetson-stats

sudo dpkg -i install/nomachine_8.11.3_3_arm64.deb

wget https://nvidia.box.com/shared/static/mp164asf3sceb570wvjsrezk1p4ftj8t.whl -O installer/torch-2.3.0-cp310-cp310-linux_aarch64.whl
wget https://nvidia.box.com/shared/static/xpr06qe6ql3l6rj22cu3c45tz1wzi36p.whl -O installer/torchvision-0.18.0a0+6043bc2-cp310-cp310-linux_aarch64.whl

python -m venv --system-site-packages venv

source venv/bin/activate

pip install haversine ultralytics flask imutils sysv_ipc PySide6 pyserial pyyaml pygame

pip install installer/torch-2.3.0-cp310-cp310-linux_aarch64.whl
pip install installer/torchvision-0.18.0a0+6043bc2-cp310-cp310-linux_aarch64.whl

mv venv/lib/python3.10/site-packages/ultralytics/engine/results.py venv/lib/python3.10/site-packages/ultralytics/engine/_results.py
cp installer/kw_results.py venv/lib/python3.10/site-packages/ultralytics/engine/results.py

echo "source reverse-detection/run.sh" >> ~/.bashrc