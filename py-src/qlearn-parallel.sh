while :
do
    ./venv/bin/python q.py 2 6  ../qmaps/nn/q
    
    wait

    sleep 10
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


#echo "All tasks complete!"

