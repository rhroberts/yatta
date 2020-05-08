#!/bin/bash
#
# Usage: timesheet [TASKNAME] [TAGS] [DESCRIPTION]
#   - Tags should be separated with forward slashes, but this is not enforced
#
# Example:
#   timesheet github#135 work/wdft/groundwater

source $HOME/.yattarc

declare -i ELAPSED
declare -i HOUR
declare -i MIN
declare -i SEC

export TASK="${1,,}"  # convert to lower case

# check if a task was given, exit if not
if [ -z "$1" ]
then
    echo "No task was specified!"
    exit 1
fi

export TAGS="${2,,}"
export TMP=$YATTA_DATA_DIR/.yatta.tmp  # from .yattarc
export TS_FILE=$YATTA_DATA_FILE
export DATE=$(date +%x)

export START_TIME=$(date +%X)
termdown -f larry3d -T $TASK --exec-cmd "echo '{0}' > $TMP"
export END_TIME=$(date +%X)

ELAPSED=$(tail -n 1 $TMP)
SEC=$ELAPSED%60
MIN=$ELAPSED/60
HOUR=$MIN/60

echo -e "\nSummary"
echo -e "\tTask: $TASK"
echo -e "\tTags: $TAGS"
echo -e "\tStart time: $START_TIME"
echo -e "\tEnd time: $END_TIME"
echo -e "\tElapsed: $HOUR hours(s) $MIN minute(s) $SEC second(s)"

echo "$DATE,$TASK,$TAGS,$START_TIME,$END_TIME,$ELAPSED" >> $TS_FILE
