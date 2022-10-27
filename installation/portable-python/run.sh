INSTALLDIR='/Volumes/UBA_MAC_M1'

DIR=`pwd`
if [[ "$DIR" == "$HOME" ]]
then
  DIR=$INSTALLDIR
fi
  
echo "Working dir: $DIR"

if [ -d $DIR/UniqueBible ]
then
  cd $DIR/UniqueBible
  ../3.10.8/bin/python uba.py
  echo "Starting UBA..."
else
  echo "Could not find $DIR/UniqueBible"
fi
