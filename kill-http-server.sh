PROCESS=`ps -ef | grep http-server |  grep -v grep | awk '{print $2}'`
echo $PROCESS
if [ "$PROCESS" != "" ]; then
  echo $PROCESS | xargs kill
fi
ps -ef | grep http-server 
