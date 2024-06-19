#!/bin/bash

export PATH_REV="$PWD"
export PATH_VOICE="$PWD/voice"

echo "echo 'dongbuict0' | sudo -S chmod 777 /dev/ttyTHS1"

REV_RUN=$(ps -ef | grep reverse_app | grep -v 'grep')

if [ -z "${DISPLAY}" ]; then
    echo "***** Can not run Apps without display!!! *****"
else
    if [ -z "${REV_RUN}" ]; then    

        echo "***** No REV APP, Running App... *****"

        source venv/bin/activate

        cd kw
        python main.py &
        python read.py &

        cd ..
        python reverse_app.py

        exit

    else
        echo "***** REV APP is running... *****"
    fi
fi
