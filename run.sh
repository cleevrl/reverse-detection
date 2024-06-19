#!/bin/bash

export PATH_REV="$PWD"
export PATH_VOICE="$PWD/voice"

echo 'dongbuict0' | sudo -S chmod 777 /dev/ttyTHS1

REV_RUN=$(ps -ef | grep reverse_app | grep -v 'grep')

if [ -z "${DISPLAY}" ]; then
    echo "***** Can not run Apps without display!!! *****"
else
    if [ -z "${REV_RUN}" ]; then    

        echo "***** No REV APP, Running App after 3 secs... *****"
        
        sleep 3

        source venv/bin/activate

        cd kw
        python main.py 1>>/dev/null 2>>/dev/null &

        echo "Run main.py ----->"
        sleep 5        

        python read.py 1>>/dev/null 2>>/dev/null &
        echo "Run read.py ----->"

        cd ..
        python reverse_app.py

        exit

    else
        echo "***** REV APP is running... *****"
    fi
fi
