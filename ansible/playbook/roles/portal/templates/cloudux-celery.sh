#!/bin/bash 

case "$1" in
    start)
        /usr/bin/celery --workdir={{basedir}} -A cloudmgmt worker -B -l info &
    ;;
    stop)
        PIDS=`ps -ef | grep "celery -A cloudmgmt worker" | grep -v grep | awk '{print $2}'`
        for PID in $PIDS
        do
            kill $PID
        done
    ;;
    *)
        echo "Usage {start|stop}"
    exit 1
    ;;
esac
exit 0