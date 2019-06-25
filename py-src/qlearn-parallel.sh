while :
do
    ./venv/bin/python q.py 1 33 ../qmaps/1.pickle &
    ./venv/bin/python q.py 33 51 ../qmaps/2.pickle 
    
    wait

    cp ../qmaps/1.pickle ../qmaps/1.backup
    cp ../qmaps/2.pickle ../qmaps/2.backup


    echo "All tasks complete!"
done
#./venv/bin/python q.py 1 60 ../qmaps/last_try1.pickle &
#./venv/bin/python q.py 61 100 ../qmaps/last_try2.pickle &
#
#wait
#
#./venv/bin/python q.py 130 160 ../qmaps/last_try1.pickle &
#./venv/bin/python q.py 161 190 ../qmaps/last_try2.pickle
#
#wait
#
#./venv/bin/python q.py 101 130 ../qmaps/last_try1.pickle
#./venv/bin/python q.py 190 221 ../qmaps/last_try2.pickle 

