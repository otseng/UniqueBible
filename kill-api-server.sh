PROCESS=`ps -ef | grep api-server |  grep -v grep | awk '{print $2}'`
if [ "$PROCESS" != "" ]; then
  echo $PROCESS | xargs kill
fi
ps -ef | grep api-server 
