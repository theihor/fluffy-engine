while :
do
    ./venv/bin/python q.py 51 52 ../qmaps/51.pickle &
    ./venv/bin/python q.py 101 102 ../qmaps/101.pickle & 
    ./venv/bin/python q.py 150 151 ../qmaps/150.pickle 
    
    wait
    
    cp ../qmaps/51.pickle ../qmaps/51.backup
    cp ../qmaps/101.pickle ../qmaps/101.backup
    cp ../qmaps/150.pickle ../qmaps/150.backup

    sleep 300
    killall -9 ./venv/bin/python

    echo "All tasks complete!"
done

#./venv/bin/python q.py 1 33 ../qmaps/1.pickle &
#./venv/bin/python q.py 33 51 ../qmaps/2.pickle 
#
#wait
#
#cp ../qmaps/1.pickle ../qmaps/1.backup
#cp ../qmaps/2.pickle ../qmaps/2.backup


echo "All tasks complete!"

