#!/bin/bash -x
BASE_URL="https://opendata.dwd.de/weather/nwp/"
WHAT_WE_WANT="icon/grib/00/(t_2m|pmsl)/.*_0[0-7][0-9]_.*"
LOCAL_DATA_DIR="/tmp"
CONTENT_LOG="content.log"
CONTENT_LOG_BZ2="$CONTENT_LOG.bz2"
CONTENT_LOG_OLD="$CONTENT_LOG.old"
TMP_BASE="fetchOpenData"
TODO_LIST="$TMP_BASE.todo"
LOCK_FILE="$TMP_BASE.lock"

WGET="/usr/bin/wget"
BUNZIP2="/usr/bin/bunzip2"

if [ -f $LOCAL_DATA_DIR/$LOCK_FILE ]
then
   echo "Script already running!"
   exit 1
fi

# Handle signals
trap 'exithandler' 0 1 2 15
exithandler() {
   rm -f $LOCAL_DATA_DIR/$LOCK_FILE $LOCAL_DATA_DIR/$TODO_LIST $LOCAL_DATA_DIR/$CONTENT_LOG
}

echo "$$" > $LOCAL_DATA_DIR/$LOCK_FILE
$WGET -q -O - ${BASE_URL}${CONTENT_LOG_BZ2} | $BUNZIP2 | egrep -v $CONTENT_LOG_BZ2 | sort > $LOCAL_DATA_DIR/$CONTENT_LOG

if [ ! -f $LOCAL_DATA_DIR/$CONTENT_LOG ]
then
   echo "Download failed"
   exit 1
fi

if [ -f $LOCAL_DATA_DIR/$CONTENT_LOG_OLD ]
then
   diff $LOCAL_DATA_DIR/$CONTENT_LOG $LOCAL_DATA_DIR/$CONTENT_LOG_OLD | egrep "<" | sed s/\<\ .// | cut -f 1 -d "|" | egrep $WHAT_WE_WANT | sed "s,^\/,$BASE_URL," > $LOCAL_DATA_DIR/$TODO_LIST
else
   cat $LOCAL_DATA_DIR/$CONTENT_LOG | cut -f 1 -d "|" | egrep $WHAT_WE_WANT | sed "s,^.\/,$BASE_URL," > $LOCAL_DATA_DIR/$TODO_LIST
fi

if [ -s $LOCAL_DATA_DIR/$TODO_LIST ]
then
   $WGET -nd -q -np -i $LOCAL_DATA_DIR/$TODO_LIST
fi

mv $LOCAL_DATA_DIR/$CONTENT_LOG $LOCAL_DATA_DIR/$CONTENT_LOG_OLD

exit 0
